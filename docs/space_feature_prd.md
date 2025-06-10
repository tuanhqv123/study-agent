# Space Feature PRD

## 1. Overview

**Spaces** are collaborative containers where users can group chat sessions around shared knowledge. Each Space maintains:

- A library of knowledge artifacts (uploaded files, notes, external links)
- A set of chat sessions that all share the same context
- Custom space-level prompt / system instructions

Users can create, join, and manage multiple Spaces. Within each Space, all AI chats automatically incorporate Space knowledge (vector search + embeddings) plus space-specific system prompt.

## 2. Goals & Success Metrics

- Enable users to organize conversations by topic, course, or project
- Provide consistent context across all sessions in a Space
- Allow custom space prompts to steer AI behavior

**Metrics:**

- % of active users creating ≥1 Space
- Average number of chat sessions per Space
- Engagement: messages per session in Spaces vs. free chat
- Retrieval accuracy: vector search hit rate within Spaces

## 3. User Personas

- **Student**: organizes study materials by course (Math Space, History Space)
- **Researcher**: groups literature review chats under Research Space
- **Instructor**: shares knowledge (syllabus, lecture notes) with student Space

## 4. User Stories

1. **Create Space**: As a user, I want to create a new Space with a name and description so I can group related chats.
2. **Upload Knowledge**: As a user, I want to upload files or links into my Space so that AI can reference them.
3. **Custom Prompt**: As a user, I want to define a custom system prompt for my Space to tailor AI tone and behavior.
4. **New Chat in Space**: As a user, I want to start multiple chat sessions within a Space, each inheriting Space context automatically.
5. **Switch Space**: As a user, I want to switch between Spaces and see their chat sessions and knowledge library.
6. **Delete Space**: As a user, I want to delete a Space and all its sessions/knowledge when no longer needed.

## 5. Functional Requirements

- **Space Management**
  - Create, rename, delete Spaces
  - List all Spaces for current user
- **Knowledge Library**
  - Upload PDF/text files into a Space
  - Add metadata (title, tags)
  - Remove knowledge artifacts
  - Vectorize and index artifacts on upload
- **Space Prompt**
  - UI to edit custom system prompt per Space
  - Validate prompt length ≤ 1000 chars
- **Chat Sessions**
  - Endpoint to create new session scoped to a Space
  - List and navigate sessions within a Space
  - Inherit Space prompt and knowledge context in chat payload

## 6. Data Model

- `spaces` table: id, user_id, name, description, prompt, created_at
- `space_knowledge` table: id, space_id, type (file/link), metadata, embedding_vector, created_at
- `chat_sessions` extend: add `space_id` column (nullable for free chat)

## 7. API Design

### Space Endpoints (`/api/spaces`)

- `POST /spaces` → create Space
- `GET /spaces` → list user Spaces
- `GET /spaces/{id}` → fetch Space details (incl. prompt)
- `PUT /spaces/{id}` → update name/description/prompt
- `DELETE /spaces/{id}` → delete Space, cascades sessions & knowledge

### Knowledge Endpoints (`/api/spaces/{id}/knowledge`)

- `POST` → upload file or submit link (multipart/form-data)
- `GET` → list knowledge
- `DELETE /knowledge/{id}` → remove artifact

### Chat Endpoints (enhance `/chat`)

- `POST /chat` add optional `space_id` param
- If `space_id` present, load space prompt + knowledge chunks before classification & AI call

## 8. UI / UX Changes

- **Sidebar**: list Spaces with creation button
- **Space View**: tabs for "Chats" and "Knowledge"
- **Knowledge tab**: file upload UI + list of artifacts
- **Custom Prompt**: editor field under Space settings
- **ChatInput**: include hidden `space_id` in payload

## 9. Technical Considerations

- Embeddings storage per Space in Supabase vector index
- Authentication & authorization: ensure only owner sees/manages their Spaces
- Pagination for large knowledge libraries
- Migration: existing chat_sessions → add null-safe `space_id`

## 10. Timeline & Milestones

- Week 1: Data model & API scaffolding
- Week 2: Knowledge upload & indexing
- Week 3: Space CRUD + custom prompt UI
- Week 4: Chat integration + testing
- Week 5: Polish, QA, docs

## 11. Risks & Mitigations

- Large file upload → enforce size limits & chunking
- Prompt abuse → sanitize user-defined system prompts
- Vector index growth → paginate & garbage-collect unused artifacts

---

_Prepared by Product Team, June 2025_
