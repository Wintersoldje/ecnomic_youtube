"""
🎬 영상 제작 모듈 (최종 버전)
- 자막이 타이밍에 맞게 정확히 표시
- moviepy 1.x/2.x 호환
- 전문적인 영상 퀄리티
"""

import os
import sys
import subprocess
from PIL import Image, ImageDraw
import numpy as np

# moviepy import
try:
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips
    )
    MOVIEPY_V2 = False
except ImportError:
    from moviepy import (
        ImageClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips
    )
    MOVIEPY_V2 = True

# 해상도
SHORTS_W, SHORTS_H = 1080, 1920
LONGFORM_W, LONGFORM_H = 1920, 1080


def check_ffmpeg():
    """ffmpeg 확인"""
    try:
        subprocess.run(["ffmpeg", "-version"],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL,
                      check=True)
        return True
    except Exception:
        return False


def load_image(path, w, h):
    """이미지 로드"""
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    else:
        img = Image.new("RGB", (w, h), (20, 30, 50))
    return np.array(img)


def make_subtitle_overlay(text, w, h, is_shorts=False):
    """자막 오버레이 생성 (타이밍에 맞게)"""
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    if not text or not text.strip():
        return np.array(canvas.convert("RGB"))
    
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 크기
    font_size = 58 if is_shorts else 48
    
    # 줄바꿈
    max_chars = 13 if is_shorts else 25
    lines = []
    temp = text.strip()
    while len(temp) > max_chars:
        lines.append(temp[:max_chars])
        temp = temp[max_chars:]
    if temp:
        lines.append(temp)
    
    # 자막 박스 위치
    line_h = font_size + 18
    box_h = len(lines) * line_h + 30
    bottom_margin = 250 if is_shorts else 190
    box_y = h - bottom_margin - box_h
    
    # 배경 박스 (진한 검정)
    draw.rectangle([16, box_y, w - 16, box_y + box_h], 
                  fill=(0, 0, 0, 220))
    
    # 텍스트
    for i, line in enumerate(lines):
        text_w = len(line) * (font_size * 0.55)
        x = max(30, int((w - text_w) / 2))
        y = box_y + 15 + (i * line_h)
        draw.text((x, y), line, fill=(255, 255, 255, 255))
    
    return np.array(canvas.convert("RGB"))


def make_watermark(w, h):
    """워터마크 생성"""
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, w, 68], fill=(0, 0, 0, 170))
    draw.text((34, 16), "[ Economic News ]", fill=(255, 215, 0, 255))
    return np.array(canvas.convert("RGB"))


def create_clip_with_subtitle(img_path, subtitle, start_time, duration, w, h, is_shorts):
    """
    이미지 + 자막 + 워터마크 클립 생성
    start_time: 시작 시간 (초)
    """
    # 배경
    bg_arr = load_image(img_path, w, h)
    bg = ImageClip(bg_arr)
    if MOVIEPY_V2:
        bg = bg.with_duration(duration).with_start(start_time)
    else:
        bg = bg.set_duration(duration).set_start(start_time)
    
    # 자막
    sub_arr = make_subtitle_overlay(subtitle, w, h, is_shorts)
    sub = ImageClip(sub_arr)
    if MOVIEPY_V2:
        sub = sub.with_duration(duration).with_start(start_time)
    else:
        sub = sub.set_duration(duration).set_start(start_time)
    
    # 워터마크
    wm_arr = make_watermark(w, h)
    wm = ImageClip(wm_arr)
    if MOVIEPY_V2:
        wm = wm.with_duration(duration).with_start(start_time)
    else:
        wm = wm.set_duration(duration).set_start(start_time)
    
    return [bg, sub, wm]


def make_shorts(scripts, images, audio_files):
    """숏츠 영상 제작"""
    print("  🎬 Making Shorts video...")
    os.makedirs("output", exist_ok=True)
    
    if not check_ffmpeg():
        print("  ❌ ffmpeg not installed!")
        return "output/shorts_error.txt"
    
    output_path = "output/shorts_video.mp4"
    audio_path = audio_files["shorts"]
    timings = audio_files["shorts_timings"]
    
    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"     Duration: {total_dur:.1f}s")
    
    try:
        all_clips = []
        
        # 타이밍별로 자막 클립 생성
        for timing in timings:
            start_sec = timing["start_ms"] / 1000.0
            end_sec = timing["end_ms"] / 1000.0
            duration = end_sec - start_sec
            subtitle = timing.get("subtitle", "")
            
            if duration <= 0:
                continue
            
            # 해당 시간에 맞는 이미지 선택
            img_idx = int(start_sec / (total_dur / len(images)))
            img_idx = min(img_idx, len(images) - 1)
            img_path = images[img_idx].get("shorts_path", "")
            
            clips = create_clip_with_subtitle(
                img_path, subtitle, start_sec, duration,
                SHORTS_W, SHORTS_H, is_shorts=True
            )
            all_clips.extend(clips)
        
        # 합성
        final = CompositeVideoClip(all_clips, size=(SHORTS_W, SHORTS_H))
        max_dur = min(total_dur, 60)
        if MOVIEPY_V2:
            final = final.with_duration(max_dur)
            audio = audio.with_duration(max_dur)
            final = final.with_audio(audio)
        else:
            final = final.set_duration(max_dur)
            audio = audio.set_duration(max_dur)
            final = final.set_audio(audio)
        
        # 저장
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="output/temp_shorts_audio.m4a",
            remove_temp=True,
            logger=None,
            threads=2
        )
        
        print(f"  ✅ Shorts: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return f"output/shorts_error.txt"


def make_longform(scripts, images, audio_files):
    """롱폼 영상 제작"""
    print("  🎬 Making Long-form video...")
    os.makedirs("output", exist_ok=True)
    
    if not check_ffmpeg():
        print("  ❌ ffmpeg not installed!")
        return "output/longform_error.txt"
    
    output_path = "output/longform_video.mp4"
    audio_path = audio_files["longform"]
    timings = audio_files["longform_timings"]
    
    audio = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"     Duration: {total_dur:.1f}s ({total_dur/60:.1f}min)")
    
    try:
        all_clips = []
        
        # 타이밍별로 자막 클립 생성
        for timing in timings:
            start_sec = timing["start_ms"] / 1000.0
            end_sec = timing["end_ms"] / 1000.0
            duration = end_sec - start_sec
            subtitle = timing.get("subtitle", "")
            
            if duration <= 0:
                continue
            
            # 이미지 선택
            img_idx = int(start_sec / (total_dur / len(images)))
            img_idx = min(img_idx, len(images) - 1)
            img_path = images[img_idx].get("longform_path", "")
            
            clips = create_clip_with_subtitle(
                img_path, subtitle, start_sec, duration,
                LONGFORM_W, LONGFORM_H, is_shorts=False
            )
            all_clips.extend(clips)
        
        # 합성
        final = CompositeVideoClip(all_clips, size=(LONGFORM_W, LONGFORM_H))
        if MOVIEPY_V2:
            final = final.with_duration(total_dur)
            final = final.with_audio(audio)
        else:
            final = final.set_duration(total_dur)
            final = final.set_audio(audio)
        
        # 저장
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="output/temp_longform_audio.m4a",
            remove_temp=True,
            logger=None,
            threads=2
        )
        
        print(f"  ✅ Longform: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return f"output/longform_error.txt"
