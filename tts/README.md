# 낭독 원고 → 오디오(mp3) 변환

`mary-stuart-audio.md` 낭독본을 TTS로 음성 파일로 만드는 스크립트입니다.

## 1. 준비

```bash
pip install -r tts/requirements.txt
```

## 2. 엔진 선택해서 실행

### A) ElevenLabs (가장 자연스러운 음성, 추천)

1. https://elevenlabs.io 가입 → 프로필에서 API 키 발급
2. 사용할 음성 ID를 보이스 라이브러리에서 복사 (생략 시 기본 음성)

```bash
export ELEVENLABS_API_KEY="발급받은_키"
python tts/synthesize.py --provider elevenlabs --out mary-stuart.mp3
# 음성·속도 지정 예:
python tts/synthesize.py --provider elevenlabs --voice <VOICE_ID> --speed 0.9
```

### B) Google Cloud Text-to-Speech

1. Google Cloud 콘솔에서 Text-to-Speech API 활성화
2. 서비스 계정 키(JSON) 발급 후 경로 지정

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
python tts/synthesize.py --provider google --out mary-stuart.mp3
# 한국어 음성 바꾸기 예: ko-KR-Neural2-A(여성) / -C(남성)
python tts/synthesize.py --provider google --voice ko-KR-Neural2-A
```

## 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--provider` | `elevenlabs` 또는 `google` | (필수) |
| `--input` | 원고 경로 | `mary-stuart-audio.md` |
| `--out` | 출력 mp3 경로 | `mary-stuart.mp3` |
| `--voice` | 음성 ID/이름 | 엔진별 기본값 |
| `--speed` | 말하기 속도 배율 | `0.95` (살짝 느리게) |

## 동작 방식

- 원고를 빈 줄 기준 문단으로 읽어, API 글자 제한(약 1,600자)에 맞춰
  문장 경계를 지키며 덩어리로 나눕니다.
- 각 덩어리를 합성한 뒤 mp3 바이트를 이어 붙여 하나의 파일로 저장합니다.
- 비장한 역사 내레이션에 맞춰 기본값을 약간 느린 속도·낮은 피치로 잡아두었습니다.

> 참고: mp3 단순 이어붙이기로 합칩니다. 덩어리 사이 이음매가 신경 쓰이면
> `pydub` + `ffmpeg`로 페이드/무음 삽입 후 합치도록 확장할 수 있습니다.
