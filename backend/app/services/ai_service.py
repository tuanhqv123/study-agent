import httpx
from .file_service import FileService
from .web_search_service import WebSearchService
from .web_scraper_service import WebScraperService
import zlib
from ..config.agents import get_agent
import json
from ..utils.logger import Logger

logger = Logger()

LMSTUDIO_URL = "http://192.168.1.14:1234/v1/chat/completions"
LMSTUDIO_AUTH = "lm-studio"
HEADERS = {
    "Authorization": f"Bearer {LMSTUDIO_AUTH}",
    "Content-Type": "application/json"
}

class AiService:
    def __init__(self):
        self.web_search_service = WebSearchService()
        self.web_scraper_service = WebScraperService()

    @staticmethod
    def _plantuml_encode(text: str) -> str:
        data = text.encode('utf-8')
        compressed = zlib.compress(data, 9)[2:-4]
        enc_table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        result = ''
        buffer = 0
        bits_left = 0
        for byte in compressed:
            buffer = (buffer << 8) | byte
            bits_left += 8
            while bits_left >= 6:
                bits_left -= 6
                index = (buffer >> bits_left) & 0x3F
                result += enc_table[index]
        if bits_left:
            index = (buffer << (6 - bits_left)) & 0x3F
            result += enc_table[index]
        return result

    def _render_plantuml(self, ai_response: str) -> str:
        import re
        pattern = r'```plantuml\n(.*?)\n```'
        def replace(match):
            puml = match.group(1)
            encoded = self._plantuml_encode(puml)
            url = f"https://www.plantuml.com/plantuml/png/{encoded}"
            return f"{match.group(0)}\n\n![Diagram]({url})"
        return re.sub(pattern, replace, ai_response, flags=re.DOTALL)

    def chat_with_ai(self, message, messages=None, agent_id=None):
        if messages is None:
            messages = []
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'Using agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        # LOG PROMPT GỬI CHO LM STUDIO
        print("[AI PROMPT PAYLOAD]", json.dumps(payload, ensure_ascii=False, indent=2))
        try:
            response = httpx.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if '```plantuml' in content:
                content = self._render_plantuml(content)
            # Không tự động append user message nữa
            messages.append({"role": "assistant", "content": content})
            return content, messages
        except Exception as e:
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error: {str(e)}')
            error_response = "Sorry, I encountered an error while processing your request."
            messages.append({"role": "assistant", "content": error_response})
            return error_response, messages

    async def chat_with_file_context(self, message, file_id, conversation_history=None, agent_id=None):
        if conversation_history is None:
            conversation_history = []
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'File context with agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
        file_service = FileService()
        chunks = file_service.search_relevant_chunks_in_supabase(message, file_id)
        if chunks is None:
            chunks = []
        logger.log_with_timestamp('AI_SERVICE', f'Retrieved {len(chunks)} chunks for query: "{message[:30]}..."')
        if chunks:
            context = "\n\n---\n\n".join(chunks)
            system_content = f"You are a helpful study assistant. User uploaded a file and asks about its content.\nHere are relevant excerpts from the file:\n{context}\nAnswer based only on the above."
        else:
            system_content = "You are a helpful study assistant. User asked about an uploaded file, but no relevant content was found. Please inform them you cannot find info."
        system_message = {"role": "system", "content": system_content}
        messages = [system_message]
        for msg in conversation_history:
            if msg.get('role') != 'system':
                messages.append(msg)
        messages.append({"role": "user", "content": message})
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024
        }
        try:
            response = httpx.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": content})
            return content, conversation_history
        except Exception as e:
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error in chat_with_file_context: {str(e)}')
            error_response = "Sorry, I encountered an error while processing your request."
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": error_response})
            return error_response, conversation_history

    async def chat_with_web_search(self, message, conversation_history=None, agent_id=None, chat_id=None):
        if conversation_history is None:
            conversation_history = []
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'Web search context with agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
        # 1. Gọi web search thực sự
        search_results = await self.web_search_service.search(message, chat_id, save_to_db=True)
        # 2. Format prompt cho AI: chèn kết quả search vào system prompt
        if search_results:
            sources_text = "\n".join([
                f"- {item['title']}: {item['url']}\n{item['snippet']}" for item in search_results
            ])
        else:
            sources_text = "(Không tìm thấy kết quả web search phù hợp)"
        system_content = f"You are a helpful study assistant. Use the following web search results to answer the user's question as accurately as possible:\n\n{sources_text}"
        system_message = {"role": "system", "content": system_content}
        messages = [system_message, {"role": "user", "content": message}]
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024
        }
        try:
            response = httpx.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": content})
            return {"content": content, "sources": search_results}, conversation_history
        except Exception as e:
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error in chat_with_web_search: {str(e)}')
            error_response = "Sorry, I encountered an error while processing your request."
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": error_response})
            return {"content": error_response, "sources": search_results}, conversation_history