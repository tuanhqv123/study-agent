# API Documentation

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication](#2-authentication)
3. [File Management APIs](#3-file-management-apis)
4. [Chat APIs](#4-chat-apis)
5. [PTIT Integration APIs](#5-ptit-integration-apis)
6. [User Management APIs](#6-user-management-apis)
7. [Error Handling](#7-error-handling)
8. [Rate Limiting](#8-rate-limiting)

## 1. API Overview

The Study Assistant API follows REST principles with JSON request/response format. All endpoints are prefixed with `/api/v1/`.

### 1.1 Base Configuration

**Base URL:** `https://api.studyassistant.ptit.edu.vn/api/v1/`  
**Content-Type:** `application/json`  
**Authentication:** Bearer JWT tokens  
**Rate Limiting:** Per-endpoint limits (see [Rate Limiting](#8-rate-limiting))

### 1.2 Common Response Format

```json
{
  "success": true|false,
  "data": {...} | [...],
  "message": "Human-readable message",
  "errors": [...], // Present only on error
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 1.3 HTTP Status Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request / Validation error
- `401` - Unauthorized / Invalid token
- `403` - Forbidden / Insufficient permissions
- `404` - Resource not found
- `429` - Rate limit exceeded
- `500` - Internal server error

## 2. Authentication

### 2.1 User Registration

**Endpoint:** `POST /auth/register`

**Request:**

```json
{
  "email": "student@ptit.edu.vn",
  "password": "SecurePassword123!",
  "full_name": "Nguyễn Văn A",
  "student_id": "B21DCAT001" // Optional
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "student@ptit.edu.vn",
      "full_name": "Nguyễn Văn A",
      "student_id": "B21DCAT001",
      "created_at": "2024-12-15T10:30:00Z"
    },
    "access_token": "jwt-token-here",
    "refresh_token": "refresh-token-here",
    "expires_in": 3600
  },
  "message": "Đăng ký thành công"
}
```

### 2.2 User Login

**Endpoint:** `POST /auth/login`

**Request:**

```json
{
  "email": "student@ptit.edu.vn",
  "password": "SecurePassword123!"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "student@ptit.edu.vn",
      "full_name": "Nguyễn Văn A"
    },
    "access_token": "jwt-token-here",
    "refresh_token": "refresh-token-here",
    "expires_in": 3600
  },
  "message": "Đăng nhập thành công"
}
```

### 2.3 Token Refresh

**Endpoint:** `POST /auth/refresh`

**Request:**

```json
{
  "refresh_token": "refresh-token-here"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "new-jwt-token",
    "expires_in": 3600
  }
}
```

### 2.4 Logout

**Endpoint:** `POST /auth/logout`  
**Authentication:** Required

**Request:** Empty body

**Response:**

```json
{
  "success": true,
  "message": "Đăng xuất thành công"
}
```

## 3. File Management APIs

### 3.1 Upload File

**Endpoint:** `POST /files/upload`  
**Authentication:** Required  
**Content-Type:** `multipart/form-data`

**Request:**

```
file: <PDF file>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "file": {
      "id": "uuid-here",
      "filename": "Lecture-Notes-Chapter1.pdf",
      "file_size": 2048576,
      "file_type": "application/pdf",
      "upload_date": "2024-12-15T10:30:00Z",
      "processing_status": "processing"
    }
  },
  "message": "File uploaded successfully. Processing in background."
}
```

**File Constraints:**

- **Maximum size:** 10MB
- **Supported formats:** PDF, DOC, DOCX, TXT
- **Rate limit:** 10 files per hour

### 3.2 Get File List

**Endpoint:** `GET /files`  
**Authentication:** Required

**Query Parameters:**

- `page` (integer, default: 1) - Page number
- `limit` (integer, default: 20, max: 100) - Items per page
- `status` (string) - Filter by processing status: `processing`, `completed`, `failed`

**Response:**

```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "uuid-here",
        "filename": "Lecture-Notes-Chapter1.pdf",
        "file_size": 2048576,
        "file_type": "application/pdf",
        "upload_date": "2024-12-15T10:30:00Z",
        "processing_status": "completed",
        "chunk_count": 15
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 45,
      "items_per_page": 20
    }
  }
}
```

### 3.3 Get File Details

**Endpoint:** `GET /files/{file_id}`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "data": {
    "file": {
      "id": "uuid-here",
      "filename": "Lecture-Notes-Chapter1.pdf",
      "file_size": 2048576,
      "file_type": "application/pdf",
      "upload_date": "2024-12-15T10:30:00Z",
      "processing_status": "completed",
      "chunk_count": 15,
      "processing_time": 45.2,
      "extracted_text_preview": "Chapter 1: Introduction to Computer Science..."
    }
  }
}
```

### 3.4 Delete File

**Endpoint:** `DELETE /files/{file_id}`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### 3.5 Get File Processing Status

**Endpoint:** `GET /files/{file_id}/status`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "data": {
    "file_id": "uuid-here",
    "status": "processing", // processing, completed, failed
    "progress": 75, // Percentage (0-100)
    "estimated_time_remaining": 30, // Seconds
    "error_message": null // Present if status is 'failed'
  }
}
```

## 4. Chat APIs

### 4.1 Send Chat Message

**Endpoint:** `POST /chat/message`  
**Authentication:** Required

**Request:**

```json
{
  "message": "Hãy giải thích khái niệm OOP trong Java",
  "chat_session_id": "uuid-here" // Optional, creates new session if not provided
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "response": {
      "id": "uuid-here",
      "message": "Object-Oriented Programming (OOP) trong Java là...",
      "timestamp": "2024-12-15T10:30:00Z",
      "response_time": 2.3,
      "context_used": [
        {
          "source_file": "Java-OOP-Concepts.pdf",
          "chunk_text": "OOP is a programming paradigm...",
          "relevance_score": 0.89
        }
      ],
      "query_type": "document_query"
    },
    "chat_session": {
      "id": "uuid-here",
      "created_at": "2024-12-15T10:25:00Z",
      "message_count": 3
    }
  }
}
```

### 4.2 Get Chat History

**Endpoint:** `GET /chat/sessions/{session_id}/messages`  
**Authentication:** Required

**Query Parameters:**

- `page` (integer, default: 1)
- `limit` (integer, default: 50, max: 100)

**Response:**

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "uuid-here",
        "type": "user", // user, assistant
        "content": "Hãy giải thích khái niệm OOP",
        "timestamp": "2024-12-15T10:30:00Z"
      },
      {
        "id": "uuid-here",
        "type": "assistant",
        "content": "Object-Oriented Programming là...",
        "timestamp": "2024-12-15T10:30:02Z",
        "context_sources": ["Java-OOP-Concepts.pdf"]
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 2,
      "total_items": 15
    }
  }
}
```

### 4.3 Get Chat Sessions

**Endpoint:** `GET /chat/sessions`  
**Authentication:** Required

**Query Parameters:**

- `page` (integer, default: 1)
- `limit` (integer, default: 20, max: 50)

**Response:**

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid-here",
        "title": "Java OOP Discussion", // Auto-generated from first message
        "created_at": "2024-12-15T10:25:00Z",
        "updated_at": "2024-12-15T10:45:00Z",
        "message_count": 8,
        "last_message_preview": "Cảm ơn bạn đã giải thích..."
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 12
    }
  }
}
```

### 4.4 Delete Chat Session

**Endpoint:** `DELETE /chat/sessions/{session_id}`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "message": "Chat session deleted successfully"
}
```

### 4.5 Update Chat Session Title

**Endpoint:** `PUT /chat/sessions/{session_id}`  
**Authentication:** Required

**Request:**

```json
{
  "title": "Java Programming Discussion"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "session": {
      "id": "uuid-here",
      "title": "Java Programming Discussion",
      "updated_at": "2024-12-15T10:50:00Z"
    }
  }
}
```

## 5. PTIT Integration APIs

### 5.1 Get Class Schedule

**Endpoint:** `GET /ptit/schedule`  
**Authentication:** Required  
**Note:** Requires PTIT account linking

**Query Parameters:**

- `week` (string, optional) - Week in format YYYY-WW (e.g., "2024-50")
- `semester` (string, optional) - Semester code (e.g., "20241")

**Response:**

```json
{
  "success": true,
  "data": {
    "schedule": [
      {
        "subject_code": "IT4043",
        "subject_name": "Lập trình Web",
        "class_code": "IT4043.01",
        "time_slot": "1-3",
        "day_of_week": 2, // 2 = Tuesday
        "room": "TC-205",
        "building": "TC",
        "instructor": "TS. Nguyễn Văn A",
        "start_time": "07:00",
        "end_time": "09:30",
        "date": "2024-12-17"
      }
    ],
    "week_info": {
      "week_number": 50,
      "year": 2024,
      "start_date": "2024-12-16",
      "end_date": "2024-12-22"
    }
  }
}
```

### 5.2 Get Exam Schedule

**Endpoint:** `GET /ptit/exams`  
**Authentication:** Required

**Query Parameters:**

- `semester` (string, optional) - Semester code

**Response:**

```json
{
  "success": true,
  "data": {
    "exams": [
      {
        "subject_code": "IT4043",
        "subject_name": "Lập trình Web",
        "exam_type": "Cuối kỳ", // Giữa kỳ, Cuối kỳ
        "exam_date": "2024-12-20",
        "start_time": "07:30",
        "duration": 90, // Minutes
        "room": "TC-101",
        "building": "TC",
        "seat_number": "25",
        "exam_form": "Trắc nghiệm" // Trắc nghiệm, Tự luận, Thực hành
      }
    ]
  }
}
```

### 5.3 Get Student Information

**Endpoint:** `GET /ptit/student-info`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "data": {
    "student": {
      "student_id": "B21DCAT001",
      "full_name": "Nguyễn Văn A",
      "class": "D21CQAT01-N",
      "major": "Công nghệ thông tin",
      "faculty": "Công nghệ thông tin",
      "academic_year": "2021-2025",
      "current_semester": "20241",
      "gpa": {
        "overall": 3.45,
        "current_semester": 3.2
      }
    }
  }
}
```

### 5.4 Link PTIT Account

**Endpoint:** `POST /ptit/link-account`  
**Authentication:** Required

**Request:**

```json
{
  "ptit_username": "B21DCAT001",
  "ptit_password": "password123"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "linked": true,
    "student_info": {
      "student_id": "B21DCAT001",
      "full_name": "Nguyễn Văn A",
      "class": "D21CQAT01-N"
    }
  },
  "message": "PTIT account linked successfully"
}
```

## 6. User Management APIs

### 6.1 Get User Profile

**Endpoint:** `GET /user/profile`  
**Authentication:** Required

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "student@ptit.edu.vn",
      "full_name": "Nguyễn Văn A",
      "student_id": "B21DCAT001",
      "created_at": "2024-12-15T10:30:00Z",
      "ptit_linked": true,
      "preferences": {
        "language": "vi",
        "theme": "light",
        "notifications": true
      },
      "usage_stats": {
        "total_files": 15,
        "total_chats": 8,
        "total_messages": 234
      }
    }
  }
}
```

### 6.2 Update User Profile

**Endpoint:** `PUT /user/profile`  
**Authentication:** Required

**Request:**

```json
{
  "full_name": "Nguyễn Văn B",
  "preferences": {
    "language": "en",
    "theme": "dark",
    "notifications": false
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "full_name": "Nguyễn Văn B",
      "preferences": {
        "language": "en",
        "theme": "dark",
        "notifications": false
      },
      "updated_at": "2024-12-15T10:50:00Z"
    }
  },
  "message": "Profile updated successfully"
}
```

### 6.3 Change Password

**Endpoint:** `PUT /user/password`  
**Authentication:** Required

**Request:**

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### 6.4 Delete Account

**Endpoint:** `DELETE /user/account`  
**Authentication:** Required

**Request:**

```json
{
  "password": "Password123!",
  "confirmation": "DELETE MY ACCOUNT"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

## 7. Error Handling

### 7.1 Validation Errors

**Status Code:** `400 Bad Request`

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email format is invalid",
      "code": "INVALID_FORMAT"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "code": "MIN_LENGTH"
    }
  ],
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 7.2 Authentication Errors

**Status Code:** `401 Unauthorized`

```json
{
  "success": false,
  "message": "Authentication required",
  "error_code": "TOKEN_EXPIRED",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 7.3 Authorization Errors

**Status Code:** `403 Forbidden`

```json
{
  "success": false,
  "message": "Insufficient permissions to access this resource",
  "error_code": "ACCESS_DENIED",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 7.4 Resource Not Found

**Status Code:** `404 Not Found`

```json
{
  "success": false,
  "message": "Resource not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 7.5 Rate Limit Exceeded

**Status Code:** `429 Too Many Requests`

```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600, // Seconds until reset
  "limit": 10,
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### 7.6 Internal Server Error

**Status Code:** `500 Internal Server Error`

```json
{
  "success": false,
  "message": "An unexpected error occurred",
  "error_code": "INTERNAL_ERROR",
  "request_id": "req_uuid_here", // For debugging
  "timestamp": "2024-12-15T10:30:00Z"
}
```

## 8. Rate Limiting

### 8.1 Rate Limit Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702627800
X-RateLimit-Retry-After: 900
```

### 8.2 Endpoint-Specific Limits

| Endpoint                  | Limit        | Window         |
| ------------------------- | ------------ | -------------- |
| `POST /auth/login`        | 5 requests   | per 15 minutes |
| `POST /files/upload`      | 10 files     | per hour       |
| `POST /chat/message`      | 60 requests  | per minute     |
| `GET /ptit/*`             | 20 requests  | per hour       |
| `POST /ptit/link-account` | 3 attempts   | per hour       |
| All other endpoints       | 100 requests | per minute     |

### 8.3 Rate Limit Bypass

Premium users or special accounts may have higher limits. Contact support for rate limit increases.

---

## SDK Examples

### 8.4 JavaScript/TypeScript Example

```typescript
class StudyAssistantAPI {
  private baseURL = "https://api.studyassistant.ptit.edu.vn/api/v1";
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async sendMessage(message: string, sessionId?: string) {
    const response = await fetch(`${this.baseURL}/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify({
        message,
        chat_session_id: sessionId,
      }),
    });

    return response.json();
  }

  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseURL}/files/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });

    return response.json();
  }
}
```

### 8.5 Python Example

```python
import requests
import json

class StudyAssistantAPI:
    def __init__(self, token: str):
        self.base_url = "https://api.studyassistant.ptit.edu.vn/api/v1"
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def send_message(self, message: str, session_id: str = None):
        payload = {"message": message}
        if session_id:
            payload["chat_session_id"] = session_id

        response = requests.post(
            f"{self.base_url}/chat/message",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def upload_file(self, file_path: str):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/files/upload",
                headers=headers,
                files=files
            )
        return response.json()
```

---

## Conclusion

This API documentation provides comprehensive coverage of all Study Assistant endpoints. For additional support or feature requests, please contact the development team.

→ **Related Documentation:**

- [Backend Architecture](./backend-architecture.md) - System design and implementation details
- [Database Design](./database-design.md) - Data models and relationships
- [Security Report](./security-report.md) - Security considerations and best practices
