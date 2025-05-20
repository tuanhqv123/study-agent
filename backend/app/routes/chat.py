from flask import Blueprint, request, jsonify
from ..services.ai_service import AiService
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
        file_id = data.get('file_id')  # handle file context
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        agent_id = data.get('agent_id')  # Get agent_id from request
        web_search_enabled = data.get('web_search_enabled', False)  # Get web search flag
        
        # Log which agent is being used
        if agent_id:
            agent = get_agent(agent_id)
            logger.log_with_timestamp(
                "AGENT SELECTION",
                f"Using agent: {agent['display_name']}",
                f"Model: {agent['model']}"
            )
        
        # Handle file context
        if file_id:
            # use file context handler
            response, updated_history = await ai_service.chat_with_file_context(
                message, file_id, conversation_history, agent_id
            )
            return jsonify({
                'response': response,
                'conversation_history': updated_history,
                'file_context_active': True,
                'file_id': file_id,
                'agent_id': agent_id
            })
        
        if not message:
            return jsonify({'error': 'No message provided', 'response': None}), 400

        # Log user message
        logger.log_with_timestamp("USER INPUT", message, f"Message length: {len(message)} chars")
        
        # Check if web search is enabled
        if web_search_enabled:
            logger.log_with_timestamp("WEB_SEARCH_ENABLED", "Using web search for query", "")
            
            # Lấy chat_id nếu có
            chat_id = data.get('chat_id')
            # Lấy lịch sử tin nhắn từ database nếu có chat_id
            db_history = []
            if chat_id:
                try:
                    result = supabase.table('messages') \
                        .select('*') \
                        .eq('chat_id', chat_id) \
                        .order('created_at') \
                        .execute()
                    if result and hasattr(result, 'data'):
                        db_history = result.data
                        # Chuyển đổi về format phù hợp cho AI (role/content)
                        db_history = [
                            {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                            for msg in db_history if msg.get("content")
                        ]
                except Exception as e:
                    logger.log_with_timestamp("DB_HISTORY_ERROR", f"Error fetching chat history: {e}")
            # Gộp lịch sử db với conversation_history từ frontend (nếu có)
            conversation_history = db_history + conversation_history
            
            # Log chat session info with more details
            if chat_id:
                logger.log_with_timestamp("CHAT_SESSION", f"Using chat session: {chat_id}")
            else:
                logger.log_with_timestamp("CHAT_SESSION_WARNING", "No chat_id provided, messages won't be saved to database", f"Request data keys: {list(data.keys())}")
                # Check all the data received to debug
                logger.log_with_timestamp("REQUEST_DATA", f"Request data: {json.dumps(data, default=str)[:500]}")
            
            # Call AI service with web search
            logger.log_with_timestamp("WEB_SEARCH_CALL", "Calling AI service with web search")
            web_response, updated_history = await ai_service.chat_with_web_search(
                message, conversation_history, agent_id, chat_id
            )
            
            # Log the response format for debugging
            logger.log_with_timestamp("WEB_SEARCH_RESPONSE", 
                                   f"Response type: {type(web_response)}, Keys: {list(web_response.keys()) if isinstance(web_response, dict) else 'Not a dict'}")
                                   
            # Log sources count and format
            if isinstance(web_response, dict) and 'sources' in web_response:
                sources = web_response.get('sources', [])
                logger.log_with_timestamp("WEB_SEARCH_SOURCES", 
                                       f"Returning {len(sources)} sources to frontend")
                if sources and len(sources) > 0:
                    logger.log_with_timestamp("FIRST_SOURCE_FORMAT", 
                                           f"First source format: {json.dumps(sources[0]) if sources else 'None'}")
            
            # Prepare response for frontend
            response_data = {
                'response': web_response['content'] if isinstance(web_response, dict) else web_response,
                'sources': web_response.get('sources', []) if isinstance(web_response, dict) else [],
                'web_search_results': True,
                'conversation_history': updated_history,
                'query_type': 'web_search',
                'agent_id': agent_id,
                'chat_id': chat_id  # Echo back the chat_id for client reference
            }
            
            logger.log_with_timestamp("WEB_SEARCH_COMPLETE", "Web search complete, returning response")
            return jsonify(response_data)
        
        # Regular flow continues if web search is not enabled
        # Use the QueryClassifier to classify the message
        classification_result = query_classifier.classify_query(message)

        # Handle UML/PlantUML diagram requests
        if classification_result.get('category') == 'uml':
            uml_prompt = {
                "role": "system",
                "content": (
                    "You are a professional programming assistant. When returning the UML diagram,"
                    "Always cover the Plantuml codes in the code block using the three -point sign and tag` plantuml`, "
                    "For example:` `` Plantuml ... `` `` Frontend can display images. "
                    "Without further explanation, only export the UML diagram."
                )
            }
            # Get response from AI - REMOVE await since chat_with_ai is not async
            response, updated_history = ai_service.chat_with_ai(
                message,
                [uml_prompt],
                agent_id
            )
            # Ensure PlantUML content is fenced for ReactMarkdown
            content = response.strip()
            if not (content.startswith('```') and content.endswith('```')):
                content = f"```plantuml\n{content}\n```"
            # Update response and history with fenced code
            response = content
            updated_history[-1]["content"] = content  # Update the last message which should be assistant
            return jsonify({
                'response': response,
                'conversation_history': updated_history,
                'query_type': 'uml',
                'agent_id': agent_id
            })
        
        # Log the classification result
        logger.log_with_timestamp(
            "CLASSIFICATION", 
            classification_result['category'].upper(),
            f"Confidence: {classification_result['confidence']:.2f} | Method: {classification_result['method']}"
        )
        
        # Handle non-academic topics immediately
        if classification_result['category'] == 'other':
            non_educational_response = (
                "Xin lỗi, tôi chỉ có thể hỗ trợ bạn với các câu hỏi liên quan đến học tập và giáo dục. "
                "Vui lòng đặt câu hỏi khác về chủ đề học tập."
            )
            logger.log_with_timestamp("STANDARD RESPONSE", non_educational_response, "Non-educational query detected")
            return jsonify({
                'response': non_educational_response,
                'conversation_history': conversation_history,
                'query_type': 'other',
                'agent_id': agent_id
            })
        
        # Khởi tạo exam_data để tránh lỗi referenced before assignment
        exam_data = None
        # Handle schedule-related queries with date extraction
        if classification_result['category'] == 'date_query' or classification_result['category'] == 'schedule':
            # Log that we're handling a schedule/date query
            logger.log_with_timestamp(
                "DATE QUERY", 
                f"Processing date query", 
                f"Query type: {classification_result['category']}"
            )
            try:
                # Get university credentials from request
                credentials = data.get('university_credentials')
                if not credentials:
                    raise Exception("Vui lòng cập nhật thông tin đăng nhập vào hệ thống trường học trong phần Thiết lập.")
                # Login to PTIT system
                success, error = ptit_auth_service.login(
                    credentials['university_username'],
                    credentials['university_password']
                )
                if not success:
                    raise Exception("Không thể đăng nhập vào hệ thống trường học. Vui lòng kiểm tra lại thông tin đăng nhập.")
                # Get current semester
                current_semester, semester_error = ptit_auth_service.get_current_semester()
                if semester_error:
                    raise Exception(f"Không thể lấy thông tin học kỳ: {semester_error}")
                # Process both class schedule and exam schedule for the same date
                schedule_result = await schedule_service.process_schedule_query(message, current_semester['hoc_ky'])
                # Nếu là date_query, luôn luôn lấy toàn bộ lịch thi học kỳ
                if classification_result['category'] == 'date_query':
                    filtered_exams, exam_text, exam_date_info = await exam_schedule_service.get_exams_for_query(message, current_semester['hoc_ky'])
                    exam_count = len(filtered_exams)
                else:
                    exam_result = await exam_schedule_service.process_exam_query(message, current_semester['hoc_ky'], False)
                    if isinstance(exam_result, list):
                        exam_text = exam_schedule_service.format_exam_schedule(exam_result)
                        exam_count = len(exam_result)
                    elif isinstance(exam_result, dict):
                        exam_text = exam_result.get('exam_text')
                        exam_count = exam_result.get('exam_count', 0)
                    else:
                        exam_text = None
                        exam_count = 0
                    exam_data = None
                has_exams = exam_count > 0
                # Format lịch học
                all_schedules = schedule_result.get('all_schedules', {})
                formatted_weekly_schedule = None
                has_classes = False
                if 'daily_schedules' in all_schedules:
                    daily_schedules = all_schedules['daily_schedules']
                    days_with_classes = [day for day in daily_schedules if day.get('classes')]
                    has_classes = len(days_with_classes) > 0
                    if has_classes:
                        formatted_weekly_schedule = "\n".join([
                            f"--- {schedule_service.get_vietnamese_weekday(datetime.strptime(day['date'], '%Y-%m-%d').weekday())}, {datetime.strptime(day['date'], '%Y-%m-%d').strftime('%d/%m/%Y')} ---\n" + schedule_service.format_schedule_for_display(day, include_header=False)
                            for day in days_with_classes
                        ])
                elif 'schedule' in all_schedules:
                    schedule = all_schedules['schedule']
                    has_classes = bool(schedule.get('classes'))
                    formatted_weekly_schedule = schedule_service.format_schedule_for_display(schedule, include_header=True) if has_classes else None
                # Tạo prompt gửi cho AI
                combined_data = ""
                if has_classes:
                    combined_data += "LỊCH HỌC (chỉ liệt kê các ngày có lớp):\n" + formatted_weekly_schedule + "\n"
                # Luôn luôn add toàn bộ lịch thi nếu là date_query
                if classification_result['category'] == 'date_query':
                    combined_data += "Đây là LỊCH THI:\n" + (exam_text or "Không có lịch thi nào phù hợp với yêu cầu.")
                elif has_exams:
                    combined_data += "LỊCH THI:\n" + exam_text
                # Nếu cả lịch học và lịch thi đều không có, trả lời lịch thi trống
                if not has_classes and not has_exams:
                    combined_data = "Hiện tại bạn không có lịch thi hoặc lịch học nào trong hệ thống."
                elif not combined_data.strip():
                    combined_data = "Không tìm thấy thông tin lớp học hoặc lịch thi cho ngày này."
                schedule_prompt = {
                    "role": "system",
                    "content": f"""
                    Bạn là trợ lý học tập cho sinh viên đại học. Dưới đây là thông tin lịch lấy từ hệ thống:{combined_data}Dựa trên lịch sử trò chuyện hãy trả lời đầy đủ, phải liệt kê chi tiết từng ngày và từng lớp học có trong dữ liệu trên. Nếu có lịch thi, hãy liệt kê rõ ràng từng môn thi, ngày thi, phòng thi. Nếu là lịch tuần, phải nhấn mạnh đây là lịch cho các ngày có lớp trong tuần từ {schedule_result['date_info']}.
                    Trả lời bằng tiếng Việt, văn phong tự nhiên, thân thiện, nhưng tuyệt đối không được tóm tắt hay rút gọn nội dung lịch học.
                    """
                }
                print("[SCHEDULE PROMPT]", f"Prompt content:\n{schedule_prompt['content']}")
                print("[SCHEDULE DATA]", f"formatted_weekly_schedule:\n{formatted_weekly_schedule}")
                # Tạo messages list: chỉ system prompt + user message hiện tại
                messages = [schedule_prompt, {"role": "user", "content": message}]
                # Gọi AI với temperature 0.8
                try:
                    agent_config = get_agent(agent_id)
                    agent_config["temperature"] = 0.8
                    enhanced_response, _ = ai_service.chat_with_ai(
                        message, 
                        messages,
                        agent_id
                    )
                except Exception as ai_error:
                    logger.log_with_timestamp("SCHEDULE AI ERROR", f"Failed to get AI response: {str(ai_error)}")
                    enhanced_response = f"Lịch của bạn:\n\n{combined_data}\n\nHãy chuẩn bị thật kỹ và đến đúng giờ nhé!"
                conversation_history.append({
                    "role": "system",
                    "content": f"Schedule data: {schedule_result.get('schedule_text')}\nExam data: {exam_text}"
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": enhanced_response
                })
                return jsonify({
                    'response': enhanced_response,
                    'schedule_data': schedule_result,
                    'exam_data': exam_data,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule',
                    'agent_id': agent_id
                })
            except Exception as e:
                error_msg = f"Error processing schedule/exam data: {str(e)}"
                logger.log_with_timestamp("SCHEDULE ERROR", error_msg)
                return jsonify({
                    'error': error_msg,
                    'schedule_data': None,
                    'exam_data': None,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule',
                    'agent_id': agent_id
                }), 500
        
        # Handle exam schedule queries
        if classification_result['category'] == 'examschedule':
            logger.log_with_timestamp(
                "EXAM SCHEDULE QUERY", 
                f"Processing exam schedule request", 
                f"Current time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            try:
                credentials = data.get('university_credentials')
                if not credentials:
                    raise Exception("Vui lòng cập nhật thông tin đăng nhập vào hệ thống trường học trong phần Thiết lập.")
                success, error = ptit_auth_service.login(
                    credentials['university_username'],
                    credentials['university_password']
                )
                if not success:
                    raise Exception("Không thể đăng nhập vào hệ thống trường học. Vui lòng kiểm tra lại thông tin đăng nhập.")
                current_semester, semester_error = ptit_auth_service.get_current_semester()
                if semester_error:
                    raise Exception(f"Không thể lấy thông tin học kỳ: {semester_error}")
                # Lấy toàn bộ lịch thi học kỳ
                exam_data = await exam_schedule_service.get_exam_schedule_by_semester(current_semester['hoc_ky'], False)
                exam_list = exam_data['data']['ds_lich_thi'] if exam_data.get('data') and exam_data['data'].get('ds_lich_thi') else []
                exam_text = exam_schedule_service.format_exam_schedule(exam_list)
                exam_count = len(exam_list)
                # Prompt: truyền toàn bộ lịch thi cho AI
                exam_prompt = {
                    "role": "system",
                    "content": f"""
                    Bạn là trợ lý học tập cho sinh viên đại học. Dưới đây là toàn bộ lịch thi học kỳ lấy từ hệ thống:
                    {exam_text}
                    Hãy tổng hợp và trả lời tổng quan về lịch thi cho sinh viên.đảm bảo đầy đủ môn thi, ngày thi, phòng thi, giờ thi,thời gian làm bài. Trả lời bằng tiếng Việt, văn phong tự nhiên.
                    """
                }
                logger.log_with_timestamp("EXAM SCHEDULE PROMPT", exam_prompt['content'])
                # Tạo messages list: chỉ system prompt + user message hiện tại
                messages = [exam_prompt, {"role": "user", "content": message}]
                try:
                    enhanced_response, _ = ai_service.chat_with_ai(
                        message, 
                        messages,
                        agent_id
                    )
                except Exception as ai_error:
                    logger.log_with_timestamp("EXAM SCHEDULE AI ERROR", f"Failed to get AI response: {str(ai_error)}")
                    enhanced_response = f"Lịch thi của bạn:\n\n{exam_text}\n\nHãy chuẩn bị thật kỹ và đến đúng giờ nhé!"
                conversation_history.append({
                    "role": "system",
                    "content": exam_text
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": enhanced_response
                })
                return jsonify({
                    'response': enhanced_response,
                    'exam_data': exam_data,
                    'conversation_history': conversation_history,
                    'query_type': 'examschedule',
                    'agent_id': agent_id
                })
            except Exception as e:
                error_msg = f"Error processing exam schedule: {str(e)}"
                logger.log_with_timestamp("EXAM SCHEDULE ERROR", error_msg)
                return jsonify({
                    'error': error_msg,
                    'exam_data': None,
                    'conversation_history': conversation_history,
                    'query_type': 'examschedule',
                    'agent_id': agent_id
                }), 500
        
        # If education-related (but not schedule), proceed with normal processing
        system_message = {
            "role": "system",
            "content": (
                "You are a dedicated study assistant for university students in Vietnam. "
                "Your role includes:\n\n"
                "1. Supporting academic success and engagement\n"
                "2. Providing motivation when students feel like skipping classes\n"
                "3. Helping students understand the importance of attendance\n"
                "4. Offering constructive advice for academic challenges\n"
                "5. Suggesting strategies to maintain focus and motivation\n\n"
                f"The student's query was classified as: {classification_result['category']}\n\n"
                "Keep responses focused, constructive, and supportive. "
                "Use examples and concrete steps when appropriate."
            )
        }
        
        # Luôn chỉ truyền system + user message hiện tại cho AI
        messages = [system_message, {"role": "user", "content": message}]
        logger.log_with_timestamp(
            "AI REQUEST", 
            message, 
            f"Query type: {classification_result['category']} | NO HISTORY (thinking mode)"
        )
        start_time = time.time()
        response, updated_history = ai_service.chat_with_ai(message, messages, agent_id)
        time_taken = round(time.time() - start_time, 2)
        logger.log_with_timestamp(
            "AI RESPONSE", 
            response, 
            f"Time: {time_taken}s"
        )
        return jsonify({
            'response': response, 
            'conversation_history': updated_history,
            'query_type': classification_result['category'],
            'agent_id': agent_id
        })
        
    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("ERROR", error_message)
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': error_message}), 500

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