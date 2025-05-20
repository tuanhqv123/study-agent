from datetime import datetime, timedelta
import calendar
import re
import httpx
from unidecode import unidecode
from ..utils.logger import Logger

logger = Logger()

class ScheduleService:
    def __init__(self, auth_service=None, ai_service=None):
        self.today = datetime.now().date()
        self.base_url = "https://uis.ptithcm.edu.vn/api/sch"
        self.auth_service = auth_service
        self.ai_service = ai_service

    def set_auth_service(self, auth_service):
        """Set the authentication service for token management

        Args:
            auth_service (PTITAuthService): The authentication service instance
        """
        self.auth_service = auth_service
        
    def set_ai_service(self, ai_service):
        """Set the AI service for time analysis
        
        Args:
            ai_service (AiService): The AI service instance
        """
        self.ai_service = ai_service
        
    def check_auth(self):
        """Check if the service is properly authenticated

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.auth_service is not None and self.auth_service.access_token is not None
        
    def normalize_vietnamese(self, text):
        """
        Convert text with diacritics to non-diacritic form to make matching more robust
        """
        return unidecode(text).lower()

    def get_vietnamese_weekday(self, weekday_index):
        """
        Convert weekday index to Vietnamese weekday name
        0 = Monday, 6 = Sunday
        """
        weekday_names = {
            0: 'Thứ Hai',
            1: 'Thứ Ba',
            2: 'Thứ Tư',
            3: 'Thứ Năm',
            4: 'Thứ Sáu',
            5: 'Thứ Bảy',
            6: 'Chủ Nhật'
        }
        return weekday_names.get(weekday_index, '')

    async def get_schedule_by_semester(self, hoc_ky):
        """Get schedule data for a specific semester

        Args:
            hoc_ky (str): Semester ID

        Returns:
            dict: Schedule data including weekly schedules and class periods
        """
        logger.log_with_timestamp("SCHEDULE API", f"Getting schedule for semester: {hoc_ky}")
        
        if not self.check_auth():
            logger.log_with_timestamp("SCHEDULE API", "No auth token found, getting current semester...")
            current_semester, error = self.auth_service.get_current_semester()
            if error:
                logger.log_with_timestamp("SCHEDULE ERROR", f"Authentication error: {error}")
                raise ValueError(f"Authentication error: {error}")
            hoc_ky = current_semester.get('hoc_ky')
            logger.log_with_timestamp("SCHEDULE API", f"Using semester from current period: {hoc_ky}")

        url = f"{self.base_url}/w-locdstkbtuanusertheohocky"
        headers = {
            "Authorization": f"Bearer {self.auth_service.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "filter": {
                "hoc_ky": hoc_ky,
                "ten_hoc_ky": ""
            },
            "additional": {
                "paging": {
                    "limit": 100,
                    "page": 1
                },
                "ordering": [{
                    "name": None,
                    "order_type": None
                }]
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.log_with_timestamp("SCHEDULE API", f"Sending request to {url} with semester {hoc_ky}")
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Log detailed response information
                logger.log_with_timestamp("SCHEDULE API", f"Received response: Status {response.status_code}")
                logger.log_with_timestamp("SCHEDULE API", "Response data details:")
                
                if data.get('data'):
                    # Log semester information
                    semester_info = data['data'].get('hoc_ky', {})
                    logger.log_with_timestamp("SCHEDULE API", f"Semester: {semester_info.get('ten_hoc_ky', 'N/A')}")
                    
                    # Log weeks information
                    weeks = data['data'].get('ds_tuan_tkb', [])
                    logger.log_with_timestamp("SCHEDULE API", f"Total weeks: {len(weeks)}")
                
                return data
        except Exception as e:
            logger.log_with_timestamp("SCHEDULE ERROR", f"Error getting schedule: {str(e)}")
            raise

    def find_current_week_schedule(self, schedule_data, query_time=None):
        """Find the schedule for the week containing the query time

        Args:
            schedule_data (dict): Full schedule data from API
            query_time (datetime, optional): Time to find schedule for. Defaults to current time.

        Returns:
            dict: Schedule information for the matching week, or None if not found
        """
        if query_time is None:
            query_time = datetime.now()
        # Đảm bảo query_time là date
        if isinstance(query_time, datetime):
            query_time = query_time.date()
        for week in schedule_data.get("data", {}).get("ds_tuan_tkb", []):
            start_date = datetime.strptime(week["ngay_bat_dau"], "%d/%m/%Y").date()
            end_date = datetime.strptime(week["ngay_ket_thuc"], "%d/%m/%Y").date()
            if start_date <= query_time <= end_date:
                return week
        return None

    def get_class_schedule(self, week_data, query_date):
        """Get class schedule for a specific date within a week

        Args:
            week_data (dict): Week schedule data
            query_date (datetime): Date to get schedule for

        Returns:
            list: List of classes scheduled for the query date
        """
        if not week_data:
            logger.log_with_timestamp("SCHEDULE API", f"No week data found for date: {query_date.strftime('%Y-%m-%d')}")
            return []

        classes = []
        logger.log_with_timestamp("SCHEDULE API", f"Searching classes for date: {query_date.strftime('%Y-%m-%d')}")
        logger.log_with_timestamp("SCHEDULE API", f"Week data structure: {week_data.keys()}")
        
        # Check if we have the correct week data structure or if we're working with the entire schedule data
        # The correct structure should have 'ds_thoi_khoa_bieu', otherwise we need to find the right week first
        if "ds_thoi_khoa_bieu" in week_data:
            class_list = week_data.get("ds_thoi_khoa_bieu", [])
        else:
            # We might have received the entire schedule data instead of a specific week
            # Try to find classes for this date from all weeks
            query_date_obj = query_date.date() if hasattr(query_date, 'date') else query_date
            all_weeks = week_data.get("data", {}).get("ds_tuan_tkb", [])
            
            # Find all classes across all weeks
            all_classes = []
            for week in all_weeks:
                all_classes.extend(week.get("ds_thoi_khoa_bieu", []))
            
            # Filter to only classes for the requested date
            class_list = []
            for class_info in all_classes:
                try:
                    api_date = class_info.get("ngay_hoc", "")
                    class_date_str = api_date.split("T")[0] if "T" in api_date else api_date
                    class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
                    
                    if class_date == query_date_obj:
                        class_list.append(class_info)
                except Exception:
                    continue
        
        logger.log_with_timestamp("SCHEDULE API", f"Total classes in week: {len(class_list)}")
        
        for class_info in class_list:
            logger.log_with_timestamp("SCHEDULE API", f"Processing class: {class_info.get('ten_mon')} ({class_info.get('ma_mon')})")
            logger.log_with_timestamp("SCHEDULE API", f"Class data structure: {class_info.keys()}")
            
            api_date = class_info["ngay_hoc"]
            logger.log_with_timestamp("SCHEDULE API", f"Raw API date: {api_date}")
            
            try:
                # Ensure we're comparing dates properly by converting both to date objects
                class_date_str = api_date.split("T")[0] if "T" in api_date else api_date
                class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
                
                # Make sure query_date is a date object
                query_date_obj = query_date.date() if hasattr(query_date, 'date') else query_date
                
                logger.log_with_timestamp("SCHEDULE API", f"Parsed class date: {class_date}, Query date: {query_date_obj} | Match: {class_date == query_date_obj}")
                
                if class_date == query_date_obj:
                    start_time = f"Tiết {class_info['tiet_bat_dau']}"
                    end_time = f"Tiết {class_info['tiet_bat_dau'] + class_info['so_tiet'] - 1}"
                    class_detail = {
                        "subject": f"{class_info['ten_mon']} ({class_info['ma_mon']})",
                        "time": f"{start_time} - {end_time}",
                        "room": class_info['ma_phong'],
                        "lecturer": class_info['ten_giang_vien'] or "Chưa cập nhật",
                        "ngay_hoc": class_date.strftime('%d/%m/%Y'),
                        "thu_kieu_so": class_info.get('thu_kieu_so', 0),
                        "ten_mon_eg": class_info.get('ten_mon_eg', ''),
                        "so_tin_chi": class_info.get('so_tin_chi', ''),
                        "ma_giang_vien": class_info.get('ma_giang_vien', ''),
                        "ten_mon": class_info.get('ten_mon', ''),
                        "ma_mon": class_info.get('ma_mon', '')
                    }
                    classes.append(class_detail)
                    logger.log_with_timestamp("SCHEDULE API", f"Found class: {class_detail['subject']} | Room: {class_detail['room']} | Time: {class_detail['time']} | Lecturer: {class_detail['lecturer']}")
            except Exception as e:
                logger.log_with_timestamp("SCHEDULE ERROR", f"Error processing class date: {str(e)}")
                continue
        
        if not classes:
            logger.log_with_timestamp("SCHEDULE API", f"No classes found for date: {query_date.strftime('%Y-%m-%d')}")
        else:
            logger.log_with_timestamp("SCHEDULE API", f"Total classes found for {query_date.strftime('%d/%m/%Y')}: {len(classes)}")
            
        return classes

    async def get_schedule(self, date, hoc_ky):
        """Get schedule for a specific date from PTIT API

        Args:
            date (datetime.date): The date to get schedule for
            hoc_ky (str): Semester ID

        Returns:
            dict: Schedule data for the specified date
        """
        try:
            # Get schedule data from API
            schedule_data = await self.get_schedule_by_semester(hoc_ky)
            
            # Find the current week's schedule
            week_data = self.find_current_week_schedule(schedule_data, date)
            if not week_data:
                return {
                    "date": date.strftime('%Y-%m-%d'),
                    "day_of_week": date.strftime('%A'),
                    "thu_kieu_so": date.weekday() + 2,  # Convert to Vietnamese day format (2=Monday, 8=Sunday)
                    "semester": f"Học kỳ {hoc_ky}",
                    "classes": []
                }
            
            # Get classes for the specific date
            classes = self.get_class_schedule(week_data, date)
            
            return {
                "date": date.strftime('%Y-%m-%d'),
                "day_of_week": date.strftime('%A'),
                "thu_kieu_so": date.weekday() + 2,  # Convert to Vietnamese day format (2=Monday, 8=Sunday)
                "semester": f"Học kỳ {hoc_ky}",
                "classes": classes
            }
            
        except Exception as e:
            print(f"Error getting schedule from PTIT API: {e}")
            return None
    
    def format_schedule_for_display(self, schedule_data, include_header=True):
        """
        Format schedule data for display in the chat.
        
        Args:
            schedule_data (dict): Schedule data to format
            include_header (bool): Whether to include the header with date information
            
        Returns:
            str: Formatted schedule text
        """
        vietnamese_days = {
            "Monday": "Thứ Hai",
            "Tuesday": "Thứ Ba",
            "Wednesday": "Thứ Tư",
            "Thursday": "Thứ Năm",
            "Friday": "Thứ Sáu",
            "Saturday": "Thứ Bảy",
            "Sunday": "Chủ Nhật"
        }
        
        day_name = vietnamese_days.get(schedule_data['day_of_week'], schedule_data['day_of_week'])
        date_parts = schedule_data['date'].split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        thu_so = schedule_data.get('thu_kieu_so', 0)
        
        if not schedule_data["classes"]:
            if include_header:
                return f"Không có lớp học nào vào {day_name} (Thứ {thu_so}), ngày {formatted_date} ({schedule_data['semester']})."
            else:
                return ""
        
        result = ""
        if include_header:
            result = f"Lịch học ngày {formatted_date} ({day_name} - Thứ {thu_so}) - {schedule_data['semester']}:\n\n"
        
        for i, class_info in enumerate(schedule_data["classes"], 1):
            # Add Vietnamese subject name
            result += f"{i}. {class_info.get('ten_mon', '')} ({class_info.get('ma_mon', '')})\n"
            
            # Add English subject name if available
            if class_info.get('ten_mon_eg'):
                result += f"    {class_info.get('ten_mon_eg')}\n"
                
            # Add class time
            result += f"    {class_info['time']}\n"
            
            # Add room information
            result += f"    Phòng {class_info['room']}\n"
            
            # Add lecturer information with ID
            result += f"    {class_info['lecturer']}"
            if class_info.get('ma_giang_vien'):
                result += f" (Mã GV: {class_info.get('ma_giang_vien')})"
            result += "\n"
            
            # Add credit hours if available
            if class_info.get('so_tin_chi'):
                result += f"    Số tín chỉ: {class_info.get('so_tin_chi')}\n"
            
            # Add class date
            result += f"    Ngày học: {class_info.get('ngay_hoc', '')}\n"
                
            result += "\n"
        
        return result
        
    async def process_schedule_query(self, question, hoc_ky):
        """
        Xử lý truy vấn lịch học, tách ngày bằng AI (parse_time_lmstudio), không dùng extract_date_references nữa.
        """
        from .lmstudio_service import parse_time_lmstudio
        import calendar
        today = datetime.now().date()
        # Gọi AI để phân tích thời gian
        time_info = parse_time_lmstudio(question)
        type_ = time_info.get('type')
        value = time_info.get('value')
        print("[DEBUG] time_info:", time_info)
        print("[DEBUG] type_:", type_)
        print("[DEBUG] value:", value)
        # Nếu value chỉ là số (ví dụ '28'), tự động ghép tháng/năm hiện tại
        if type_ == 'day' and isinstance(value, str) and value.isdigit():
            today = datetime.now().date()
            value = f"{value}/{today.month:02d}/{today.year}"
            print("[DEBUG] value auto-filled with current month/year:", value)
        def get_week_dates(ref):
            if ref == 'current_week':
                start = today - timedelta(days=today.weekday())
            elif ref == 'next_week':
                start = today - timedelta(days=today.weekday()) + timedelta(days=7)
            else:
                # Nếu là ngày cụ thể ("25/03"), tìm tuần chứa ngày đó
                try:
                    d = datetime.strptime(ref+f'/{today.year}', '%d/%m/%Y').date()
                except:
                    d = today
                start = d - timedelta(days=d.weekday())
            return [(start + timedelta(days=i)) for i in range(7)]
        def filter_by_dates(dates):
            schedules = []
            for d in dates:
                s = d
                schedules.append(s)
            return schedules
        def filter_by_weekdays(weekdays, week_dates):
            weekday_map = {calendar.day_name[i]: i for i in range(7)}
            result = []
            for wd in weekdays:
                if wd in weekday_map:
                    idx = weekday_map[wd]
                    if idx < len(week_dates):
                        result.append(week_dates[idx])
            return result
        schedule_dates = []
        date_range_info = ''
        date_type = type_
        original_text = question
        if type_ == 'far_time':
            # Không hỗ trợ lấy lịch học cho các truy vấn quá xa
            formatted_message = "Xin lỗi, tôi chỉ hỗ trợ truy vấn lịch học trong tuần hoặc ngày cụ thể."
            all_schedules = {}
            return {
                'schedule_text': formatted_message,
                'date_info': '',
                'date_type': type_,
                'original_text': question,
                'all_schedules': all_schedules
            }
        elif type_ == 'day':
            if isinstance(value, str):
                # today, tomorrow, yesterday, "25/03", "Monday"...
                if value in ['today', 'tomorrow', 'yesterday']:
                    base = today
                    if value == 'tomorrow': base += timedelta(days=1)
                    if value == 'yesterday': base -= timedelta(days=1)
                    schedule_dates = [base]
                elif '/' in value:
                    try:
                        d = datetime.strptime(value+f'/{today.year}', '%d/%m/%Y').date()
                        schedule_dates = [d]
                    except:
                        schedule_dates = []
                elif value in calendar.day_name:
                    idx = list(calendar.day_name).index(value)
                    week_dates = get_week_dates('current_week')
                    if idx < len(week_dates):
                        schedule_dates = [week_dates[idx]]
                else:
                    schedule_dates = []
            elif isinstance(value, list):
                week_ref = None
                weekdays = []
                dates = []
                for v in value:
                    if v in ['current_week', 'next_week']:
                        week_ref = v
                    elif '/' in v:
                        dates.append(v)
                    elif v in calendar.day_name:
                        weekdays.append(v)
                if week_ref:
                    week_dates = get_week_dates(week_ref)
                    if weekdays:
                        schedule_dates = filter_by_weekdays(weekdays, week_dates)
                    elif dates:
                        # Chuyển chuỗi ngày sang date object
                        for dstr in dates:
                            try:
                                d = datetime.strptime(dstr+f'/{today.year}', '%d/%m/%Y').date()
                                schedule_dates.append(d)
                            except:
                                continue
                    else:
                        schedule_dates = week_dates
                else:
                    # Không có week_ref, chỉ lọc theo ngày/thứ
                    if weekdays:
                        week_dates = get_week_dates('current_week')
                        schedule_dates = filter_by_weekdays(weekdays, week_dates)
                    if dates:
                        for dstr in dates:
                            try:
                                d = datetime.strptime(dstr+f'/{today.year}', '%d/%m/%Y').date()
                                schedule_dates.append(d)
                            except:
                                continue
        elif type_ == 'week':
            if isinstance(value, str):
                if value in ['current_week', 'next_week']:
                    schedule_dates = get_week_dates(value)
                elif '/' in value:
                    try:
                        d = datetime.strptime(value+f'/{today.year}', '%d/%m/%Y').date()
                        schedule_dates = get_week_dates(value)
                    except:
                        schedule_dates = []
            elif isinstance(value, list):
                week_ref = None
                weekdays = []
                dates = []
                for v in value:
                    if v in ['current_week', 'next_week']:
                        week_ref = v
                    elif '/' in v:
                        dates.append(v)
                    elif v in calendar.day_name:
                        weekdays.append(v)
                if dates:
                    try:
                        d = datetime.strptime(dates[0]+f'/{today.year}', '%d/%m/%Y').date()
                        week_dates = get_week_dates(dates[0])
                    except:
                        week_dates = get_week_dates('current_week')
                elif week_ref:
                    week_dates = get_week_dates(week_ref)
                else:
                    week_dates = get_week_dates('current_week')
                if weekdays:
                    schedule_dates = filter_by_weekdays(weekdays, week_dates)
                else:
                    schedule_dates = week_dates
        # Sau khi tính xong schedule_dates
        print("[DEBUG] schedule_dates:", schedule_dates)
        if not schedule_dates:
            print("[DEBUG] schedule_dates is empty, fallback to current week")
            schedule_dates = get_week_dates('current_week')
        # Lấy lịch học cho các ngày đã xác định
        all_daily_schedules = []
        has_any_classes = False
        for d in schedule_dates:
            daily_schedule = await self.get_schedule(d, hoc_ky)
            print(f"[DEBUG] daily_schedule for {d}: {daily_schedule}")
            if daily_schedule:
                all_daily_schedules.append(daily_schedule)
                if daily_schedule.get("classes"):
                    has_any_classes = True
        print("[DEBUG] all_daily_schedules:", all_daily_schedules)
        # Format kết quả
        if len(schedule_dates) > 1:
            formatted_message = f"Đây là lịch học cho truy vấn của bạn ({type_}):\n\n"
            for daily_schedule in all_daily_schedules:
                current_date = datetime.strptime(daily_schedule['date'], '%Y-%m-%d').date()
                formatted_date = current_date.strftime('%d/%m/%Y')
                day_name = self.get_vietnamese_weekday(current_date.weekday())
                formatted_message += f"--- {day_name}, {formatted_date} ---\n"
                if daily_schedule["classes"]:
                    formatted_message += self.format_schedule_for_display(daily_schedule, include_header=False)
                else:
                    formatted_message += "Không có lớp học vào ngày này.\n"
                formatted_message += "\n"
            if not has_any_classes:
                formatted_message += f"Không có lớp học nào trong khoảng thời gian này.\nVui lòng kiểm tra lại lịch học trên hệ thống quản lý học tập của trường."
            date_range_info = f"{schedule_dates[0].strftime('%d/%m/%Y')} to {schedule_dates[-1].strftime('%d/%m/%Y')}"
            all_schedules = {
                'date_range': date_range_info,
                'daily_schedules': all_daily_schedules
            }
        elif len(schedule_dates) == 1:
            schedule_data = all_daily_schedules[0] if all_daily_schedules else None
            if schedule_data:
                formatted_message = self.format_schedule_for_display(schedule_data)
            else:
                formatted_message = "Xin lỗi, không thể lấy thông tin lịch học từ hệ thống. Vui lòng thử lại sau."
            date_range_info = schedule_dates[0].strftime('%d/%m/%Y')
            all_schedules = {
                'single_date': date_range_info,
                'schedule': schedule_data
            }
        else:
            print("[DEBUG] Không tìm thấy ngày phù hợp trong truy vấn hoặc không lấy được daily_schedules")
            formatted_message = "Không tìm thấy ngày phù hợp trong truy vấn của bạn."
            date_range_info = ''
            all_schedules = {}
        print("[DEBUG] RETURN all_schedules:", all_schedules)
        return {
            'schedule_text': formatted_message,
            'date_info': date_range_info,
            'date_type': type_,
            'original_text': question,
            'all_schedules': all_schedules
        }