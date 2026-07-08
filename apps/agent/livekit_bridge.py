"""
LiveKit Audio Track Integration
Kết nối vào phòng LiveKit, nhận audio track, pipe sang STT adapter.

Sử dụng LiveKit Python SDK (livekit-protocol + livekit-api).
Pipeline: LiveKit Room → Audio Track → STT Adapter → Transcription
"""

import os
import logging
import asyncio
from typing import Optional

from ports.stt_port import STTPort, TranscriptionResult

logger = logging.getLogger(__name__)

# Lazy import LiveKit — chỉ load khi thực sự dùng
try:
    from livekit import api, rtc
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    logger.warning("LiveKit Python SDK not installed. Install with: pip install livekit")


class LiveKitAudioBridge:
    """
    Bridge: kết nối vào LiveKit room, nhận audio track, forward sang STT adapter.

    Flow:
    1. Tạo LiveKit token cho agent participant
    2. Connect room
    3. Subscribe audio tracks từ participants khác
    4. Stream audio → STT adapter
    5. Forward transcription qua callback cho frontend
    """

    def __init__(
        self,
        stt_adapter: STTPort,
        livekit_url: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
    ):
        if not LIVEKIT_AVAILABLE:
            raise ImportError(
                "LiveKit Python SDK not installed. Run: pip install livekit"
            )

        self.stt = stt_adapter
        self.livekit_url = livekit_url or os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        self.api_key = api_key or os.getenv("LIVEKIT_API_KEY", "devkey")
        self.api_secret = api_secret or os.getenv("LIVEKIT_API_SECRET", "")
        self._room: Optional["rtc.Room"] = None
        self._running = False

    async def connect_to_room(self, room_name: str, participant_identity: str = "ai-agent"):
        """
        Tạo token và connect vào LiveKit room.

        Args:
            room_name: Tên phòng LiveKit
            participant_identity: Identity của agent participant
        """
        # Tạo access token
        token = (
            api.AccessToken(self.api_key, self.api_secret)
            .with_identity(participant_identity)
            .with_name("OpenMeet AI Agent")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=False,      # Agent không publish video/audio
                can_subscribe=True,     # Subscribe audio từ participants
            ))
            .to_jwt()
        )

        self._room = rtc.Room()

        # Event: participant joined
        @self._room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")
            # Subscribe tất cả audio tracks
            for pub in participant.track_publications.values():
                if pub.kind == rtc.TrackKind.KIND_AUDIO:
                    logger.info(f"Subscribing to audio track from {participant.identity}")

        # Event: track received
        @self._room.on("track_received")
        def on_track_received(track: rtc.Track, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                logger.info(f"Audio track received from {participant.identity}")
                # Tạo AudioStream và pipe sang STT
                asyncio.create_task(self._handle_audio_track(track, participant.identity))

        # Connect
        await self._room.connect(self.livekit_url, token)
        logger.info(f"Connected to LiveKit room: {room_name}")

        # Subscribe existing participants
        for participant in self._room.remote_participants.values():
            for pub in participant.track_publications.values():
                if pub.kind == rtc.TrackKind.KIND_AUDIO and pub.track:
                    asyncio.create_task(self._handle_audio_track(pub.track, participant.identity))

    async def _handle_audio_track(self, track: rtc.Track, participant_identity: str):
        """
        Nhận audio frames từ LiveKit track, convert sang PCM, pipe sang STT.
        """
        audio_stream = rtc.AudioStream(track)
        on_transcription = self._on_transcription_callback

        async def audio_chunk_generator():
            """Yield PCM bytes từ LiveKit AudioFrame."""
            async for frame in audio_stream:
                # frame: AudioFrame (PCM 16-bit signed, interleaved)
                yield bytes(frame.data)

        try:
            async for result in self.stt.transcribe_stream(audio_chunk_generator(), language="vi"):
                if on_transcription:
                    await on_transcription(participant_identity, result)
        except Exception as e:
            logger.error(f"Audio track handler error ({participant_identity}): {e}")

    def on_transcription(self, callback):
        """
        Register callback nhận transcription.

        Callback signature: async def callback(identity: str, result: TranscriptionResult)
        """
        self._on_transcription_callback = callback

    _on_transcription_callback = None

    async def disconnect(self):
        """Disconnect khỏi room."""
        self._running = False
        if self._room:
            await self._room.disconnect()
            logger.info("Disconnected from LiveKit room.")
