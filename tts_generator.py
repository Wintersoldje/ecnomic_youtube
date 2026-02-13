"""
🎙️ TTS(음성) 생성 모듈
- gTTS (Google Text-to-Speech, 완전 무료)를 사용해 한국어 음성을 생성합니다.
- 숏츠용: 속도 1.3배속으로 빠르게
- 롱폼용: 자연스러운 속도 + 문단 사이 쉬는 시간 포함
"""

import os
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import time

from ffmpeg_utils import configure_pydub_ffmpeg


configure_pydub_ffmpeg()


def create_silence(duration_ms):
    """무음 오디오 생성 (쉬는 시간)"""
    return AudioSegment.silent(duration=duration_ms)


def text_to_speech_part(text, speed_up=False):
    """
    텍스트 하나를 음성 파일로 변환
    speed_up=True: 숏츠용 빠른 속도
    """
    tts = gTTS(text=text, lang='ko', slow=False)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tmp.name)
    tmp.close()

    audio = AudioSegment.from_mp3(tmp.name)
    os.unlink(tmp.name)

    if speed_up:
        # 숏츠: 1.3배속 (빠르게)
        audio = speed_change(audio, 1.3)

    return audio


def speed_change(audio, speed=1.3):
    """
    오디오 속도 변경 (pydub 방식)
    음정은 유지하면서 속도만 빠르게
    """
    # pydub로 속도 변경 (프레임 레이트 조정 방식)
    new_frame_rate = int(audio.frame_rate * speed)
    fast_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": new_frame_rate
    })
    # 다시 원래 frame_rate로 변환 (음정 보정)
    return fast_audio.set_frame_rate(audio.frame_rate)


def generate_tts(scripts):
    """
    숏츠와 롱폼 음성 파일을 생성합니다.
    
    Returns: {
        "shorts": "output/audio_shorts.mp3",
        "longform": "output/audio_longform.mp3",
        "shorts_timings": [...],    # 각 파트의 시작/종료 시간 (자막 싱크용)
        "longform_timings": [...]
    }
    """
    os.makedirs("output", exist_ok=True)

    shorts_script = scripts["shorts"]
    longform_script = scripts["longform"]

    # 숏츠 음성 생성 (1.3배속)
    print("  🎙️  숏츠 음성 생성 중 (빠른 속도)...")
    shorts_audio, shorts_timings = build_audio_track(shorts_script, speed_up=True)
    shorts_path = "output/audio_shorts.mp3"
    shorts_audio.export(shorts_path, format="mp3")
    print(f"     → 숏츠 음성: {shorts_path} ({len(shorts_audio)/1000:.1f}초)")

    # 쿨다운 (Google TTS 요청 제한 방지)
    time.sleep(2)

    # 롱폼 음성 생성 (자연스러운 속도)
    print("  🎙️  롱폼 음성 생성 중 (자연스러운 속도)...")
    longform_audio, longform_timings = build_audio_track(longform_script, speed_up=False)
    longform_path = "output/audio_longform.mp3"
    longform_audio.export(longform_path, format="mp3")
    print(f"     → 롱폼 음성: {longform_path} ({len(longform_audio)/1000:.1f}초)")

    return {
        "shorts": shorts_path,
        "longform": longform_path,
        "shorts_timings": shorts_timings,
        "longform_timings": longform_timings
    }


def build_audio_track(script_parts, speed_up=False):
    """
    스크립트 파트 목록을 받아 하나의 오디오 트랙으로 합칩니다.
    각 파트 사이에 쉬는 시간(pause)을 추가합니다.
    
    Returns: (AudioSegment, timings_list)
    timings: [{start_ms, end_ms, subtitle}, ...]
    """
    combined = AudioSegment.empty()
    timings = []

    for i, part in enumerate(script_parts):
        text = part.get("text", "")
        pause_sec = part.get("pause", 0.5)
        subtitle = part.get("subtitle", "")

        if not text.strip():
            continue

        try:
            # 음성 생성
            audio_part = text_to_speech_part(text, speed_up=speed_up)
            
            # 타이밍 기록
            start_ms = len(combined)
            end_ms = start_ms + len(audio_part)
            timings.append({
                "start_ms": start_ms,
                "end_ms": end_ms,
                "subtitle": subtitle,
                "text": text
            })

            combined += audio_part

            # 문단 사이 쉬는 시간 추가
            pause_ms = int(pause_sec * 1000)
            if speed_up:
                pause_ms = int(pause_ms * 0.5)  # 숏츠는 쉬는 시간도 짧게
            combined += create_silence(pause_ms)

            print(f"     [{i+1}/{len(script_parts)}] 완료", end="\r")
            
            # 너무 많은 요청 방지 (약간의 딜레이)
            time.sleep(0.3)

        except Exception as e:
            print(f"\n     ⚠️  파트 {i+1} 오류: {e}")
            # 실패한 파트는 무음으로 대체
            combined += create_silence(2000)
            timings.append({
                "start_ms": len(combined) - 2000,
                "end_ms": len(combined),
                "subtitle": subtitle,
                "text": text
            })

    print()
    return combined, timings


if __name__ == "__main__":
    # 단독 테스트
    sample_scripts = {
        "shorts": [
            {"text": "안녕하세요! 오늘의 경제 뉴스 3가지 시작합니다!", "pause": 0.3, "subtitle": "경제 뉴스 TOP 3"},
            {"text": "첫 번째! 미국 연준이 기준금리를 동결했습니다.", "pause": 0.5, "subtitle": "연준 기준금리 동결"},
        ],
        "longform": [
            {"text": "안녕하세요. 오늘의 경제 뉴스를 자세히 알아보겠습니다.", "pause": 1.0, "subtitle": "경제 뉴스 분석"},
            {"text": "미국 연방준비제도가 이번 FOMC 회의에서 기준금리를 현행 수준으로 유지하기로 결정했습니다.", "pause": 0.8, "subtitle": "연준 금리 동결 결정"},
        ]
    }
    
    result = generate_tts(sample_scripts)
    print("\n생성된 파일:")
    print(f"  숏츠: {result['shorts']}")
    print(f"  롱폼: {result['longform']}")
