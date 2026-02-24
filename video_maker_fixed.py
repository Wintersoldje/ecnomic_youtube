"""
🎬 영상 제작 모듈 (자막 강화 버전)
- moviepy 1.x / 2.x 호환
- 자막이 확실하게 보이도록 개선
- 숏츠: 1080x1920 (9:16), 롱폼: 1920x1080 (16:9)
"""

import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── moviepy 버전별 호환 import ──────────────────────────────
try:
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip, 
        concatenate_videoclips, ColorClip
    )
    MOVIEPY_V2 = False
    print("  [video] moviepy 1.x detected")
except ImportError:
    try:
        from moviepy import (
            ImageClip, AudioFileClip, CompositeVideoClip,
            concatenate_videoclips, ColorClip
        )
        MOVIEPY_V2 = True
        print("  [video] moviepy 2.x detected")
    except ImportError:
        print("  [ERROR] moviepy required: pip install moviepy --user")
        sys.exit(1)

# 해상도
SHORTS_W, SHORTS_H = 1080, 1920
LONGFORM_W, LONGFORM_H = 1920, 1080


def check_ffmpeg():
    """ffmpeg 설치 여부 확인"""
    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
        return True
    except Exception:
        return False


def print_ffmpeg_guide():
    """ffmpeg 설치 안내 출력"""
    print()
    print("  ❌ ffmpeg is not installed!")
    print()
    print("  ▶ Installation Method:")
    print("     Open cmd as Administrator and run:")
    print("     winget install ffmpeg")
    print()
    print("  After installation, restart PC and run again.")
    print()


def load_image_as_array(path, w, h):
    """이미지 파일을 numpy 배열로 로드"""
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    else:
        # 기본 배경 (진한 네이비)
        img = Image.new("RGB", (w, h), (15, 25, 50))
    return np.array(img)


def create_subtitle_image(text, w, h, is_shorts=False):
    """
    자막 이미지 생성 - PIL로 직접 그려서 확실하게 보이게 함
    """
    # 투명 캔버스
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    if not text or not text.strip():
        return np.array(img.convert("RGB"))
    
    draw = ImageDraw.Draw(img)
    
    # 폰트 크기 (숏츠가 더 큼)
    font_size = 56 if is_shorts else 46
    
    # 텍스트 줄바꿈 (한 줄당 최대 글자 수)
    max_chars = 14 if is_shorts else 26
    lines = []
    temp = text.strip()
    while len(temp) > max_chars:
        lines.append(temp[:max_chars])
        temp = temp[max_chars:]
    if temp:
        lines.append(temp)
    
    # 자막 박스 위치 (하단에서 조금 위)
    line_height = font_size + 16
    total_text_height = len(lines) * line_height
    box_padding = 24
    box_height = total_text_height + box_padding * 2
    
    # 하단에서 위치 계산
    bottom_margin = 240 if is_shorts else 180
    box_y_start = h - bottom_margin - box_height
    
    # 배경 박스 그리기 (검은색 반투명)
    box_left = 20
    box_right = w - 20
    draw.rectangle(
        [box_left, box_y_start, box_right, box_y_start + box_height],
        fill=(0, 0, 0, 210)  # 진한 반투명
    )
    
    # 각 줄 텍스트 그리기 (흰색)
    for i, line in enumerate(lines):
        # 대략적인 중앙 정렬
        text_width = len(line) * (font_size * 0.55)
        x_pos = max(40, int((w - text_width) / 2))
        y_pos = box_y_start + box_padding + (i * line_height)
        
        # 텍스트 그리기 (흰색, 선명하게)
        draw.text((x_pos, y_pos), line, fill=(255, 255, 255, 255))
    
    # RGB로 변환 (moviepy는 RGBA를 잘 못 읽음)
    return np.array(img.convert("RGB"))


def create_watermark_image(w, h):
    """상단 워터마크 바 생성"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 상단 바 (반투명 검정)
    bar_height = 64
    draw.rectangle([0, 0, w, bar_height], fill=(0, 0, 0, 160))
    
    # 워터마크 텍스트 (골드 컬러)
    draw.text((32, 14), "[ Economic News Today ]", fill=(255, 215, 0, 255))
    
    return np.array(img.convert("RGB"))


def make_video_segment(img_path, subtitle_text, duration, w, h, is_shorts=False):
    """
    단일 영상 구간 생성 (배경 + 자막 + 워터마크)
    """
    # 1. 배경 이미지
    bg_array = load_image_as_array(img_path, w, h)
    bg_clip = ImageClip(bg_array)
    if MOVIEPY_V2:
        bg_clip = bg_clip.with_duration(duration)
    else:
        bg_clip = bg_clip.set_duration(duration)
    
    # 2. 자막 오버레이
    subtitle_array = create_subtitle_image(subtitle_text, w, h, is_shorts)
    sub_clip = ImageClip(subtitle_array)
    if MOVIEPY_V2:
        sub_clip = sub_clip.with_duration(duration)
    else:
        sub_clip = sub_clip.set_duration(duration)
    
    # 3. 워터마크 오버레이
    wm_array = create_watermark_image(w, h)
    wm_clip = ImageClip(wm_array)
    if MOVIEPY_V2:
        wm_clip = wm_clip.with_duration(duration)
    else:
        wm_clip = wm_clip.set_duration(duration)
    
    # 4. 모든 레이어 합성
    composite = CompositeVideoClip([bg_clip, sub_clip, wm_clip], size=(w, h))
    
    return composite


def export_with_audio(video_clip, audio_path, output_path, fps=24):
    """영상 + 오디오 합쳐서 저장"""
    audio = AudioFileClip(audio_path)
    
    if MOVIEPY_V2:
        final = video_clip.with_audio(audio)
    else:
        final = video_clip.set_audio(audio)
    
    temp_audio = output_path.replace(".mp4", "_temp_audio.m4a")
    
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio,
        remove_temp=True,
        logger=None,
        threads=2
    )


def get_subtitle_for_time(timings, start_sec, end_sec):
    """특정 시간 구간의 자막 텍스트 가져오기"""
    mid_time = (start_sec + end_sec) / 2
    
    # 중간 시점에 해당하는 자막 찾기
    for timing in timings:
        t_start = timing["start_ms"] / 1000.0
        t_end = timing["end_ms"] / 1000.0
        if t_start <= mid_time <= t_end:
            return timing.get("subtitle", "")
    
    # 없으면 가장 가까운 것
    if timings:
        closest = min(timings, key=lambda t: abs(t["start_ms"] / 1000.0 - mid_time))
        return closest.get("subtitle", "")
    
    return ""


def make_shorts(scripts, images, audio_files):
    """
    숏츠 영상 제작 (9:16)
    """
    print("  🎬 Creating Shorts video...")
    os.makedirs("output", exist_ok=True)
    
    if not check_ffmpeg():
        print_ffmpeg_guide()
        _save_script_fallback(scripts["shorts"], "output/shorts_script.txt")
        return "output/shorts_script.txt  ← Install ffmpeg first"
    
    output_path = "output/shorts_video.mp4"
    audio_path = audio_files["shorts"]
    timings = audio_files["shorts_timings"]
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    print(f"     Duration: {total_duration:.1f}s")
    
    try:
        # 뉴스 개수만큼 구간 나누기
        num_segments = len(images)
        segment_duration = total_duration / num_segments
        
        segments = []
        for i, img_info in enumerate(images):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            # 해당 구간의 자막 텍스트
            subtitle = get_subtitle_for_time(timings, start_time, end_time)
            
            # 영상 구간 생성
            seg = make_video_segment(
                img_info.get("shorts_path", ""),
                subtitle,
                segment_duration,
                SHORTS_W, SHORTS_H,
                is_shorts=True
            )
            segments.append(seg)
        
        # 모든 구간 연결
        full_video = concatenate_videoclips(segments)
        
        # 최대 60초로 제한
        max_duration = min(total_duration, 60)
        if MOVIEPY_V2:
            full_video = full_video.with_duration(max_duration)
            audio = audio.with_duration(max_duration)
        else:
            full_video = full_video.set_duration(max_duration)
            audio = audio.set_duration(max_duration)
        
        # 오디오 합성 및 저장
        export_with_audio(full_video, audio_path, output_path)
        
        print(f"  ✅ Shorts completed: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return f"output/shorts_error.txt  ← Check: {e}"


def make_longform(scripts, images, audio_files):
    """
    롱폼 영상 제작 (16:9)
    """
    print("  🎬 Creating Long-form video...")
    os.makedirs("output", exist_ok=True)
    
    if not check_ffmpeg():
        print_ffmpeg_guide()
        _save_script_fallback(scripts["longform"], "output/longform_script.txt")
        return "output/longform_script.txt  ← Install ffmpeg first"
    
    output_path = "output/longform_video.mp4"
    audio_path = audio_files["longform"]
    timings = audio_files["longform_timings"]
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    print(f"     Duration: {total_duration:.1f}s ({total_duration/60:.1f}min)")
    
    try:
        # 뉴스 개수만큼 구간 나누기
        num_segments = len(images)
        segment_duration = total_duration / num_segments
        
        segments = []
        for i, img_info in enumerate(images):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            # 해당 구간의 자막 텍스트
            subtitle = get_subtitle_for_time(timings, start_time, end_time)
            
            # 영상 구간 생성
            seg = make_video_segment(
                img_info.get("longform_path", ""),
                subtitle,
                segment_duration,
                LONGFORM_W, LONGFORM_H,
                is_shorts=False
            )
            segments.append(seg)
        
        # 모든 구간 연결
        full_video = concatenate_videoclips(segments)
        
        if MOVIEPY_V2:
            full_video = full_video.with_duration(total_duration)
        else:
            full_video = full_video.set_duration(total_duration)
        
        # 오디오 합성 및 저장
        export_with_audio(full_video, audio_path, output_path)
        
        print(f"  ✅ Long-form completed: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return f"output/longform_error.txt  ← Check: {e}"


def _save_script_fallback(script_parts, path):
    """ffmpeg 없을 때 스크립트 텍스트 저장"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("=== Video Script (Install ffmpeg to create video) ===\n\n")
            for i, part in enumerate(script_parts, 1):
                f.write(f"[{i}] Subtitle: {part.get('subtitle','')}\n")
                f.write(f"     Audio: {part.get('text','')}\n\n")
        print(f"     → Script saved: {path}")
    except Exception:
        pass
