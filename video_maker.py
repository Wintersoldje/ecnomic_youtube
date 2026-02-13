"""
🎬 영상 제작 모듈
- moviepy 1.x / 2.x 둘 다 호환
- ffmpeg 없으면 설치 안내 후 스크립트 텍스트 저장
- 숏츠: 1080x1920 (9:16), 롱폼: 1920x1080 (16:9)
"""

import os
import sys
import subprocess
from PIL import Image, ImageDraw
import numpy as np

# ── moviepy 버전별 호환 import ──────────────────────────────
try:
    # moviepy 1.x
    from moviepy.editor import (
        ImageClip, AudioFileClip, TextClip,
        CompositeVideoClip, concatenate_videoclips, ColorClip
    )
    MOVIEPY_V2 = False
    print("  [video] moviepy 1.x 감지")
except ImportError:
    try:
        # moviepy 2.x
        from moviepy import (
            ImageClip, AudioFileClip, TextClip,
            CompositeVideoClip, concatenate_videoclips, ColorClip
        )
        MOVIEPY_V2 = True
        print("  [video] moviepy 2.x 감지")
    except ImportError:
        print("  [ERROR] moviepy 설치 필요: pip install moviepy --user")
        sys.exit(1)

# 해상도
SHORTS_W,   SHORTS_H   = 1080, 1920
LONGFORM_W, LONGFORM_H = 1920, 1080
KEYWORD_COLOR = "#FFD700"


# ── ffmpeg 체크 ────────────────────────────────────────────
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
        return True
    except Exception:
        return False


def print_ffmpeg_guide():
    print()
    print("  ❌ ffmpeg 가 설치되어 있지 않습니다!")
    print("     영상 파일을 만들려면 ffmpeg 가 반드시 필요합니다.")
    print()
    print("  ▶ 설치 방법 1 - 관리자 cmd 에서 아래 명령 실행:")
    print("     winget install ffmpeg")
    print()
    print("  ▶ 설치 방법 2 - 수동 설치:")
    print("     1. https://ffmpeg.org/download.html 접속")
    print("     2. Windows builds 다운로드 및 압축 해제 (예: C:\\ffmpeg)")
    print("     3. 시스템 환경변수 PATH 에 C:\\ffmpeg\\bin 추가")
    print("     4. PC 재시작 후 run.bat 다시 실행")
    print()


# ── 이미지 로드 헬퍼 ──────────────────────────────────────
def load_img_array(path, w, h):
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    else:
        # 이미지 없으면 짙은 네이비 배경
        img = Image.new("RGB", (w, h), (20, 20, 50))
    return np.array(img)


# ── 자막 오버레이 이미지 생성 ─────────────────────────────
def make_subtitle_overlay(text, w, h, is_shorts=False):
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not text or not text.strip():
        return np.array(canvas.convert("RGB"))

    draw = ImageDraw.Draw(canvas)
    font_size = 54 if is_shorts else 44
    max_ch    = 16 if is_shorts else 28

    lines, tmp = [], text.strip()
    while len(tmp) > max_ch:
        lines.append(tmp[:max_ch])
        tmp = tmp[max_ch:]
    if tmp:
        lines.append(tmp)

    lh = font_size + 14
    total_h = len(lines) * lh + 28
    bottom  = 220 if is_shorts else 170
    y0      = h - bottom - total_h

    # 배경
    draw.rectangle([16, y0 - 8, w - 16, y0 + total_h + 8], fill=(0, 0, 0, 185))

    # 텍스트 (중앙 정렬 근사)
    for i, line in enumerate(lines):
        approx_w = len(line) * int(font_size * 0.58)
        x = max(24, (w - approx_w) // 2)
        draw.text((x, y0 + i * lh + 6), line, fill="white")

    return np.array(canvas.convert("RGB"))


# ── 워터마크 오버레이 ─────────────────────────────────────
def make_watermark_overlay(w, h):
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    bar_h = 56
    draw.rectangle([0, 0, w, bar_h], fill=(0, 0, 0, 150))
    draw.text((28, 10), "[ Today Economic News ]", fill="#FFD700")
    return np.array(canvas.convert("RGB"))


# ── 단일 구간 클립 생성 ───────────────────────────────────
def build_segment(img_path, subtitle, duration, w, h, is_shorts=False):
    bg_arr  = load_img_array(img_path, w, h)
    sub_arr = make_subtitle_overlay(subtitle, w, h, is_shorts=is_shorts)
    wm_arr  = make_watermark_overlay(w, h)

    def _clip(arr, dur):
        c = ImageClip(arr)
        return c.with_duration(dur) if MOVIEPY_V2 else c.set_duration(dur)

    bg  = _clip(bg_arr,  duration)
    sub = _clip(sub_arr, duration)
    wm  = _clip(wm_arr,  duration)

    return CompositeVideoClip([bg, sub, wm], size=(w, h))


# ── 영상 내보내기 ─────────────────────────────────────────
def export_video(clip, audio, output_path, fps=24):
    clip_a = clip.with_audio(audio) if MOVIEPY_V2 else clip.set_audio(audio)
    tmp    = output_path.replace(".mp4", "_tmpaudio.m4a")
    clip_a.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=tmp,
        remove_temp=True,
        logger=None,
        threads=2,
    )


# ── 단순 슬라이드쇼 (오류 대비) ──────────────────────────
def simple_slideshow(img_paths, audio_path, output_path, w, h):
    print("  ⚠️  단순 슬라이드쇼 모드로 재시도...")
    audio = AudioFileClip(audio_path)
    dur   = audio.duration / max(len(img_paths), 1)

    clips = []
    for p in img_paths:
        arr = load_img_array(p, w, h)
        c   = ImageClip(arr)
        c   = c.with_duration(dur) if MOVIEPY_V2 else c.set_duration(dur)
        clips.append(c)

    if not clips:
        arr = load_img_array(None, w, h)
        c   = ImageClip(arr)
        c   = c.with_duration(audio.duration) if MOVIEPY_V2 else c.set_duration(audio.duration)
        clips = [c]

    final = concatenate_videoclips(clips)
    export_video(final, audio, output_path)
    return output_path


# ── 숏츠 제작 ────────────────────────────────────────────
def make_shorts(scripts, images, audio_files):
    print("  🎬 숏츠 영상 제작 중...")
    os.makedirs("output", exist_ok=True)

    if not check_ffmpeg():
        print_ffmpeg_guide()
        _save_script_txt(scripts["shorts"], "output/shorts_script.txt")
        return "output/shorts_script.txt  ← ffmpeg 설치 후 재실행하세요"

    output_path = "output/shorts_video.mp4"
    audio       = AudioFileClip(audio_files["shorts"])
    timings     = audio_files["shorts_timings"]
    total       = audio.duration
    print(f"     총 길이: {total:.1f}초")

    try:
        n    = max(len(images), 1)
        seg  = total / n
        clips = []
        for i, img_info in enumerate(images):
            subtitle = _pick_subtitle(timings, i * seg, (i + 1) * seg)
            clips.append(build_segment(
                img_info.get("shorts_path", ""),
                subtitle, seg,
                SHORTS_W, SHORTS_H, is_shorts=True
            ))

        final   = concatenate_videoclips(clips)
        cap_dur = min(total, 60)
        final   = final.with_duration(cap_dur) if MOVIEPY_V2 else final.set_duration(cap_dur)
        audio_c = audio.with_duration(cap_dur) if MOVIEPY_V2 else audio.set_duration(cap_dur)
        export_video(final, audio_c, output_path)
        print(f"  ✅ 숏츠 완성: {output_path}")
        return output_path

    except Exception as e:
        print(f"  ⚠️  오류 ({e}) → 슬라이드쇼 모드")
        return simple_slideshow(
            [img.get("shorts_path", "") for img in images],
            audio_files["shorts"], output_path,
            SHORTS_W, SHORTS_H
        )


# ── 롱폼 제작 ────────────────────────────────────────────
def make_longform(scripts, images, audio_files):
    print("  🎬 롱폼 영상 제작 중...")
    os.makedirs("output", exist_ok=True)

    if not check_ffmpeg():
        print_ffmpeg_guide()
        _save_script_txt(scripts["longform"], "output/longform_script.txt")
        return "output/longform_script.txt  ← ffmpeg 설치 후 재실행하세요"

    output_path = "output/longform_video.mp4"
    audio       = AudioFileClip(audio_files["longform"])
    timings     = audio_files["longform_timings"]
    total       = audio.duration
    print(f"     총 길이: {total:.1f}초 ({total/60:.1f}분)")

    try:
        n    = max(len(images), 1)
        seg  = total / n
        clips = []
        for i, img_info in enumerate(images):
            subtitle = _pick_subtitle(timings, i * seg, (i + 1) * seg)
            clips.append(build_segment(
                img_info.get("longform_path", ""),
                subtitle, seg,
                LONGFORM_W, LONGFORM_H, is_shorts=False
            ))

        final = concatenate_videoclips(clips)
        final = final.with_duration(total) if MOVIEPY_V2 else final.set_duration(total)
        export_video(final, audio, output_path)
        print(f"  ✅ 롱폼 완성: {output_path}")
        return output_path

    except Exception as e:
        print(f"  ⚠️  오류 ({e}) → 슬라이드쇼 모드")
        return simple_slideshow(
            [img.get("longform_path", "") for img in images],
            audio_files["longform"], output_path,
            LONGFORM_W, LONGFORM_H
        )


# ── 헬퍼 ─────────────────────────────────────────────────
def _pick_subtitle(timings, start_sec, end_sec):
    mid = (start_sec + end_sec) / 2
    for t in timings:
        s = t["start_ms"] / 1000.0
        e = t["end_ms"]   / 1000.0
        if s <= mid <= e:
            return t.get("subtitle", "")
    if timings:
        closest = min(timings, key=lambda t: abs(t["start_ms"] / 1000.0 - mid))
        return closest.get("subtitle", "")
    return ""


def _save_script_txt(parts, path):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("=== 스크립트 (ffmpeg 설치 후 영상 생성 가능) ===\n\n")
            for i, p in enumerate(parts, 1):
                f.write(f"[{i}] 자막: {p.get('subtitle','')}\n")
                f.write(f"     음성: {p.get('text','')}\n\n")
        print(f"     → 스크립트 저장: {path}")
    except Exception:
        pass
