from datetime import datetime, timedelta
import httpx
from ..utils.logger import Logger
from .lmstudio_service import parse_time_lmstudio

logger = Logger()

class ExamScheduleService:
    def __init__(self, auth_service=None, schedule_service=None):
        self.base_url = "https://uis.ptithcm.edu.vn/api/epm"
        self.auth_service = auth_service
        self.schedule_service = schedule_service
        
    def set_auth_service(self, auth_service):
        """Set the authentication service for token management

        Args:
            auth_service (PTITAuthService): The authentication service instance
        """
        self.auth_service = auth_service
        
    def set_schedule_service(self, schedule_service):
        """Set the schedule service for date extraction

        Args:
            schedule_service (ScheduleService): The schedule service instance
        """
        self.schedule_service = schedule_service
        
    def check_auth(self):
        """Check if the service is properly authenticated

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.auth_service is not None and self.auth_service.access_token is not None
        
    async def get_exam_schedule_by_semester(self, hoc_ky=None, is_giua_ky=False):
        """Get exam schedule data for a specific semester

        Args:
            hoc_ky (str): Semester ID, will use current semester if None
            is_giua_ky (bool): Whether to get midterm or final exam schedule

        Returns:
            dict: Exam schedule data
        """
        logger.log_with_timestamp("EXAM SCHEDULE API", f"Getting exam schedule for semester: {hoc_ky}, midterm: {is_giua_ky}")
        
        if not self.check_auth():
            logger.log_with_timestamp("EXAM SCHEDULE API", "No auth token found, getting current semester...")
            current_semester, error = self.auth_service.get_current_semester()
            if error:
                logger.log_with_timestamp("EXAM SCHEDULE ERROR", f"Authentication error: {error}")
                raise ValueError(f"Authentication error: {error}")
            hoc_ky = current_semester.get('hoc_ky')
            logger.log_with_timestamp("EXAM SCHEDULE API", f"Using semester from current period: {hoc_ky}")

        url = f"{self.base_url}/w-locdslichthisvtheohocky"
        headers = {
            "Authorization": f"Bearer {self.auth_service.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "filter": {
                "hoc_ky": hoc_ky,
                "is_giua_ky": is_giua_ky
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
                logger.log_with_timestamp("EXAM SCHEDULE API", f"Sending request to {url} with semester {hoc_ky}")
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                logger.log_with_timestamp("EXAM SCHEDULE API", f"Received response: Status {response.status_code}")
                
                if data.get('data'):
                    exams = data['data'].get('ds_lich_thi', [])
                    logger.log_with_timestamp("EXAM SCHEDULE API", f"Total exams: {len(exams)}")
                    
                    for exam in exams:
                        logger.log_with_timestamp("EXAM SCHEDULE API", 
                            f"Exam: {exam.get('ten_mon')} | Date: {exam.get('ngay_thi')} | Room: {exam.get('ma_phong')}")
                
                return data
        except Exception as e:
            logger.log_with_timestamp("EXAM SCHEDULE ERROR", f"Error getting exam schedule: {str(e)}")
            raise
            
    def get_exams_by_date(self, exam_data, date_str):
        """Get exams for a specific date

        Args:
            exam_data (dict): Full exam schedule data from API
            date_str (str): Date string in DD/MM/YYYY format

        Returns:
            list: List of exams on the specified date
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        date_exams = []
        
        for exam in exams:
            if exam.get('ngay_thi') == date_str:
                date_exams.append(exam)
                
        return date_exams
        
    def get_exams_by_date_range(self, exam_data, start_date, end_date):
        """Get exams within a date range (inclusive)

        Args:
            exam_data (dict): Full exam schedule data from API
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range

        Returns:
            list: List of exams within the date range
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            logger.log_with_timestamp("EXAM SCHEDULE", "No exam data available")
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        range_exams = []
        
        # Format dates for comparison
        start_date_str = start_date.strftime('%d/%m/%Y')
        end_date_str = end_date.strftime('%d/%m/%Y')
        
        logger.log_with_timestamp("EXAM SCHEDULE", f"Searching for exams between {start_date_str} and {end_date_str}")
        
        # Convert all dates in the range to strings for comparison
        date_range_strs = []
        current_date = start_date
        while current_date <= end_date:
            date_range_strs.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)
        
        # Find all exams with dates in the range
        for exam in exams:
            exam_date = exam.get('ngay_thi', '')
            if exam_date in date_range_strs:
                range_exams.append(exam)
                logger.log_with_timestamp("EXAM SCHEDULE", f"Found exam on {exam_date}: {exam.get('ten_mon')}")
                
        logger.log_with_timestamp("EXAM SCHEDULE", f"Found {len(range_exams)} exams in date range")
        return range_exams
        
    def get_exams_by_subject(self, exam_data, subject_keyword):
        """Get exams for a specific subject (by keyword)

        Args:
            exam_data (dict): Full exam schedule data from API
            subject_keyword (str): Subject name or code keyword

        Returns:
            list: List of exams matching the subject keyword
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        subject_exams = []
        
        subject_keyword = subject_keyword.lower()
        for exam in exams:
            subject_name = exam.get('ten_mon', '').lower()
            subject_code = exam.get('ma_mon', '').lower()
            
            if subject_keyword in subject_name or subject_keyword in subject_code:
                subject_exams.append(exam)
                
        return subject_exams
    
    def format_exam_schedule(self, exams, is_list=True):
        """Format exam schedule data for display

        Args:
            exams (list): List of exam data
            is_list (bool): Whether to format as a list of multiple exams

        Returns:
            str: Formatted exam schedule text
        """
        if not exams:
            return "Không tìm thấy lịch thi nào phù hợp với yêu cầu."
            
        result = ""
        
        for i, exam in enumerate(exams, 1):
            # Get the key exam information
            ten_mon = exam.get('ten_mon', 'N/A')
            ma_mon = exam.get('ma_mon', 'N/A')
            ky_thi = exam.get('ky_thi', 'N/A')
            hinh_thuc_thi = exam.get('hinh_thuc_thi', 'N/A')
            so_phut = exam.get('so_phut', 'N/A')
            gio_bat_dau = exam.get('gio_bat_dau', 'N/A')
            ngay_thi = exam.get('ngay_thi', 'N/A')
            dia_diem_thi = exam.get('dia_diem_thi', 'N/A')
            ma_phong = exam.get('ma_phong', 'N/A')
            ten_mon_eg = exam.get('ten_mon_eg', '')
            
            # Format the exam entry
            if is_list:
                result += f"{i}. {ten_mon} ({ma_mon})\n"
            else:
                result += f"{ten_mon} ({ma_mon})\n"
                
            # Add English subject name if available
            if ten_mon_eg:
                result += f"   {ten_mon_eg}\n"
                
            # Add exam details
            result += f"   {ky_thi}\n"
            result += f"   Hình thức: {hinh_thuc_thi}\n"
            result += f"   Thời gian: {gio_bat_dau}, {so_phut} phút, ngày {ngay_thi}\n"
            result += f"   Phòng thi: {ma_phong}, {dia_diem_thi}\n\n"
            
        return result
    
    async def process_exam_query(self, question, hoc_ky=None, is_giua_ky=False):
        """Process an exam schedule query and return formatted results (AI-first date extraction)"""
        # Get the complete exam schedule
        exam_data = await self.get_exam_schedule_by_semester(hoc_ky, is_giua_ky)
        all_exams = exam_data['data']['ds_lich_thi'] if exam_data.get('data') and exam_data['data'].get('ds_lich_thi') else []
        # Gọi AI để phân tích thời gian
        time_info = parse_time_lmstudio(question)
        type_ = time_info.get('type')
        value = time_info.get('value')
        from datetime import datetime, timedelta
        import calendar
        def get_week_dates(ref):
            today = datetime.now().date()
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
            return [(start + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
        def filter_by_dates(exams, dates):
            return [e for e in exams if e.get('ngay_thi') in dates]
        def filter_by_weekdays(exams, weekdays, week_dates):
            # weekdays: ['Monday', ...], week_dates: list of date string in that week
            weekday_map = {calendar.day_name[i]: i for i in range(7)}
            result = []
            for wd in weekdays:
                if wd in weekday_map:
                    idx = weekday_map[wd]
                    if idx < len(week_dates):
                        date = week_dates[idx]
                        result.extend([e for e in exams if e.get('ngay_thi') == date])
            return result
        exams_to_display = []
        filter_type = type_
        filter_value = value
        if type_ == 'far_time':
            exams_to_display = []
        elif type_ == 'day':
            # value có thể là string hoặc array
            if isinstance(value, str):
                # today, tomorrow, yesterday, "25/03", "Monday"...
                if value in ['today', 'tomorrow', 'yesterday']:
                    base = datetime.now().date()
                    if value == 'tomorrow': base += timedelta(days=1)
                    if value == 'yesterday': base -= timedelta(days=1)
                    date_str = base.strftime('%d/%m/%Y')
                    exams_to_display = filter_by_dates(all_exams, [date_str])
                elif '/' in value:
                    # "25/03" dạng ngày/tháng
                    try:
                        d = datetime.strptime(value+f'/{datetime.now().year}', '%d/%m/%Y').date()
                        date_str = d.strftime('%d/%m/%Y')
                        exams_to_display = filter_by_dates(all_exams, [date_str])
                    except:
                        exams_to_display = []
                elif value in calendar.day_name:
                    # "Monday" ... lấy ngày gần nhất trong tuần này
                    today = datetime.now().date()
                    idx = list(calendar.day_name).index(value)
                    week_dates = get_week_dates('current_week')
                    if idx < len(week_dates):
                        date = week_dates[idx]
                        exams_to_display = filter_by_dates(all_exams, [date])
                else:
                    exams_to_display = []
            elif isinstance(value, list):
                # Có thể gồm thứ, ngày, week context
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
                        exams_to_display = filter_by_weekdays(all_exams, weekdays, week_dates)
                    elif dates:
                        exams_to_display = filter_by_dates(all_exams, dates)
                    else:
                        exams_to_display = filter_by_dates(all_exams, week_dates)
                else:
                    # Không có week_ref, chỉ lọc theo ngày/thứ
                    if weekdays:
                        week_dates = get_week_dates('current_week')
                        exams_to_display = filter_by_weekdays(all_exams, weekdays, week_dates)
                    if dates:
                        exams_to_display += filter_by_dates(all_exams, dates)
        elif type_ == 'week':
            # value có thể là string hoặc array
            if isinstance(value, str):
                if value in ['current_week', 'next_week']:
                    week_dates = get_week_dates(value)
                    exams_to_display = filter_by_dates(all_exams, week_dates)
                elif '/' in value:
                    # "25/03" → lấy tuần chứa ngày đó
                    try:
                        d = datetime.strptime(value+f'/{datetime.now().year}', '%d/%m/%Y').date()
                        week_dates = get_week_dates(value)
                        exams_to_display = filter_by_dates(all_exams, week_dates)
                    except:
                        exams_to_display = []
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
                    # Lấy tuần chứa ngày đầu tiên
                    try:
                        d = datetime.strptime(dates[0]+f'/{datetime.now().year}', '%d/%m/%Y').date()
                        week_dates = get_week_dates(dates[0])
                    except:
                        week_dates = get_week_dates('current_week')
                elif week_ref:
                    week_dates = get_week_dates(week_ref)
                else:
                    week_dates = get_week_dates('current_week')
                if weekdays:
                    exams_to_display = filter_by_weekdays(all_exams, weekdays, week_dates)
                else:
                    exams_to_display = filter_by_dates(all_exams, week_dates)
        # Format kết quả
        formatted_exams = self.format_exam_schedule(exams_to_display)
        return {
            'exam_text': formatted_exams,
            'filter_type': filter_type,
            'filter_value': filter_value,
            'exam_count': len(exams_to_display),
            'is_midterm': is_giua_ky,
            'query': question,
            'is_full_data': False,
            'all_exams': exams_to_display
        } 

    async def get_exams_for_query(self, message, hoc_ky):
        """
        Phân tích ngày từ message, auto-fill tháng/năm nếu thiếu, lọc exam đúng ngày hoặc trong tuần, trả về danh sách exam và text.
        """
        exam_data = await self.get_exam_schedule_by_semester(hoc_ky, False)
        all_exams = exam_data['data']['ds_lich_thi'] if exam_data.get('data') and exam_data['data'].get('ds_lich_thi') else []
        time_info = parse_time_lmstudio(message)
        type_ = time_info.get('type')
        value = time_info.get('value')
        today = datetime.now().date()
        exam_dates = []
        date_info = ''
        from datetime import timedelta
        # Chuẩn hóa value
        if type_ == 'day':
            # Nếu value là số (int), ép về string
            if isinstance(value, int):
                value = str(value)
            # Nếu value là string số, auto-fill tháng/năm
            if isinstance(value, str) and value.isdigit():
                value = f"{value}/{today.month:02d}/{today.year}"
            # Nếu value là string ngày/tháng
            if isinstance(value, str) and '/' in value:
                try:
                    d = datetime.strptime(value, '%d/%m/%Y').date()
                    exam_dates = [d.strftime('%d/%m/%Y')]
                    date_info = d.strftime('%d/%m/%Y')
                except:
                    exam_dates = []
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, int) or (isinstance(v, str) and v.isdigit()):
                        v = f"{v}/{today.month:02d}/{today.year}"
                    if isinstance(v, str) and '/' in v:
                        try:
                            d = datetime.strptime(v, '%d/%m/%Y').date()
                            exam_dates.append(d.strftime('%d/%m/%Y'))
                        except:
                            continue
                if len(exam_dates) == 1:
                    date_info = exam_dates[0]
                elif len(exam_dates) > 1:
                    date_info = f"{exam_dates[0]} to {exam_dates[-1]}"
        elif type_ == 'week':
            # value có thể là string hoặc list
            def get_week_dates(ref):
                if ref == 'current_week':
                    start = today - timedelta(days=today.weekday())
                elif ref == 'next_week':
                    start = today - timedelta(days=today.weekday()) + timedelta(days=7)
                else:
                    try:
                        d = datetime.strptime(ref+f'/{today.year}', '%d/%m/%Y').date()
                    except:
                        d = today
                    start = d - timedelta(days=d.weekday())
                return [(start + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
            week_dates = []
            if isinstance(value, str):
                if value in ['current_week', 'next_week']:
                    week_dates = get_week_dates(value)
                elif '/' in value:
                    try:
                        d = datetime.strptime(value+f'/{today.year}', '%d/%m/%Y').date()
                        week_dates = get_week_dates(value)
                    except:
                        week_dates = []
            elif isinstance(value, list):
                week_ref = None
                dates = []
                for v in value:
                    if v in ['current_week', 'next_week']:
                        week_ref = v
                    elif '/' in v:
                        dates.append(v)
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
            exam_dates = week_dates
            if len(exam_dates) > 1:
                date_info = f"{exam_dates[0]} to {exam_dates[-1]}"
            elif len(exam_dates) == 1:
                date_info = exam_dates[0]
        # Lọc exam
        filtered_exams = [e for e in all_exams if e.get('ngay_thi') in exam_dates]
        exam_text = self.format_exam_schedule(filtered_exams)
        return filtered_exams, exam_text, date_info 