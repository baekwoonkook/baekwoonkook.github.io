#!/usr/bin/env python3
"""
메리 스튜어트 낭독 원고(mary-stuart-audio.md)를 음성 파일(mp3)로 변환한다.

지원 엔진:
  - elevenlabs : ElevenLabs TTS (가장 자연스러운 다국어 음성)
  - google     : Google Cloud Text-to-Speech (한국어 뉴럴 음성)

사용 예:
  # 1) 의존 패키지 설치
  pip install -r tts/requirements.txt

  # 2-a) ElevenLabs 사용
  export ELEVENLABS_API_KEY="발급받은_키"
  python tts/synthesize.py --provider elevenlabs --out mary-stuart.mp3

  # 2-b) Google Cloud 사용 (서비스 계정 JSON 경로 지정)
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
  python tts/synthesize.py --provider google --out mary-stuart.mp3

옵션:
  --input     원고 경로 (기본: mary-stuart-audio.md)
  --voice     음성 ID/이름 (엔진 기본값 사용하려면 생략)
  --speed     말하기 속도 배율 (기본 0.95 = 살짝 느리게)
"""

import argparse
import os
import sys
import time
from pathlib import Path

# API 한 번에 보낼 수 있는 대략적 글자 제한(여유분 포함)
CHUNK_LIMIT = 1600


def read_paragraphs(path: Path) -> list[str]:
    """원고를 문단 단위로 읽는다(빈 줄 기준)."""
    text = path.read_text(encoding="utf-8")
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paras


def chunk_text(paragraphs: list[str], limit: int = CHUNK_LIMIT) -> list[str]:
    """문단을 합쳐 limit 글자 이하의 덩어리로 묶는다(문장 경계 유지)."""
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        candidate = (buf + "\n\n" + para).strip() if buf else para
        if len(candidate) <= limit:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            # 한 문단이 limit보다 길면 마침표 기준으로 다시 쪼갠다
            if len(para) > limit:
                sentence = ""
                for token in para.replace(". ", ".|").split("|"):
                    cand2 = (sentence + " " + token).strip() if sentence else token
                    if len(cand2) <= limit:
                        sentence = cand2
                    else:
                        if sentence:
                            chunks.append(sentence)
                        sentence = token
                buf = sentence
            else:
                buf = para
    if buf:
        chunks.append(buf)
    return chunks


def synth_elevenlabs(chunks: list[str], voice: str | None, speed: float) -> bytes:
    """ElevenLabs로 각 덩어리를 합성해 하나의 mp3 바이트로 잇는다."""
    import requests

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("환경변수 ELEVENLABS_API_KEY 가 필요합니다.")
    # 기본 음성: 차분한 내레이션용. 원하는 음성 ID로 --voice 지정 가능.
    voice_id = voice or "pNInz6obpgDQGcFmaJgB"  # 예시: 안정적인 남성 보이스
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    audio = bytearray()
    for i, chunk in enumerate(chunks, 1):
        payload = {
            "text": chunk,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.75,
                "style": 0.25,
                "speed": speed,
            },
        }
        print(f"  [{i}/{len(chunks)}] ElevenLabs 합성 중... ({len(chunk)}자)")
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        if resp.status_code != 200:
            sys.exit(f"ElevenLabs 오류 {resp.status_code}: {resp.text[:300]}")
        audio.extend(resp.content)
        time.sleep(0.3)  # 레이트리밋 여유
    return bytes(audio)


def synth_google(chunks: list[str], voice: str | None, speed: float) -> bytes:
    """Google Cloud TTS로 각 덩어리를 합성해 하나의 mp3 바이트로 잇는다."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()
    voice_name = voice or "ko-KR-Neural2-C"  # 차분한 한국어 남성 뉴럴 음성
    voice_params = texttospeech.VoiceSelectionParams(
        language_code="ko-KR", name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speed,
        pitch=-1.0,  # 살짝 낮게 — 비장한 톤
    )

    audio = bytearray()
    for i, chunk in enumerate(chunks, 1):
        print(f"  [{i}/{len(chunks)}] Google TTS 합성 중... ({len(chunk)}자)")
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        resp = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )
        audio.extend(resp.audio_content)
    return bytes(audio)


def main() -> None:
    parser = argparse.ArgumentParser(description="메리 스튜어트 낭독 원고 → mp3")
    parser.add_argument("--provider", choices=["elevenlabs", "google"], required=True)
    parser.add_argument("--input", default="mary-stuart-audio.md")
    parser.add_argument("--out", default="mary-stuart.mp3")
    parser.add_argument("--voice", default=None)
    parser.add_argument("--speed", type=float, default=0.95)
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"원고 파일을 찾을 수 없습니다: {src}")

    paragraphs = read_paragraphs(src)
    chunks = chunk_text(paragraphs)
    total_chars = sum(len(c) for c in chunks)
    print(f"원고 {len(paragraphs)}문단 → {len(chunks)}덩어리, 총 {total_chars}자")

    if args.provider == "elevenlabs":
        audio = synth_elevenlabs(chunks, args.voice, args.speed)
    else:
        audio = synth_google(chunks, args.voice, args.speed)

    Path(args.out).write_bytes(audio)
    print(f"\n완료: {args.out} ({len(audio)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
