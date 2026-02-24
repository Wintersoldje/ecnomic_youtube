"""
📺 경제 유튜브 자동화 시스템 (최종 버전)
- 매일 경제 뉴스를 수집하고, 숏츠 + 롱폼 영상을 자동으로 생성
- 사용법: python main.py
"""

import os
import sys
import subprocess

def check_and_install():
    """필요한 패키지 자동 설치"""
    packages = [
        ("requests", "requests"),
        ("bs4", "beautifulsoup4"),
        ("feedparser", "feedparser"),
        ("PIL", "Pillow"),
        ("gtts", "gtts"),
        ("pydub", "pydub"),
        ("moviepy", "moviepy"),
    ]
    
    print("📦 Checking packages...")
    
    # pip 업그레이드
    print("  → Upgrading pip...")
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user", "-q"],
        stderr=subprocess.DEVNULL
    )
    
    # 패키지 설치
    for import_name, pip_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            print(f"  → Installing {pip_name}...")
            subprocess.call(
                [sys.executable, "-m", "pip", "install", pip_name, "--user", "-q"],
                stderr=subprocess.DEVNULL
            )
    
    print("✅ Packages ready!\n")


check_and_install()

from news_collector import collect_top_news
from script_generator import generate_scripts
from tts_generator import generate_tts
from image_collector import collect_images
from video_maker import make_shorts, make_longform


def main():
    print("=" * 60)
    print("   📈 Economic YouTube Automation System")
    print("=" * 60)
    print()
    
    # 1. 뉴스 수집
    print("📰 Step 1: Collecting news...")
    news_list = collect_top_news()
    if not news_list:
        print("❌ Failed to collect news. Check internet connection.")
        return
    print(f"  → {len(news_list)} news collected!\n")
    
    # 2. 스크립트 생성
    print("✍️  Step 2: Generating scripts...")
    scripts = generate_scripts(news_list)
    print("  → Scripts generated!\n")
    
    # 3. 이미지 수집
    print("🖼️  Step 3: Collecting images...")
    images = collect_images(news_list)
    print(f"  → {len(images)} images ready!\n")
    
    # 4. 음성 생성
    print("🎙️  Step 4: Generating TTS...")
    audio_files = generate_tts(scripts)
    print("  → Audio files generated!\n")
    
    # 5. 영상 제작
    print("🎬 Step 5: Creating videos...")
    shorts_path = make_shorts(scripts, images, audio_files)
    longform_path = make_longform(scripts, images, audio_files)
    
    print()
    print("=" * 60)
    print("   🎉 COMPLETED!")
    print("=" * 60)
    print(f"  📱 Shorts: {shorts_path}")
    print(f"  🎥 Longform: {longform_path}")
    print()
    print("  👆 Upload these files to YouTube!")
    print("=" * 60)


if __name__ == "__main__":
    main()
