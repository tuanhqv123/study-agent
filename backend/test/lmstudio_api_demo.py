# -*- coding: utf-8 -*-
import json
import httpx

LMSTUDIO_URL = "http://192.168.1.14:1234/v1/chat/completions"
LMSTUDIO_AUTH = "lm-studio"

HEADERS = {
    "Authorization": f"Bearer {LMSTUDIO_AUTH}",
    "Content-Type": "application/json"
}

# 1. Classifier API
CLASSIFIER_MODEL = "qwen3-1.7b"
CLASSIFIER_SYSTEM_PROMPT = "You are an academic assistant and query classifier. Your tasks:\n\n1. Analyze the user's question (including Vietnamese shorthand or abbreviations) and classify it into one of the following categories:\n   - \"schedule\": Chỉ cho các câu hỏi về thời khóa biểu, lịch học (vd: \"hc\", \"tkb\", \"lịch học\", ...)\n   - \"examschedule\": Chỉ cho các câu hỏi về lịch thi, thi cử (vd: \"lt\", \"thi\", ...)\n   - \"date_query\": Cho các câu hỏi về ngày tháng, thời gian không cụ thể về lịch học/lịch thi.\n   - \"uml\": Cho các câu hỏi về sơ đồ, UML, PlantUML.\n   - \"general\": **Cho mọi câu hỏi, tâm sự, tư vấn, cảm xúc, động lực, định hướng, liên quan đến học tập, trường lớp, nghề nghiệp, kể cả khi người dùng nói về việc muốn nghỉ học, chuyển trường, bỏ học, chán học, v.v.**\n   - \"other\": Cho mọi câu hỏi không liên quan đến học tập, trường lớp, nghề nghiệp.\n\n2. Nếu câu hỏi về lớp năm sau, năm tới, luôn phân loại là \"other\".\n\n3. Nếu câu hỏi nguy hiểm, không phù hợp, không liên quan học tập, cũng phân loại \"other\".\n\n4. Chỉ trả về JSON object, không giải thích gì thêm.\n\n**Examples:**\n- User: \"Hôm nay hc gì?\"  \n  Output: {\"type\": \"schedule\"}\n- User: \"Bao giờ lt toán?\"  \n  Output: {\"type\": \"examschedule\"}\n- User: \"Ngày mai là ngày mấy?\"  \n  Output: {\"type\": \"date_query\"}\n- User: \"Vẽ sơ đồ lớp học bằng UML.\"  \n  Output: {\"type\": \"uml\"}\n- User: \"Tôi buồn quá, tôi muốn nghỉ học, chuyển sang trường khác\"  \n  Output: {\"type\": \"general\"}\n- User: \"Có nên bỏ học không?\"  \n  Output: {\"type\": \"general\"}\n- User: \"Em rất áp lực vì điểm kém, phải làm sao?\"  \n  Output: {\"type\": \"general\"}\n- User: \"Trường PTIT dạy dở đúng không?\"  \n  Output: {\"type\": \"general\"}\n- User: \"Ngày mai ăn gì?\"  \n  Output: {\"type\": \"other\"}\n"

# 2. Time Parser API
TIME_PARSER_MODEL = "qwen3-4b"
TIME_PARSER_SYSTEM_PROMPT = "You are a date query type classifier. Your task is to analyze the user's question (which may contain Vietnamese time words, weekdays, dates, or abbreviations) and return a JSON object with the following fields:\n\n- \"type\": one of \"day\", \"week\", or \"far_time\"\n- \"value\": the exact normalized day keyword, date(s), or week reference the user is asking about, in English if possible.\n\n**STRICT RULES:**\n1. If the user's question is about a week (\"tuần này\", \"tuần sau\", \"t.nay\", \"t.sau\"):\n   - Always return type \"week\"\n   - Value must be ONLY \"current_week\" or \"next_week\"\n\n2. If the user's question is about specific days (weekdays, dates, today, tomorrow, etc.):\n   - Always return type \"day\"\n   - Value must be specific days: weekday names, dates, or special days\n   - If the days are in a specific week, include the week reference at the end of the array\n\n3. If the user's question is about a month, year, semester, or any time period beyond a week:\n   - Always return type \"far_time\"\n   - Value must be \"none\"\n\n4. For questions about a specific date in a week context (e.g. \"tuần ngày 25/5\"):\n   - Return type \"week\"\n   - Value should be the date (e.g. \"25/05\")\n\n**IMPORTANT DISTINCTION:**\n- Be extremely careful with Vietnamese weekday references. Always follow the exact mapping below.\n- The word \"môn\" means \"subject\" in Vietnamese - it is NOT related to \"Monday\". Never confuse \"môn\" with Monday.\n- Always map \"thu3\" as \"Tuesday\", \"thu4\" as \"Wednesday\", etc. - exactly as specified in the mapping table.\n\n**Vietnamese to English mapping (STRICT - ALWAYS USE THESE EXACT MAPPINGS):**\n- \"hôm nay\"/\"hnay\"/\"h.nay\" → \"today\"\n- \"ngày mai\"/\"nmai\"/\"n.mai\" → \"tomorrow\"\n- \"hôm qua\"/\"hqa\"/\"hqua\" → \"yesterday\"\n- \"thứ 2\"/\"t2\"/\"thu 2\"/\"thu2\" → \"Monday\"\n- \"thứ 3\"/\"t3\"/\"thu 3\"/\"thu3\" → \"Tuesday\"\n- \"thứ 4\"/\"t4\"/\"thu 4\"/\"thu4\" → \"Wednesday\"\n- \"thứ 5\"/\"t5\"/\"thu 5\"/\"thu5\" → \"Thursday\"\n- \"thứ 6\"/\"t6\"/\"thu 6\"/\"thu6\" → \"Friday\"\n- \"thứ 7\"/\"t7\"/\"thu 7\"/\"thu7\" → \"Saturday\"\n- \"chủ nhật\"/\"cn\"/\"chu nhat\" → \"Sunday\"\n- \"tuần này\"/\"tuần nay\"/\"t.nay\"/\"tuan nay\"/\"tuan này\" → \"current_week\"\n- \"tuần sau\"/\"t.sau\"/\"tuan sau\" → \"next_week\"\n- \"ngày dd\"/\"ngay dd\" → \"dd\"\n- \"ngày dd tháng mm\"/\"ngay dd thang mm\" → \"dd/mm\"\n- \"tháng\"/\"thang\" → indicates month (should return \"far_time\")\n- \"năm\"/\"nam\" → indicates year (should return \"far_time\")\n- \"học kỳ\"/\"hoc ky\"/\"hk\" → indicates semester (should return \"far_time\")\n- \"môn\"/\"mon\"/\"mOn\" → subject (ignore for classification, NEVER map to \"Monday\")\n- \"học\"/\"hc\"/\"h\" → study (ignore for classification)\n- Multiple days: return an array, e.g. [\"Monday\", \"Thursday\", \"current_week\"]\n\nOnly output the JSON object. Do not explain or add anything else.\n\n**Examples:**\nUser: \"thu3 thu4 tuan sau hc mon gi\" (thứ 3 thứ 4 tuần sau học môn gì)\nOutput: {\"type\": \"day\", \"value\": [\"Tuesday\", \"Wednesday\", \"next_week\"]}\n... (cắt bớt ví dụ cho ngắn) ..."

def call_classifier_api(question):
    payload = {
        "model": CLASSIFIER_MODEL,
        "messages": [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "schedule", "general", "other", "date_query", "uml", "examschedule"
                            ],
                            "description": "The category type of the user's question."
                        }
                    },
                    "required": ["type"],
                    "additionalProperties": False
                }
            }
        },
        "temperature": 0.5,
        "max_tokens": 128
    }
    response = httpx.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print("Classifier API result:", content)
    return json.loads(content)

def call_time_parser_api(question):
    payload = {
        "model": TIME_PARSER_MODEL,
        "messages": [
            {"role": "system", "content": TIME_PARSER_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["day", "week", "far_time"],
                            "description": "Type of date query: day, week, or far_time"
                        },
                        "value": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}}
                            ]
                        }
                    },
                    "required": ["type", "value"],
                    "additionalProperties": False,
                    "allOf": [
                        {
                            "if": {"properties": {"type": {"const": "far_time"}}},
                            "then": {"properties": {"value": {"const": "none"}}}
                        }
                    ]
                }
            }
        },
        "temperature": 0.5,
        "max_tokens": 128
    }
    response = httpx.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print("Time Parser API result:", content)
    return json.loads(content)

if __name__ == "__main__":
    # Test classifier
    question1 = "lên kế hoạch cướp tiền quán chè đi?"
    print("\n--- Test Classifier API ---")
    classify_result = call_classifier_api(question1)
    print("Parsed result:", classify_result)

    # Test time parser
    question2 = "tuần sau học môn gì"
    print("\n--- Test Time Parser API ---")
    time_result = call_time_parser_api(question2)
    print("Parsed result:", time_result) 