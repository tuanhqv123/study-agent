from .ptit_cache_service import ptit_cache_service
from typing import Dict, Optional, Tuple
import asyncio
import time

class PTITAPIService:
    """Wrapper service for PTIT APIs with Redis caching"""
    
    def __init__(self):
        self.ptit_cache = ptit_cache_service
    
    async def get_current_semester_with_cache(self, chat_session_id: str, ptit_auth_service) -> Tuple[Optional[Dict], bool]:
        """Get current semester with caching"""
        # Try cache first
        cached_data = self.ptit_cache.get_cached_data(
            chat_session_id,
            "current_semester"
        )
        
        if cached_data:
            return cached_data, True  # From cache
        
        # Cache miss - call API
        try:
            current_sem, _ = ptit_auth_service.get_current_semester()
            
            # Cache the result
            if current_sem:
                self.ptit_cache.set_cached_data(
                    chat_session_id,
                    "current_semester",
                    current_sem
                )
            
            return current_sem, False  # From API
            
        except Exception as e:
            print(f"❌ Current semester API error: {e}")
            return None, False
    
    async def get_schedule_with_cache(self, chat_session_id: str, time_info: Dict, semester: str, schedule_service) -> Tuple[Optional[Dict], bool]:
        """Get schedule data with caching"""
        cache_params = {
            "time_type": time_info.get('type'),
            "date": time_info.get('date'),
            "week": time_info.get('week'),
            "semester": semester
        }
        
        # Try cache first
        cached_data = self.ptit_cache.get_cached_data(
            chat_session_id, 
            "schedule", 
            cache_params
        )
        
        if cached_data:
            return cached_data, True  # From cache
        
        # Cache miss - call API
        try:
            schedule_data = await schedule_service.process_schedule_query(time_info, semester)
            
            # Cache the result
            if schedule_data:
                self.ptit_cache.set_cached_data(
                    chat_session_id,
                    "schedule", 
                    schedule_data,
                    cache_params
                )
            
            return schedule_data, False  # From API
            
        except Exception as e:
            print(f"❌ Schedule API error: {e}")
            return None, False

    async def get_exams_with_cache(self, chat_session_id: str, query: str, semester: str, exam_schedule_service) -> Tuple[Optional[Dict], bool]:
        """Get exam data with caching"""
        cache_params = {
            "query": query.lower().strip(),
            "semester": semester
        }
        
        # Try cache first
        cached_data = self.ptit_cache.get_cached_data(
            chat_session_id,
            "exams",
            cache_params
        )
        
        if cached_data:
            return cached_data, True  # From cache
        
        # Cache miss - call API
        try:
            exams_list, exam_txt, raw_data = await exam_schedule_service.get_exams_for_query(query, semester)
            
            exam_data = {
                "exams_list": exams_list,
                "exam_text": exam_txt,
                "raw_data": raw_data,
                "query": query,
                "semester": semester,
                "timestamp": time.time()
            }
            
            # Cache the result
            if exam_data and exam_txt:
                self.ptit_cache.set_cached_data(
                    chat_session_id,
                    "exams",
                    exam_data, 
                    cache_params
                )
            
            return exam_data, False  # From API
            
        except Exception as e:
            print(f"❌ Exams API error: {e}")
            return None, False

    async def get_all_exams_with_cache(self, chat_session_id: str, semester: str, exam_schedule_service) -> Tuple[Optional[Dict], bool]:
        """Get all exam schedule with caching"""
        cache_params = {
            "query": "all_exams",
            "semester": semester
        }
        
        # Try cache first
        cached_data = self.ptit_cache.get_cached_data(
            chat_session_id,
            "exams",
            cache_params
        )
        
        if cached_data:
            return cached_data, True
        
        # Cache miss - call API
        try:
            # Get full exam schedule for semester
            exam_data = await exam_schedule_service.get_exam_schedule_by_semester(semester, False)
            all_exams = exam_data.get('data', {}).get('ds_lich_thi', [])
            
            # Format exam list
            full_exam_txt = exam_schedule_service.format_exam_schedule(all_exams)
            
            formatted_exam_data = {
                "exams_list": all_exams,
                "exam_text": full_exam_txt,
                "raw_data": exam_data,
                "query": "all_exams",
                "semester": semester,
                "timestamp": time.time()
            }
            
            # Cache the result
            if formatted_exam_data and full_exam_txt:
                self.ptit_cache.set_cached_data(
                    chat_session_id,
                    "exams",
                    formatted_exam_data,
                    cache_params
                )
            
            return formatted_exam_data, False
            
        except Exception as e:
            print(f"❌ All Exams API error: {e}")
            return None, False

# Global instance
ptit_api_service = PTITAPIService()
