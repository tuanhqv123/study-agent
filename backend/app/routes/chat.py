from flask import Blueprint, request, jsonify
from ..services.ai_service import AiService, LMSTUDIO_URL, HEADERS
from ..services.query_classifier import QueryClassifier
from ..services.schedule_service import ScheduleService
from ..services.exam_schedule_service import ExamScheduleService
from ..services.ptit_auth_service import PTITAuthService
from ..utils.logger import Logger
from ..lib.supabase import supabase
import time
from datetime import datetime, timedelta
import json
from ..config.agents import get_agent, get_all_agents
from collections import Counter
import httpx
from flask import Response
from ..services.lmstudio_service import parse_time_lmstudio
from ..services.file_service import FileService
import threading
import asyncio
import pytz

chat_bp = Blueprint('chat', __name__)
ai_service = AiService()
logger = Logger()
query_classifier = QueryClassifier()
schedule_service = ScheduleService()
exam_schedule_service = ExamScheduleService()
ptit_auth_service = PTITAuthService()

# Initialize services with auth service and AI service
schedule_service.set_auth_service(ptit_auth_service)
schedule_service.set_ai_service(ai_service)
exam_schedule_service.set_auth_service(ptit_auth_service)
# Set the schedule_service in the exam_schedule_service for date extraction
exam_schedule_service.set_schedule_service(schedule_service)

@chat_bp.route('/agents', methods=['GET'])
def get_agents():
    """
    Get the list of available agents.
    
    Returns:
        JSON response with list of available agents.
    """
    agents = get_all_agents()
    return jsonify({'agents': agents})

@chat_bp.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.json
        file_ids = data.get('file_ids', [])  # Expect array of file IDs
        file_id = data.get('file_id')  # Keep backward compatibility
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        chat_id = data.get('chat_id')
        agent_id = data.get('agent_id')
        web_search_enabled = data.get('web_search_enabled', False)
        space_id = data.get('space_id')
        
        # Log agent selection
        if agent_id:
            agent = get_agent(agent_id)
            logger.log_with_timestamp(
                "AGENT SELECTION",
                f"Using agent: {agent['display_name']}",
                f"Model: {agent['model']}"
            )
        
        # Classify query but don't exit early - let AI handle all categories
        classification = query_classifier.classify_query(message)
        # Log classification result
        logger.log_with_timestamp(
            "CLASSIFICATION", 
            f"Category: {classification.get('category')}",
            f"Method: {classification.get('method')}"
        )
        # Note: Removed early exit for 'other' category - let AI respond naturally
        
        # Prepare user query and no_thinking flag
        flag = ""
        clean_message = message
        if clean_message.strip().endswith("/no_thinking"):
            clean_message = clean_message.strip()[:-len("/no_thinking")].strip()
            flag = "/no_thinking"
        # Build unified user prompt: start with clean user query
        user_content = clean_message
        
        # Add space prompt if we're in a space context
        space_prompt = ""
        if space_id:
            try:
                space_result = supabase.table('spaces').select('prompt').eq('id', space_id).single().execute()
                if space_result and hasattr(space_result, 'data') and space_result.data:
                    space_prompt = space_result.data.get('prompt', '')
                    if space_prompt:
                        user_content = f"{space_prompt}\n\nUser message: {clean_message}"
                        logger.log_with_timestamp(
                            "SPACE_PROMPT",
                            f"Applied space prompt for space {space_id}",
                            f"Prompt length: {len(space_prompt)}"
                        )
            except Exception as e:
                logger.log_with_timestamp('SPACE_PROMPT_ERROR', f'Error fetching space prompt: {str(e)}')
        
        # File context - handle both single file (backward compatibility) and multiple files
        all_file_chunks = []
        processed_files = []
        
        # Handle backward compatibility with single file_id
        if file_id:
            file_ids = [file_id]
        
        # Get space files if we're in a space context
        space_file_ids = []
        if space_id:
            try:
                space_files = supabase.table('user_files').select('id').eq('space_id', space_id).eq('status', 'ready').execute()
                if space_files.data:
                    space_file_ids = [f['id'] for f in space_files.data]
                    logger.log_with_timestamp(
                        "SPACE_FILES", 
                        f"Found {len(space_file_ids)} files in space {space_id}"
                    )
            except Exception as e:
                logger.log_with_timestamp('SPACE_FILES_ERROR', f'Error fetching space files: {str(e)}')
        
        # Combine chat-specific files with space files
        all_file_ids = []
        if file_ids:
            all_file_ids.extend(file_ids)
        if space_file_ids:
            all_file_ids.extend(space_file_ids)
        
        if all_file_ids:
            file_service = FileService()
            for current_file_id in all_file_ids:
                chunks = file_service.search_relevant_chunks_in_supabase(message, current_file_id)
                if chunks:
                    all_file_chunks.extend(chunks)
                    processed_files.append(current_file_id)
                    
            # Log file chunks count and sample
            logger.log_with_timestamp(
                "FILE_CHUNKS",
                f"Found {len(all_file_chunks)} chunks across {len(processed_files)} files (chat: {len(file_ids or [])}, space: {len(space_file_ids)})",
                str(all_file_chunks[:3])
            )
            
            if all_file_chunks:
                user_content += "\n\nRelevant file excerpts:\n" + "\n\n---\n\n".join(all_file_chunks)
            else:
                user_content += "\n\n[FILE_QUERY] Không tìm thấy đoạn văn phù hợp trong các file đã tải lên."
        # Web search context with LLM query optimization
        if web_search_enabled:
            agent_cfg = get_agent(agent_id)
            search_data = await ai_service.web_search_service.search_with_optimization(
                message, agent_cfg['model'], chat_id, save_to_db=True
            )
            web_results = search_data['results']
            optimized_query = search_data['optimized_query']
            
            # Log the query optimization result
            if search_data['original_query'] != optimized_query:
                logger.log_with_timestamp(
                    'WEB_SEARCH_OPTIMIZATION', 
                    f'Query optimized: "{search_data["original_query"]}" -> "{optimized_query}"'
                )
            
            if web_results:
                # Hiển thị kết quả web search với format rõ ràng hơn, bao gồm nội dung đã scrape
                formatted_results = []
                for i, r in enumerate(web_results):
                    result_text = f"### {i+1}. {r['title']}\n\n{r['snippet']}"
                    # Thêm nội dung đã scrape nếu có
                    if 'scraped_content' in r and r['scraped_content']:
                        result_text += f"\n\n**Nội dung từ trang web**:\n{r['scraped_content']}"
                    formatted_results.append(result_text)
                
                formatted = "\n\n".join(formatted_results)
                user_content += f"\n\n## Web search results\n**Query used**: '{optimized_query}'\n\n" + formatted
        # Schedule context (only parse time for schedule/date_query)
        if classification.get('category') in ('schedule','date_query'):
            # Add current time information for schedule queries with XML tags
            current_time = get_vietnam_current_time()
            user_content += f"\n\n<current_time>\n"
            user_content += f"<today_info>\n"
            user_content += f"Hôm nay là {current_time['weekday']}, ngày {current_time['date']}\n"
            user_content += f"Giờ hiện tại: {current_time['time']}\n"
            user_content += f"</today_info>\n"
            user_content += f"</current_time>\n"
            
            time_info = parse_time_lmstudio(message)
            # Log time parsing result
            logger.log_with_timestamp(
                "TIME_PARSER",
                f"Type: {time_info.get('type')}",
                f"Value: {time_info.get('value')}"
            )
            creds = data.get('university_credentials')
            if creds:
                success, err = ptit_auth_service.login(
                    creds['university_username'], creds['university_password']
                )
            current_sem = None
            try:
                current_sem, _ = ptit_auth_service.get_current_semester()
            except:
                pass
            if current_sem:
                # Use pre-parsed time_info directly
                sched = await schedule_service.process_schedule_query(
                    time_info, current_sem.get('hoc_ky')
                )
                sched_text = sched.get('schedule_text', '') if isinstance(sched, dict) else str(sched)
                user_content += "\n<class_schedule>\n"
                user_content += f"<query_type>{time_info.get('type', 'unknown')}</query_type>\n"
                user_content += f"<query_value>{time_info.get('value', 'unknown')}</query_value>\n"
                user_content += f"<schedule_data>\n{sched_text}\n</schedule_data>\n"
                user_content += "</class_schedule>"

        # Exam context: date_query should fetch filtered exams, examschedule fetch full schedule
        if classification.get('category') in ('date_query','examschedule'):
            # Add current time information for exam schedule queries with XML tags
            current_time = get_vietnam_current_time()
            user_content += f"\n\n<current_time>\n"
            user_content += f"<today_info>\n"
            user_content += f"Hôm nay là {current_time['weekday']}, ngày {current_time['date']}\n"
            user_content += f"Giờ hiện tại: {current_time['time']}\n"
            user_content += f"</today_info>\n"
            user_content += f"</current_time>\n"
            
            creds = data.get('university_credentials')
            if creds:
                success, err = ptit_auth_service.login(
                    creds['university_username'], creds['university_password']
                )
            current_sem = None
            try:
                current_sem, _ = ptit_auth_service.get_current_semester()
            except:
                pass
            if current_sem:
                if classification.get('category') == 'date_query':
                    # Filtered exams for specific date
                    exams_list, exam_txt, _ = await exam_schedule_service.get_exams_for_query(
                        message, current_sem.get('hoc_ky')
                    )
                    logger.log_with_timestamp(
                        "EXAM_API_DATA",
                        f"Filtered exams for date {time_info.get('value')}",
                        exam_txt[:200]
                    )
                    user_content += "\n<exam_schedule>\n"
                    user_content += f"<query_type>date_specific</query_type>\n"
                    user_content += f"<query_value>{time_info.get('value', 'unknown')}</query_value>\n"
                    user_content += f"<exam_count>{len(exams_list)}</exam_count>\n"
                    user_content += f"<exam_data>\n{exam_txt}\n</exam_data>\n"
                    user_content += "</exam_schedule>"
                else:
                    # Full exam schedule for all dates
                    data = await exam_schedule_service.get_exam_schedule_by_semester(
                        current_sem.get('hoc_ky'), False
                    )
                    all_exams = data.get('data', {}).get('ds_lich_thi', [])
                    # Format full exam list
                    full_exam_txt = exam_schedule_service.format_exam_schedule(all_exams)
                    # Log full exam schedule and append to user_content
                    logger.log_with_timestamp(
                        "EXAM_API_DATA",
                        f"Fetched full exam schedule for semester {current_sem.get('hoc_ky')}",
                        full_exam_txt[:200]
                    )
                    user_content += "\n<exam_schedule>\n"
                    user_content += f"<query_type>full_schedule</query_type>\n"
                    user_content += f"<exam_count>{len(all_exams)}</exam_count>\n"
                    user_content += f"<exam_data>\n{full_exam_txt}\n</exam_data>\n"
                    user_content += "</exam_schedule>"

        # Append no_thinking flag at the end if present
        if flag:
            user_content += " " + flag
        # Log final user content before sending to LM Studio
        logger.log_with_timestamp(
            "FINAL_USER_CONTENT",
            user_content[:500],
            f"Category: {classification.get('category')}"
        )

        # Prepare system prompt with category awareness and XML guidance
        category = classification.get('category', 'general')
        if category == 'other':
            system_content = (
                "You are a helpful AI assistant. While you primarily focus on educational topics, "
                "you can also provide polite, brief responses to non-educational questions when appropriate. "
                "If the question is clearly off-topic or inappropriate, you may politely redirect to educational topics. "
                "Answer based on context when provided, otherwise use your general knowledge appropriately."
            )
        elif category in ('schedule', 'date_query', 'examschedule'):
            system_content = (
                "<role>You are a dedicated study assistant for university students in Vietnam specializing in academic schedule and exam information.</role>\n\n"
                "<instructions>\n"
                "- Analyze the provided XML-structured data carefully and use ALL information available\n"
                "- Use ONLY the information provided in the <class_schedule>, <exam_schedule>, and <current_time> tags\n"
                "- ALWAYS provide COMPLETE and COMPREHENSIVE responses that include ALL details from the data\n"
                "- For schedule queries: Include ALL class details - subject name (both Vietnamese and English), time slots, room, instructor name with ID, credits, dates\n"
                "- For exam queries: Include ALL exam details - subject name, exam type, format, time, weekday, date, room, location\n"
                "- When user asks follow-up questions, refer to the conversation history to provide context and complete answers\n"
                "- Always reference the current time context when explaining relative dates (today, tomorrow, next week)\n"
                "- Use Vietnamese language naturally and professionally\n"
                "- Organize information logically with clear headings, bullet points, and structured formatting\n"
                "- Never provide partial information - if data is available, include it ALL\n"
                "- Do not add or fabricate any information not present in the provided XML data\n"
                "</instructions>\n\n"
                "<response_format>\n"
                "- NEVER start with summary, overview, or any introductory text\n"
                "- Begin immediately with the specific information requested\n"
                "- Do NOT use phrases like 'summary:', 'tóm tắt:', 'overview:', or similar introductory words\n"
                "- Present ALL information from the provided data in a clear, organized format\n"
                "- Use headers, lists, and bullet points to structure the complete information\n"
                "- Include every single detail available in the data - subject names, times, rooms, instructors, credits, etc.\n"
                "- Organize by date/time chronologically when showing multiple items\n"
                "- End with brief helpful context only if relevant\n"
                "- If user asks follow-up questions, check conversation history and provide complete context\n"
                "</response_format>"
            )
        else:
            system_content = (
                "You are a dedicated study assistant for university students in Vietnam. "
                "Provide clear, helpful answers based only on the provided context and focus strictly on the user's question. "
                "Do not add or fabricate any information not present in the context."
            )
            
        system_message = {
            'role': 'system',
            'content': system_content
        }
        
        # Build messages without conversation history - only system prompt and current user query
        messages = [system_message]
        
        # Add current user message with all context
        messages.append({'role':'user','content': user_content})
        
        # Log that we're not using conversation history
        logger.log_with_timestamp(
            "CONVERSATION_HISTORY",
            "Skipping conversation history - sending only system prompt and current query"
        )
        # Handle streaming response
        agent_cfg = get_agent(agent_id)
        payload = {
            'model': agent_cfg['model'],
            'messages': messages,
            'temperature': 0.2,
            'stream': True
        }
        # Log raw payload sent to LM Studio (full content)
        print(f"[{Logger.get_timestamp()}] LMSTUDIO_PAYLOAD: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # Save user message to database first
        if chat_id:
            try:
                # Save the original user message (before adding context/space prompt)
                original_user_message = clean_message
                await ai_service.web_search_service.save_message_with_sources(
                    chat_id, 'user', original_user_message, None
                )
                logger.log_with_timestamp('MESSAGE_SAVE', f'Saved original user message (without space prompt)')
            except Exception as e:
                logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Error saving user message: {str(e)}')
        
        # Store web search results for later saving
        web_search_sources = None
        if web_search_enabled and web_results:
            web_search_sources = web_results
        
        def generate():
            full_response = ""
            try:
                logger.log_with_timestamp('STREAMING', 'Starting LM Studio request...')
                with httpx.stream('POST', LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60) as r:
                    logger.log_with_timestamp('STREAMING', f'Response status: {r.status_code}')
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if not line: continue
                        d = line.decode('utf-8') if isinstance(line,(bytes,bytearray)) else line
                        if d.startswith('data: '):
                            part = d[len('data: '):]
                            if part.strip() == '[DONE]':
                                logger.log_with_timestamp('STREAMING', 'Received [DONE] signal')
                                break
                            try:
                                obj = json.loads(part)
                                delta = obj['choices'][0].get('delta',{})
                                text = delta.get('content')
                                if text: 
                                    full_response += text
                                    yield text
                            except Exception as e:
                                logger.log_with_timestamp('STREAMING_ERROR', f'Error parsing line: {str(e)}')
            except Exception as e:
                logger.log_with_timestamp('STREAMING_ERROR', f'Error during streaming: {str(e)}')
                yield f"data: Lỗi khi gọi AI: {str(e)}\n\n"
            
            # Save assistant message with sources after streaming is complete
            if chat_id and full_response:
                try:
                    # Create a background task to save the message
                    def save_message():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(
                                ai_service.web_search_service.save_message_with_sources(
                                    chat_id, 'assistant', full_response, web_search_sources
                                )
                            )
                            logger.log_with_timestamp('MESSAGE_SAVE', f'Saved assistant message with {len(web_search_sources) if web_search_sources else 0} sources')
                        except Exception as e:
                            logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Error saving assistant message: {str(e)}')
                        finally:
                            loop.close()
                    
                    # Run in background thread
                    thread = threading.Thread(target=save_message)
                    thread.start()
                except Exception as e:
                    logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Error starting save thread: {str(e)}')
        return Response(generate(), content_type='text/event-stream')
        
    except Exception as e:
        logger.log_with_timestamp('ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/messages', methods=['GET'])
async def get_chat_messages():
    """
    Endpoint to get messages for a specific chat session.
    This is useful for debugging and verifying that messages are properly saved.
    
    Query parameters:
        chat_id: UUID of the chat session
        
    Returns:
        JSON response with messages from the specified chat session
    """
    try:
        chat_id = request.args.get('chat_id')
        
        if not chat_id:
            return jsonify({'error': 'Missing chat_id parameter'}), 400
            
        logger.log_with_timestamp("GET_MESSAGES", f"Fetching messages for chat: {chat_id}")
        
        # Query the database for messages
        result = supabase.table('messages') \
                        .select('*') \
                        .eq('chat_id', chat_id) \
                        .order('created_at') \
                        .execute()
                        
        # Format and return messages
        messages = []
        if result and hasattr(result, 'data'):
            messages = result.data
            # Log what we found
            logger.log_with_timestamp("GET_MESSAGES", f"Found {len(messages)} messages")
            
            # Check for messages with sources
            messages_with_sources = [msg for msg in messages if msg.get('sources')]
            if messages_with_sources:
                logger.log_with_timestamp("SOURCES_FOUND", f"Found {len(messages_with_sources)} messages with sources")
            
        return jsonify({
            'chat_id': chat_id,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("ERROR", f"Error fetching messages: {error_message}")
        return jsonify({'error': error_message}), 500

@chat_bp.route('/api/messages/metrics/daily', methods=['GET'])
def messages_per_day():
    """
    Returns the number of messages per day for dashboard analytics.
    Accepts optional 'from' and 'to' query parameters (YYYY-MM-DD).
    """
    try:
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        query = supabase.table('messages').select('created_at')
        if from_date:
            query = query.gte('created_at', from_date)
        if to_date:
            # Add 1 day to include the 'to' date fully
            from datetime import datetime, timedelta
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.lt('created_at', to_date_obj.strftime("%Y-%m-%d"))
        res = query.execute()
        if not hasattr(res, 'data') or not res.data:
            return jsonify([])
        from collections import Counter
        date_counts = Counter()
        for msg in res.data:
            dt = msg.get('created_at')
            if dt:
                date_str = str(dt)[:10]  # 'YYYY-MM-DD'
                date_counts[date_str] += 1
        result = [
            {"date": date, "total": date_counts[date]}
            for date in sorted(date_counts.keys())
        ]
        return jsonify(result)
    except Exception as e:
        logger.log_with_timestamp('DASHBOARD_METRICS_ERROR', str(e))
        return jsonify([]), 500

def get_vietnam_current_time():
    """Get current date and time in Vietnam timezone"""
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vietnam_tz)
    
    # Vietnamese weekday names
    vietnamese_weekdays = {
        0: "Thứ Hai",    # Monday
        1: "Thứ Ba",     # Tuesday  
        2: "Thứ Tư",     # Wednesday
        3: "Thứ Năm",    # Thursday
        4: "Thứ Sáu",    # Friday
        5: "Thứ Bảy",    # Saturday
        6: "Chủ Nhật"    # Sunday
    }
    
    weekday_vn = vietnamese_weekdays[now.weekday()]
    date_str = now.strftime('%d/%m/%Y')
    time_str = now.strftime('%H:%M:%S')
    
    return {
        'date': date_str,
        'time': time_str,
        'weekday': weekday_vn,
        'datetime_obj': now
    }