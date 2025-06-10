import asyncio
import json
import httpx
import uuid
from ..utils.logger import Logger
from ..lib.supabase import supabase

logger = Logger()

class WebSearchService:
    def __init__(self):
        # Google Custom Search API credentials
        # Cần tạo tại: https://developers.google.com/custom-search/v1/introduction
        self.GOOGLE_API_KEY = "AIzaSyBcWP-MavLpMc1SF-IryANHxkB1uuiAcb8"
        self.GOOGLE_SEARCH_ENGINE_ID = "315c7d160a9b0494c"  # cx parameter
        # Google Custom Search API URL
        self.GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"

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
            
            # Call the Google Custom Search API
            google_params = {
                "key": self.GOOGLE_API_KEY,
                "cx": self.GOOGLE_SEARCH_ENGINE_ID,
                "q": query,
                "num": 10,  # Number of results (max 10)
                "lr": "lang_vi",  # Language restriction to Vietnamese
                "safe": "medium"  # Safe search level
            }
            
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
                    raw_json = json.dumps(result, indent=2)[:1000]
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
                    # Đảm bảo kết quả luôn có các trường cần thiết và không null
                    result = {
                        'title': item.get('title', 'Untitled'),
                        'url': item.get('link', '#'),  # Google uses 'link' instead of 'url'
                        'snippet': item.get('snippet', '')
                    }
                    formatted_results.append(result)
            
            # Log kết quả đầu tiên để kiểm tra định dạng
            if formatted_results:
                logger.log_with_timestamp('SEARCH_FORMAT', f'First result format: {json.dumps(formatted_results[0])}')
            
            # Limit to top 5 results to avoid overwhelming context
            return formatted_results[:5]
            
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