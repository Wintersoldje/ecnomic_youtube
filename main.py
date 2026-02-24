"""
📺 경제 유튜브 자동화 시스템
- 매일 경제 뉴스를 수집하고, 숏츠 + 롱폼 영상을 자동으로 생성합니다.
- 사용법: python main.py
"""

import os
import sys
import subprocess

def check_and_install():
    """필요한 패키지를 자동으로 설치합니다."""

    # (import명, pip 설치명) 쌍으로 관리
    packages = [
        ("requests",      "requests"),
        ("bs4",           "beautifulsoup4"),
        ("feedparser",    "feedparser"),
        ("PIL",           "Pillow"),
        ("gtts",          "gtts"),
        ("pydub",         "pydub"),
        ("moviepy",       "moviepy"),
    ]

    print("📦 필요한 패키지를 확인 중...")

    # 1단계: pip 자체를 먼저 최신으로 올려서 버전 파싱 오류 방지
    print("  → pip 업그레이드 중...")
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user", "-q"],
        stderr=subprocess.DEVNULL
    )

    # 2단계: 각 패키지 설치
    for import_name, pip_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            print(f"  → {pip_name} 설치 중...")
            ret = subprocess.call(
                [sys.executable, "-m", "pip", "install", pip_name, "--user", "-q"],
                stderr=subprocess.DEVNULL
            )
            if ret != 0:
                # --user 실패 시 일반 설치 재시도
                subprocess.call(
                    [sys.executable, "-m", "pip", "install", pip_name, "-q"],
                    stderr=subprocess.DEVNULL
                )

    print("✅ 패키지 준비 완료!\n")

check_and_install()

from news_collector import collect_top_news
from script_generator import generate_scripts
from tts_generator import generate_tts
from image_collector import collect_images
from video_maker import make_shorts, make_longform

def main():
    print("=" * 55)
    print("   📈 경제 유튜브 자동화 시스템 시작!")
    print("=" * 55)
    print()

    # 1. 뉴스 수집
    print("📰 Step 1: 오늘의 경제 뉴스 수집 중...")
    news_list = collect_top_news()
    if not news_list:
        print("❌ 뉴스를 가져오지 못했습니다. 인터넷 연결을 확인하세요.")
        return
    print(f"  → {len(news_list)}개 뉴스 수집 완료!\n")

    # 2. 스크립트 생성
    print("✍️  Step 2: 영상 스크립트 생성 중...")
    scripts = generate_scripts(news_list)
    print("  → 숏츠 & 롱폼 스크립트 완성!\n")

    # 3. 이미지 수집
    print("🖼️  Step 3: 관련 이미지 수집 중...")
    images = collect_images(news_list)
    print(f"  → {len(images)}개 이미지 준비 완료!\n")

    # 4. 음성 생성
    print("🎙️  Step 4: 음성(TTS) 생성 중...")
    audio_files = generate_tts(scripts)
    print("  → 숏츠 & 롱폼 음성 파일 생성 완료!\n")

    # 5. 영상 제작
    print("🎬 Step 5: 영상 제작 중...")
    shorts_path = make_shorts(scripts, images, audio_files)
    longform_path = make_longform(scripts, images, audio_files)

    print()
    print("=" * 55)
    print("   🎉 영상 제작 완료!")
    print("=" * 55)
    print(f"  📱 숏츠 영상: {shorts_path}")
    print(f"  🎥 롱폼 영상: {longform_path}")
    print()
    print("  👆 위 파일을 유튜브에 업로드하세요!")
    print("=" * 55)

if __name__ == "__main__":
    main()
