# OpenMeet - Project Roadmap & Progress

Đây là tài liệu theo dõi tiến độ chính thức của dự án OpenMeet. 
Dự án được định hướng là giải pháp họp trực tuyến (Self-hosted Google Meet alternative) dành cho các tổ chức yêu cầu bảo mật cao, sử dụng công nghệ LiveKit SFU, Next.js 15, Keycloak SSO, PostgreSQL, và Python AI Agent (Whisper + Ollama).

## Phase 1: Foundation & Basic Video Conferencing (10 Sub-tasks)
Trạng thái: **Đang thực hiện**

- [x] **1.1:** Khởi tạo Next.js 15, thiết lập bộ khung UI (Dark Mode, phong cách Linear) chạy trên cổng 3001.
- [x] **1.2:** Triển khai và tích hợp hệ thống xác thực Keycloak SSO (gắn với OpenLDAP, test bằng tài khoản `analyst`).
- [ ] **1.3:** Triển khai và cấu hình **LiveKit Server + TURN Server (coturn)** hỗ trợ kết nối peer-to-peer cho video stream.
- [ ] **1.4:** Thiết lập Database PostgreSQL và xây dựng API tạo phòng họp (POST `/api/rooms` -> lưu DB + tương tác LiveKit).
- [ ] **1.5:** Xây dựng trang Phòng họp chi tiết (Routing `/rooms/[slug]`) và tích hợp LiveKit Video/Audio Components.
- [ ] **1.6:** Xử lý hiển thị trạng thái người tham gia trong phòng (Joined, Left, Muted, Unmuted).
- [ ] **1.7:** Phát triển tính năng In-room Text Chat (Nhắn tin văn bản trong phòng họp).
- [ ] **1.8:** Tích hợp tính năng Chia sẻ màn hình (Screen sharing).
- [ ] **1.9:** Tối ưu hóa UI/UX Layout phòng họp (Grid layout cho nhiều người, Speaker view).
- [ ] **1.10:** Kiểm thử end-to-end toàn bộ tính năng Phase 1, review code và fix bug.

## Phase 2: AI Integration (Python AI Agent)
Trạng thái: **Chưa bắt đầu**

- [ ] **2.1:** Khởi tạo service Python AI Agent (FastAPI / thư viện LiveKit Python).
- [ ] **2.2:** Tích hợp mô hình Whisper để nhận diện giọng nói (Speech-to-Text) theo thời gian thực.
- [ ] **2.3:** Tích hợp Ollama (Local LLM) để tóm tắt nội dung cuộc họp hoặc ra lệnh trợ lý ảo.
- [ ] **2.4:** Đồng bộ hóa dữ liệu từ Agent trả về giao diện chat của người dùng (Live transcripts/summaries).

## Phase 3: Security & Production Deployment
Trạng thái: **Chưa bắt đầu**

- [ ] **3.1:** Tích hợp hệ thống mã hóa đầu cuối (E2EE) cho kết nối âm thanh và hình ảnh.
- [ ] **3.2:** Đóng gói Docker Compose / Kubernetes cho môi trường Production (Air-gappable).
- [ ] **3.3:** Kiểm tra rò rỉ bộ nhớ, tối ưu hóa tài nguyên phần cứng (đặc biệt cho VPS RAM nhỏ).
- [ ] **3.4:** Viết tài liệu hướng dẫn triển khai (Deployment Docs) dành cho Admin.

---
*Lưu ý cho AI Assistant: Sau khi hoàn thành bất kỳ sub-task nào, hãy đánh dấu `[x]` vào danh sách này, verify, review code, tạo Git commit và Push lên GitHub để không mất dữ liệu.*