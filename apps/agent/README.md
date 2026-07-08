# OpenMeet AI Agent

Python AI Agent service cho OpenMeet — nhận diện giọng nói (STT) và tóm tắt nội dung (LLM) theo thời gian thực.

## Kiến trúc Port-Adapter

```
                    ┌─────────────────────────────────┐
                    │         FastAPI Server           │
                    │   /transcribe  /summarize  /health │
                    └──────────┬──────────┬───────────┘
                               │          │
                    ┌──────────▼──┐  ┌────▼─────┐
                    │  STT Port   │  │  LLM Port │
                    │  (Protocol) │  │ (Protocol) │
                    └──────┬──────┘  └─────┬─────┘
                           │               │
              ┌────────────┴──────┐ ┌─────┴──────────┐
              │                   │ │                │
     ┌────────▼───────┐ ┌────────▼┐ ┌─▼──────────┐ ┌──▼─────────┐
     │ LocalWhisper    │ │ OpenAI  │ │ LocalOllama│ │ OpenAI     │
     │   Adapter       │ │   STT   │ │  Adapter   │ │   LLM      │
     │ (faster-whisper)│ │ Adapter │ │(ollama API) │ │ Adapter    │
     └────────────────┘ └─────────┘ └────────────┘ └────────────┘
```

## Cấu hình

Trong file `.env`:

```bash
# Provider selection: "local" hoặc "openai"
STT_PROVIDER=local          # local | openai
LLM_PROVIDER=openai         # local | openai

# Local STT (Whisper)
WHISPER_MODEL=base          # tiny | base | small | medium | large-v3

# OpenAI-compatible STT
OPENAI_STT_API_KEY=sk-xxx
OPENAI_STT_BASE_URL=https://api.openai.com/v1
OPENAI_STT_MODEL=whisper-1

# Local LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# OpenAI-compatible LLM
OPENAI_LLM_API_KEY=sk-xxx
OPENAI_LLM_BASE_URL=https://api.openai.com/v1
OPENAI_LLM_MODEL=gpt-4o-mini

# LiveKit
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=openmeet-livekit-secret-very-long-string-for-security-12345
```

## Chạy

```bash
# Local dev
cd apps/agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Docker
docker compose -f infra/agent/docker-compose.yml up -d
```
