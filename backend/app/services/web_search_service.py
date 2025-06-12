import asyncio
import json
import httpx
import uuid
from ..utils.logger import Logger
from ..lib.supabase import supabase
from .web_scraper_service import WebScraperService

logger = Logger()

# LM Studio configuration for query optimization
LMSTUDIO_URL = "http://192.168.1.216:1234/v1/chat/completions"
LMSTUDIO_AUTH = "lm-studio"
LMSTUDIO_HEADERS = {
    "Authorization": f"Bearer {LMSTUDIO_AUTH}",
    "Content-Type": "application/json"
}

class WebSearchService:
    def __init__(self):
        # Google Custom Search API credentials
        # Cần tạo tại: https://developers.google.com/custom-search/v1/introduction
        self.GOOGLE_API_KEY = "AIzaSyBcWP-MavLpMc1SF-IryANHxkB1uuiAcb8"
        self.GOOGLE_SEARCH_ENGINE_ID = "315c7d160a9b0494c"  # cx parameter
        # Google Custom Search API URL
        self.GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"
        # Đảm bảo kết quả trả về không bị escape Unicode
        self.GOOGLE_PARAMS = {
            "key": "AIzaSyBcWP-MavLpMc1SF-IryANHxkB1uuiAcb8",
            "cx": "315c7d160a9b0494c",
            "num": 10,  # Number of results (max 10)
            "lr": "lang_vi",  # Language restriction to Vietnamese
            "safe": "medium",  # Safe search level
            "prettyPrint": True  # Để dễ đọc kết quả
        }
        # Khởi tạo web scraper
        self.web_scraper = WebScraperService()

    async def optimize_query_with_llm(self, user_query, agent_model):
        """
        Use LLM to optimize search query before performing web search.
        
        Args:
            user_query (str): Original user query
            agent_model (str): Model name being used by the user
            
        Returns:
            str: Optimized search query
        """
        try:
            logger.log_with_timestamp('QUERY_OPTIMIZATION', f'Optimizing query: "{user_query}" using model: {agent_model}')
            
            # System prompt for query optimization (KHÔNG ưu tiên tiếng Anh)
            system_prompt = (
                "Bạn là chuyên gia tối ưu hóa truy vấn tìm kiếm web. Hãy chuyển đổi câu hỏi của người dùng thành một truy vấn tìm kiếm hiệu quả nhất, ngắn gọn, giữ lại các từ khóa quan trọng.\n"
                "Chỉ trả về một object JSON duy nhất với trường 'query' chứa truy vấn tối ưu, không giải thích, không thêm bất kỳ văn bản nào khác.\n"
                "Ví dụ:\n"
                "User: 'Tôi muốn biết về tình hình kinh tế Việt Nam hiện tại'\n"
                "Output: {\"query\": \"tình hình kinh tế Việt Nam 2024\"}\n"
                "User: 'Cách học lập trình Python hiệu quả'\n"
                "Output: {\"query\": \"phương pháp học lập trình Python hiệu quả cho người mới\"}"
            )
            
            # JSON schema giống như trong lmstudio_service.py
            payload = {
                'model': agent_model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_query + ' /no_thinking'}
                ],
                'response_format': {
                    'type': 'json_schema',
                    'json_schema': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'query': {
                                    'type': 'string'
                                }
                            },
                            'required': ['query'],
                            'additionalProperties': False
                        }
                    }
                },
                'temperature': 0.2,
                'max_tokens': 50,
                'stream': False
            }
            
            # Log the optimization request
            logger.log_with_timestamp('QUERY_OPTIMIZATION_REQUEST', f'Sending to LM Studio: {json.dumps(payload, ensure_ascii=False)}')
            
            # Make request to LM Studio
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    LMSTUDIO_URL,
                    headers=LMSTUDIO_HEADERS,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    try:
                        query_obj = json.loads(content)
                        optimized_query = query_obj['query'].strip()
                        logger.log_with_timestamp('QUERY_OPTIMIZATION_SUCCESS', f'Original: "{user_query}" -> Optimized: "{optimized_query}"')
                        return optimized_query
                    except Exception as e:
                        logger.log_with_timestamp('QUERY_OPTIMIZATION_PARSE_ERROR', f'Error parsing JSON: {str(e)} | Content: {content}')
                        return user_query
                else:
                    logger.log_with_timestamp('QUERY_OPTIMIZATION_ERROR', f'LM Studio error: {response.status_code}')
                    return user_query
                    
        except Exception as e:
            logger.log_with_timestamp('QUERY_OPTIMIZATION_ERROR', f'Error optimizing query: {str(e)}')
            return user_query

    async def search_with_optimization(self, user_query, agent_model, chat_id=None, save_to_db=False, with_scraping=True):
        """
        Perform web search with LLM query optimization and optional content scraping.
        
        Args:
            user_query (str): Original user query
            agent_model (str): Model name being used by the user
            chat_id (uuid, optional): The chat session ID to save search results to
            save_to_db (bool, optional): Whether to save search results to database
            with_scraping (bool, optional): Whether to scrape content from search results
            
        Returns:
            dict: Contains optimized_query and search results
        """
        try:
            # Step 1: Optimize query using LLM
            optimized_query = await self.optimize_query_with_llm(user_query, agent_model)
            
            # Step 2: Perform search with optimized query and optional scraping
            if with_scraping:
                logger.log_with_timestamp('SEARCH_WITH_OPTIMIZATION', f'Using scraping for query: "{optimized_query}"')
                search_results = await self.search_with_scraping(optimized_query, chat_id, save_to_db)
            else:
                search_results = await self.search(optimized_query, chat_id, save_to_db)
            
            # Return both optimized query and results for transparency
            return {
                'original_query': user_query,
                'optimized_query': optimized_query,
                'results': search_results
            }
            
        except Exception as e:
            logger.log_with_timestamp('SEARCH_WITH_OPTIMIZATION_ERROR', f'Error in optimized search: {str(e)}')
            # Fallback to regular search with original query
            search_results = await self.search(user_query, chat_id, save_to_db)
            return {
                'original_query': user_query,
                'optimized_query': user_query,  # Same as original if optimization failed
                'results': search_results
            }

    async def search(self, query, chat_id=None, save_to_db=False):
        """
        Perform a web search using Google Custom Search API.
        
        Args:
            query (str): The search query
            chat_id (uuid, optional): The chat session ID to save search results to
            save_to_db (bool, optional): Whether to save search results to database
            
        Returns:
            list: Search results with snippets and URLs
        """
        try:
            logger.log_with_timestamp('WEB_SEARCH', f'Searching web for: "{query}"')
            
            # Call the Google Custom Search API - sử dụng self.GOOGLE_PARAMS
            google_params = self.GOOGLE_PARAMS.copy()
            google_params["q"] = query
            
            print('[GOOGLE_SEARCH_PAYLOAD] params:', google_params)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.GOOGLE_API_URL,
                    params=google_params
                )
                
                # Check if response is successful
                if response.status_code != 200:
                    logger.log_with_timestamp(
                        'WEB_SEARCH_ERROR', 
                        f'Error from Google Search API: Status {response.status_code}'
                    )
                    return []
                
                # Parse JSON response
                result = response.json()
                
                # Log the raw response structure for debugging
                try:
                    raw_json = json.dumps(result, ensure_ascii=False, indent=2)[:1000]
                    logger.log_with_timestamp('WEB_SEARCH_RAW', f'Raw API structure: {raw_json}')
                    print('[WEB_SEARCH_RAW]', raw_json)
                    
                    if 'items' not in result:
                        logger.log_with_timestamp('WEB_SEARCH_RAW', 'No "items" key in Google API response!')
                        print('[WEB_SEARCH_RAW] No "items" key in Google API response!')
                        # Check for errors
                        if 'error' in result:
                            error_msg = result['error'].get('message', 'Unknown error')
                            logger.log_with_timestamp('WEB_SEARCH_ERROR', f'Google API Error: {error_msg}')
                    else:
                        items = result.get('items', [])
                        logger.log_with_timestamp('WEB_SEARCH_RAW', f'Number of search results: {len(items)}')
                        print(f'[WEB_SEARCH_RAW] Number of search results: {len(items)}')
                except Exception as e:
                    logger.log_with_timestamp('WEB_SEARCH_RAW', f'Error logging raw structure: {str(e)}')
                    print('[WEB_SEARCH_RAW] Error logging raw structure:', str(e))
                
                logger.log_with_timestamp('WEB_SEARCH', 'Successfully received search results')
                
                # Process and format results
                search_results = self._format_search_results(result)
                logger.log_with_timestamp('WEB_SEARCH', f'Found {len(search_results)} results')
                
                # Save to database if requested
                if save_to_db and chat_id:
                    try:
                        await self.save_search_results(chat_id, query, search_results)
                    except Exception as e:
                        logger.log_with_timestamp('WEB_SEARCH_DB_ERROR', f'Error saving search results: {str(e)}')
                
                return search_results
                    
        except Exception as e:
            logger.log_with_timestamp('WEB_SEARCH_ERROR', f'Error searching web: {str(e)}')
            # Return empty results on error
            return []
    
    def _format_search_results(self, raw_results):
        """
        Format and extract relevant information from raw Google search results.
        
        Args:
            raw_results (dict): Raw search results from Google Custom Search
            
        Returns:
            list: Formatted search results with snippets and URLs
        """
        formatted_results = []
        
        try:
            # Extract results from the Google Custom Search API response
            if isinstance(raw_results, dict):
                items = raw_results.get('items', [])
                
                for item in items:
                    # Decode Unicode escape sequences in title and snippet
                    title = item.get('title', 'Untitled')
                    snippet = item.get('snippet', '')
                    url = item.get('link', '#')
                    
                    # Log title trước khi decode để debug
                    logger.log_with_timestamp('SEARCH_TITLE_RAW', f'Raw title: {title}')
                    
                    # Đảm bảo kết quả luôn có các trường cần thiết và không null
                    result = {
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    }
                    formatted_results.append(result)
            
            # Log kết quả đầu tiên để kiểm tra định dạng
            if formatted_results:
                logger.log_with_timestamp('SEARCH_FORMAT', f'First result format: {json.dumps(formatted_results[0], ensure_ascii=False)}')
            
            # Trả về tối đa 10 kết quả thay vì 5
            return formatted_results[:10]
            
        except Exception as e:
            logger.log_with_timestamp('WEB_SEARCH_ERROR', f'Error formatting results: {str(e)}')
            return formatted_results
            
    async def save_message_with_sources(self, chat_id, role, content, sources=None):
        """
        Save a message with optional search results to the database.
        
        Args:
            chat_id (uuid): The chat session ID
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
            sources (list, optional): List of search results to save
            
        Returns:
            int: ID of the saved message
        """
        try:
            # Validate chat_id
            if not chat_id:
                logger.log_with_timestamp('MESSAGE_SAVE_ERROR', 'No chat_id provided, skipping message save')
                return None
                
            # Convert chat_id to string if it's already a UUID object
            if isinstance(chat_id, uuid.UUID):
                chat_id = str(chat_id)
                
            # Validate chat_id format
            try:
                # Check if this is a valid UUID
                uuid_obj = uuid.UUID(chat_id)
            except ValueError:
                logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Invalid chat_id format: {chat_id}')
                return None
            
            # Prepare message data
            message_data = {
                'chat_id': chat_id,
                'role': role,
                'content': content
            }
            
            # Add sources if provided, ensuring correct format
            if sources and isinstance(sources, list):
                # Validate and format sources as valid JSON array
                formatted_sources = []
                for source in sources:
                    if isinstance(source, dict):
                        formatted_source = {
                            'title': source.get('title', 'Untitled'),
                            'url': source.get('url', '#'),
                            'snippet': source.get('snippet', '')
                        }
                        formatted_sources.append(formatted_source)
                
                # Only add if we have valid sources
                if formatted_sources:
                    message_data['sources'] = formatted_sources
                    logger.log_with_timestamp('MESSAGE_SAVE', f'Adding {len(formatted_sources)} formatted sources to message')
            
            # Log before database save
            logger.log_with_timestamp('MESSAGE_SAVE', f'Saving {role} message to chat {chat_id}')
            
            # Debug purpose - show raw message data structure
            try:
                logger.log_with_timestamp('MESSAGE_DATA', f'Data structure: {json.dumps(message_data)}')
            except Exception as e:
                logger.log_with_timestamp('MESSAGE_DATA_ERROR', f'Error logging message data: {str(e)}')
            
            # Save to database
            result = supabase.table('messages').insert(message_data).execute()
            
            # Check for successful insert and return the ID
            if result and hasattr(result, 'data') and len(result.data) > 0:
                message_id = result.data[0].get('id')
                logger.log_with_timestamp('MESSAGE_SAVE', f'Saved message with ID: {message_id}')
                return message_id
            else:
                logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Failed to save message, result: {result}')
                return None
                
        except Exception as e:
            logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Error saving message: {str(e)}')
            return None
            
    async def save_search_results(self, chat_id, query, results):
        """
        Save search results separately for logging or analysis purposes.
        
        Args:
            chat_id (uuid): The chat session ID
            query (str): The search query
            results (list): Search results
            
        Returns:
            bool: Success or failure
        """
        try:
            # This could be used to save search results in a separate table if needed
            logger.log_with_timestamp('SEARCH_SAVE', f'Search results for chat {chat_id} saved')
            return True
        except Exception as e:
            logger.log_with_timestamp('SEARCH_SAVE_ERROR', f'Error saving search results: {str(e)}')
            return False

    async def search_with_scraping(self, query, chat_id=None, save_to_db=False):
        """
        Perform web search and scrape content from the top results.
        
        Args:
            query (str): The search query
            chat_id (uuid, optional): The chat session ID to save search results to
            save_to_db (bool, optional): Whether to save search results to database
            
        Returns:
            list: Search results with snippets, URLs, and scraped content
        """
        try:
            logger.log_with_timestamp('WEB_SEARCH_SCRAPING', f'Searching and scraping for: "{query}"')
            
            # Step 1: Get search results from Google
            search_results = await self.search(query, chat_id, save_to_db)
            
            if not search_results:
                logger.log_with_timestamp('WEB_SEARCH_SCRAPING', 'No search results found')
                return []
                
            # Step 2: Extract URLs from top 5 results
            urls_to_scrape = [result['url'] for result in search_results[:5]]
            
            # Step 3: Scrape content from these URLs
            logger.log_with_timestamp('WEB_SEARCH_SCRAPING', f'Scraping {len(urls_to_scrape)} URLs')
            scraped_contents = await self.web_scraper.scrape_urls(urls_to_scrape)
            
            # Step 4: Merge scraped content with search results
            for i, result in enumerate(search_results):
                # Find matching scraped content for this URL
                for scraped in scraped_contents:
                    if scraped['url'] == result['url']:
                        # Add scraped content to search result
                        result['scraped_content'] = scraped['content']
                        break
                else:
                    # No scraped content found for this URL
                    result['scraped_content'] = ""
            
            logger.log_with_timestamp('WEB_SEARCH_SCRAPING', f'Completed scraping for {len(scraped_contents)} URLs')
            return search_results
            
        except Exception as e:
            logger.log_with_timestamp('WEB_SEARCH_SCRAPING_ERROR', f'Error in search with scraping: {str(e)}')
            # Fallback to regular search without scraping
            return await self.search(query, chat_id, save_to_db) 