# OpenMeet - Self-Hosted Video Conferencing & AI Agent

OpenMeet là giải pháp họp trực tuyến mã nguồn mở, được thiết kế để tự lưu trữ (self-hosted), dành cho các tổ chức yêu cầu bảo mật cao. Hệ thống là giải pháp thay thế cho Google Meet, kết hợp với AI Agent On-premise để tự động tạo phụ đề (STT) và tóm tắt biên bản cuộc họp.

## Công Nghệ Cốt Lõi
- **Web App:** Next.js 15, Tailwind CSS, Prisma.
- **Xác thực:** Keycloak SSO + OpenLDAP.
- **Video/Audio:** LiveKit (WebRTC SFU).
- **Cơ sở dữ liệu:** PostgreSQL.
- **AI Agent:** FastAPI (Python), kiến trúc Port-Adapter (Hỗ trợ Faster-Whisper, WhisperX có Diarization, và OpenAI-compatible API).

---

## Yêu Cầu Hệ Thống (Prerequisites)
1. **Git**
2. **Docker & Docker Compose** (để chạy Backend: DB, Keycloak, LDAP, LiveKit, AI Agent)
3. **Node.js (>= 20.x)** & **npm** (để chạy Next.js Web App)
4. *(Tùy chọn)* **PM2** nếu muốn chạy Web trong background.

---

## Hướng Dẫn Setup & Chạy Dự Án

### Bước 1: Clone Mã Nguồn
```bash
git clone https://github.com/hothai19o5/openmeet.git
cd openmeet
```

### Bước 2: Thiết Lập Biến Môi Trường (Environment Variables)
Hệ thống yêu cầu các file `.env` chứa mật khẩu và API Key. (Các file này không được push lên git để bảo mật).

**2.1. Biến môi trường cho Web App (Next.js)**
Tạo file `apps/web/.env`:
```ini
# Database
DATABASE_URL="postgresql://openmeet:[REDACTED_PASSWORD]@localhost:5432/openmeet?schema=public"

# NextAuth (Keycloak)
NEXTAUTH_URL="http://localhost:3001"
NEXTAUTH_SECRET="[REDACTED_SECRET]"
KEYCLOAK_CLIENT_ID="openmeet-web"
KEYCLOAK_CLIENT_SECRET="[REDACTED_SECRET]"
KEYCLOAK_ISSUER="http://localhost:8080/realms/openmeet"

# LiveKit
NEXT_PUBLIC_LIVEKIT_URL="ws://localhost:7880"
LIVEKIT_API_KEY="[REDACTED_API_KEY]"
LIVEKIT_API_SECRET="[REDACTED_SECRET]"
```

**2.2. Biến môi trường cho AI Agent (Python)**
Tạo file `apps/agent/.env` (tham khảo file `.env.example` có sẵn trong thư mục đó):
```bash
cd apps/agent
cp .env.example .env
```
Thiết lập `STT_PROVIDER=local` (hoặc `openai` / `whisperx`).

---

### Bước 3: Khởi Động Hạ Tầng Backend (Docker)
Mở terminal, chạy lần lượt các file Docker Compose trong thư mục `infra/`:

```bash
cd infra

# 1. Khởi động LDAP (Dữ liệu người dùng cơ sở)
docker compose -f ldap/docker-compose.yml up -d

# 2. Khởi động Keycloak & PostgreSQL Database
docker compose -f keycloak/docker-compose.yml up -d

# 3. Khởi động LiveKit Server & Redis (WebRTC cho Video Call)
docker compose -f livekit/docker-compose.yml up -d

# 4. Khởi động AI Agent (Tóm tắt & STT)
docker compose -f agent/docker-compose.yml up -d
```
*(Chạy `docker ps` để đảm bảo tất cả container đang ở trạng thái `Up`).*

---

### Bước 4: Setup Cơ Sở Dữ Liệu & Prisma (Web App)
Đẩy schema cấu trúc dữ liệu của Web App vào PostgreSQL:
```bash
cd ../apps/web
npm install

# Push schema vào database
npx prisma db push

# Generate Prisma Client
npx prisma generate
```

---

### Bước 5: Chạy Ứng Dụng Web (Next.js)

**Chạy Development:**
```bash
npm run dev -- -p 3001
```
Web sẽ chạy tại `http://localhost:3001`.

**Chạy Production (khuyên dùng pm2):**
```bash
npm run build
pm2 start npm --name "openmeet-web" -- start -- -p 3001
```

---

### Bước 6: Đăng Nhập & Bắt Đầu
1. Mở trình duyệt, truy cập: **`http://localhost:3001`**
2. Nhấn Sign In, hệ thống redirect qua Keycloak.
3. Đăng nhập bằng tài khoản mẫu:
   - **Username:** `analyst`
   - **Password:** `[REDACTED_PASSWORD]`
4. Tạo phòng họp mới và trải nghiệm!

*(Lưu ý: Nếu public qua IP/Domain ngoài Internet, hãy mở các port Firewall: 3001, 8080, 7880, và dải 50000-60000/udp cho LiveKit).*