"""
🎙️ TTS 생성 모듈 (속도 차이 강화)
- 숏츠: 1.4배속 (빠르고 역동적)
- 롱폼: 1.0배속 (자연스럽고 이해하기 쉽게)
"""

import os
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import time


def create_silence(duration_ms):
    """무음 생성"""
    return AudioSegment.silent(duration=duration_ms)


def text_to_audio(text, speed_multiplier=1.0):
    """
    텍스트 → 음성 변환
    speed_multiplier: 1.0 = 정상, 1.4 = 빠르게
    """
    tts = gTTS(text=text, lang='ko', slow=False)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tmp.name)
    tmp.close()
    
    audio = AudioSegment.from_mp3(tmp.name)
    os.unlink(tmp.name)
    
    if speed_multiplier != 1.0:
        # 속도 변경 (음높이 유지)
        new_frame_rate = int(audio.frame_rate * speed_multiplier)
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
        audio = audio.set_frame_rate(audio.frame_rate)
    
    return audio


def build_audio_track(script_parts, is_shorts=False):
    """
    스크립트 파트들을 하나의 오디오 트랙으로 합성
    
    Returns: (AudioSegment, timings_list)
    """
    # 속도 설정
    speed = 1.4 if is_shorts else 1.0
    
    combined = AudioSegment.empty()
    timings = []
    
    total_parts = len(script_parts)
    
    for i, part in enumerate(script_parts):
        text = part.get("text", "")
        pause_sec = part.get("pause", 0.5)
        subtitle = part.get("subtitle", "")
        
        if not text.strip():
            continue
        
        try:
            # 음성 생성
            audio_part = text_to_audio(text, speed_multiplier=speed)
            
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
            
            # 쉬는 시간
            pause_ms = int(pause_sec * 1000)
            if is_shorts:
                pause_ms = int(pause_ms * 0.6)  # 숏츠는 쉬는 시간도 짧게
            
            combined += create_silence(pause_ms)
            
            print(f"     [{i+1}/{total_parts}] Generated", end="\r")
            
            time.sleep(0.2)  # API 제한 방지
            
        except Exception as e:
            print(f"\n     Error at part {i+1}: {e}")
            # 실패 시 2초 무음으로 대체
            combined += create_silence(2000)
            timings.append({
                "start_ms": len(combined) - 2000,
                "end_ms": len(combined),
                "subtitle": subtitle,
                "text": text
            })
    
    print()
    return combined, timings


def generate_tts(scripts):
    """
    숏츠 + 롱폼 음성 파일 생성
    """
    os.makedirs("output", exist_ok=True)
    
    shorts_script = scripts["shorts"]
    longform_script = scripts["longform"]
    
    # 숏츠 음성 (1.4배속)
    print("  🎙️  Shorts TTS (1.4x speed) ...")
    shorts_audio, shorts_timings = build_audio_track(shorts_script, is_shorts=True)
    shorts_path = "output/audio_shorts.mp3"
    shorts_audio.export(shorts_path, format="mp3")
    print(f"     → Shorts audio: {len(shorts_audio)/1000:.1f}s")
    
    time.sleep(2)  # API 쿨다운
    
    # 롱폼 음성 (1.0배속)
    print("  🎙️  Longform TTS (1.0x speed) ...")
    longform_audio, longform_timings = build_audio_track(longform_script, is_shorts=False)
    longform_path = "output/audio_longform.mp3"
    longform_audio.export(longform_path, format="mp3")
    print(f"     → Longform audio: {len(longform_audio)/1000:.1f}s")
    
    return {
        "shorts": shorts_path,
        "longform": longform_path,
        "shorts_timings": shorts_timings,
        "longform_timings": longform_timings
    }


if __name__ == "__main__":
    test_scripts = {
        "shorts": [
            {"text": "오늘 경제 뉴스 3가지!", "pause": 0.3, "subtitle": "경제 뉴스 TOP 3"},
            {"text": "첫 번째! 미국 연준 금리 동결", "pause": 0.5, "subtitle": "연준 금리 동결"},
        ],
        "longform": [
            {"text": "안녕하세요. 오늘의 경제 뉴스를 알려드립니다.", "pause": 1.0, "subtitle": "경제 뉴스"},
        ]
    }
    
    result = generate_tts(test_scripts)
    print(f"\nFiles created:")
    print(f"  Shorts: {result['shorts']}")
    print(f"  Longform: {result['longform']}")
