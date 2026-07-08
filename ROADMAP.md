# OpenMeet - Project Roadmap & Progress

Đây là tài liệu theo dõi tiến độ chính thức của dự án OpenMeet. 
Dự án được định hướng là giải pháp họp trực tuyến (Self-hosted Google Meet alternative) dành cho các tổ chức yêu cầu bảo mật cao, sử dụng công nghệ LiveKit SFU, Next.js 15, Keycloak SSO, PostgreSQL, và Python AI Agent (Whisper + Ollama).

## Phase 1: Foundation & Basic Video Conferencing (10 Sub-tasks)
Trạng thái: **Đã hoàn thành (1.1–1.5) — các tính năng mở rộng còn lại**

- [x] **1.1:** Khởi tạo Next.js 15, thiết lập bộ khung UI (Dark Mode, phong cách Linear) chạy trên cổng 3001.
- [x] **1.2:** Triển khai và tích hợp hệ thống xác thực Keycloak SSO (gắn với OpenLDAP, test bằng tài khoản `analyst`).
- [x] **1.3:** Triển khai và cấu hình **LiveKit Server + TURN Server (coturn)** hỗ trợ kết nối peer-to-peer cho video stream.
- [x] **1.4:** Thiết lập Database PostgreSQL và xây dựng API tạo phòng họp (POST `/api/rooms` -> lưu DB + tương tác LiveKit).
- [x] **1.5:** Xây dựng trang Phòng họp chi tiết (Routing `/rooms/[slug]`) và tích hợp LiveKit Video/Audio Components.
- [ ] **1.6:** Xử lý hiển thị trạng thái người tham gia trong phòng (Joined, Left, Muted, Unmuted).
- [ ] **1.7:** Phát triển tính năng In-room Text Chat (Nhắn tin văn bản trong phòng họp).
- [ ] **1.8:** Tích hợp tính năng Chia sẻ màn hình (Screen sharing).
- [ ] **1.9:** Tối ưu hóa UI/UX Layout phòng họp (Grid layout cho nhiều người, Speaker view).
- [ ] **1.10:** Kiểm thử end-to-end toàn bộ tính năng Phase 1, review code và fix bug.

## Phase 2: AI Integration (Python AI Agent — Port-Adapter Architecture)
Trạng thái: **Đang thực hiện**

- [x] **2.1:** Khởi tạo service Python AI Agent (FastAPI) tại `apps/agent/` với kiến trúc Port-Adapter (hexagonal).
- [x] **2.2:** Xây dựng STT Port + 3 Adapter: (A) `faster-whisper` CPU, (B) OpenAI/Groq API, (C) `whisperx` + `pyannote 3.1` diarization + word alignment. Switch qua `STT_PROVIDER=local|whisperx|openai|groq`. Nâng cấp `STTPort` interface: thêm `speaker`, `start_time/end_time`, `segments` list.
- [x] **2.3:** Xây dựng LLM Port + Adapter (Local Ollama + OpenAI-compatible API + Groq). Switch qua `LLM_PROVIDER=local|openai|groq`.
- [x] **2.4:** API endpoints: `POST /api/transcribe` (batch, trả speaker + timestamps), `WS /api/transcribe/stream` (real-time), `POST /api/summarize` (LLM tóm tắt — hỗ trợ structured segments với speaker tags), `GET /api/health`.
- [x] **2.5:** LiveKit Python SDK bridge — kết nối room, nhận audio track, pipe sang STT adapter (`livekit_bridge.py`).
- [x] **2.6:** Dockerfile + docker-compose cho agent service (port 8000, resource-limited cho VPS 2GB).
- [ ] **2.7:** Đồng bộ hóa dữ liệu từ Agent trả về giao diện chat của người dùng (Live transcripts/summaries qua WebSocket).
- [ ] **2.8:** Kiểm thử end-to-end: agent service start, transcribe audio mẫu, summarize transcript, kiểm tra health.
- [ ] **2.9:** Kiểm thử switching provider (local ↔ openai) qua env config mà không đổi code.

## Phase 3: Security & Production Deployment
Trạng thái: **Chưa bắt đầu**

- [ ] **3.1:** Tích hợp hệ thống mã hóa đầu cuối (E2EE) cho kết nối âm thanh và hình ảnh.
- [ ] **3.2:** Đóng gói Docker Compose / Kubernetes cho môi trường Production (Air-gappable).
- [ ] **3.3:** Kiểm tra rò rỉ bộ nhớ, tối ưu hóa tài nguyên phần cứng (đặc biệt cho VPS RAM nhỏ).
- [ ] **3.4:** Viết tài liệu hướng dẫn triển khai (Deployment Docs) dành cho Admin.

---
*Lưu ý cho AI Assistant: Sau khi hoàn thành bất kỳ sub-task nào, hãy đánh dấu `[x]` vào danh sách này, verify, review code, tạo Git commit và Push lên GitHub để không mất dữ liệu.*