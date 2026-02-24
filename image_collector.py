"""
🖼️ 이미지 수집 모듈 (개선 버전)
- Pillow 버전 호환성 문제 해결 (rounded_rectangle → rectangle)
- 실제로 보기 좋은 이미지 생성
- 무료 이미지 API 통합
"""

import os
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import io
import time

# 무료 이미지 API 키 (선택사항)
UNSPLASH_ACCESS_KEY = ""
PIXABAY_API_KEY = ""

# 해상도
SHORTS_WIDTH, SHORTS_HEIGHT = 1080, 1920
LONGFORM_WIDTH, LONGFORM_HEIGHT = 1920, 1080

# 경제 키워드 → 영어 검색어
KEYWORD_MAP = {
    "금리": "interest rate",
    "주식": "stock market",
    "반도체": "semiconductor chip",
    "달러": "dollar currency",
    "환율": "exchange rate",
    "인플레이션": "inflation",
    "부동산": "real estate",
    "삼성": "samsung electronics",
    "수출": "export container",
    "연준": "federal reserve",
    "코스피": "stock market",
}


def get_font(size):
    """한글/유니코드를 지원하는 폰트를 우선 로드"""
    font_candidates = [
        # Windows
        r"C:\\Windows\\Fonts\\malgun.ttf",
        r"C:\\Windows\\Fonts\\malgunbd.ttf",
        r"C:\\Windows\\Fonts\\gulim.ttc",
        # macOS
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue

    # 최후 fallback: Pillow 기본 폰트
    return ImageFont.load_default()


def keyword_to_query(keyword):
    """한국어 키워드를 영어 검색어로 변환"""
    for k, v in KEYWORD_MAP.items():
        if k in keyword:
            return v
    return "business economy"


def download_unsplash(query, save_path, width, height):
    """Unsplash에서 무료 이미지 다운로드"""
    if not UNSPLASH_ACCESS_KEY:
        return False
    
    try:
        url = f"https://api.unsplash.com/photos/random?query={urllib.parse.quote(query)}&orientation=landscape"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            img_url = data["urls"]["regular"]
            img_response = requests.get(img_url, timeout=15)
            
            if img_response.status_code == 200:
                img = Image.open(io.BytesIO(img_response.content))
                img = img.resize((width, height), Image.LANCZOS)
                img.save(save_path, quality=95)
                return True
    except Exception as e:
        print(f"     [Unsplash error: {e}]")
    return False


def create_professional_image(title, keywords, save_path, width, height, is_shorts=False):
    """
    전문적인 경제 뉴스 이미지 생성
    - Pillow 호환성: rounded_rectangle 사용 안 함
    - 뉴스별 다른 색상 테마
    """
    # 색상 테마 (배경, 악센트)
    themes = [
        ("#0d47a1", "#42a5f5"),  # 파랑
        ("#1b5e20", "#66bb6a"),  # 초록
        ("#b71c1c", "#ef5350"),  # 빨강
        ("#4a148c", "#ab47bc"),  # 보라
        ("#e65100", "#ff9800"),  # 주황
    ]
    
    theme_idx = hash(title) % len(themes)
    bg_color, accent_color = themes[theme_idx]
    
    # 캔버스 생성
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    header_font = get_font(40 if is_shorts else 34)
    tag_font = get_font(34 if is_shorts else 28)
    title_font = get_font(54 if is_shorts else 46)
    date_font = get_font(32 if is_shorts else 28)
    
    # 그라데이션 효과 (수평선들)
    for y in range(0, height, 2):
        alpha = int(255 * (1 - y / height) * 0.3)
        color = tuple(min(255, c + alpha) for c in Image.new("RGB", (1, 1), bg_color).getpixel((0, 0)))
        draw.line([(0, y), (width, y)], fill=color, width=2)
    
    # 상단 헤더바
    header_h = int(height * 0.08)
    draw.rectangle([0, 0, width, header_h], fill=accent_color)
    
    # 헤더 텍스트
    header_text = "ECONOMIC NEWS"
    text_w = int(draw.textlength(header_text, font=header_font))
    draw.text((int((width - text_w) / 2), int(header_h * 0.2)), 
              header_text, fill="white", font=header_font)
    
    # 키워드 태그들
    tag_y = int(height * 0.12)
    tag_x = int(width * 0.05)
    for kw in keywords[:3]:
        tag_text = f"#{kw}"
        tag_w = len(tag_text) * 16 + 20
        # rounded_rectangle 대신 일반 rectangle 사용
        draw.rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + 40], 
                      fill=accent_color, outline="white", width=2)
        draw.text((tag_x + 10, tag_y + 8), tag_text, fill="white", font=tag_font)
        tag_x += tag_w + 12
    
    # 제목 영역
    title_y = int(height * 0.32)
    title_bg_h = int(height * 0.35)
    
    # 제목 배경 (반투명 효과 대신 불투명 박스)
    draw.rectangle([int(width * 0.05), title_y,
                   int(width * 0.95), title_y + title_bg_h],
                  fill=(0, 0, 0), outline=accent_color, width=3)
    
    # 제목 텍스트 (줄바꿈)
    safe_title = "".join(c for c in title if ord(c) < 0x10000)  # 이모지 제거
    max_chars = 14 if is_shorts else 18
    lines = []
    temp = safe_title
    while len(temp) > max_chars:
        lines.append(temp[:max_chars])
        temp = temp[max_chars:]
    if temp:
        lines.append(temp)
    
    font_size = 54 if is_shorts else 46
    line_height = font_size + 14
    
    for i, line in enumerate(lines[:3]):
        y = title_y + 20 + (i * line_height)
        draw.text((int(width * 0.08), y), line, fill="white", font=title_font)
    
    # 하단바
    footer_y = int(height * 0.88)
    draw.rectangle([0, footer_y, width, height], fill=(0, 0, 0))
    
    from datetime import datetime
    date_str = datetime.now().strftime("%Y.%m.%d")
    draw.text((int(width * 0.05), footer_y + 15), date_str, fill=accent_color, font=date_font)
    
    # 저장
    img.save(save_path, quality=95)
    return True


def collect_images(news_list):
    """
    각 뉴스의 이미지 수집
    Returns: list of {shorts_path, longform_path, ...}
    """
    os.makedirs("output/images", exist_ok=True)
    images = []
    
    for i, news in enumerate(news_list):
        title = news["title"]
        keywords = news.get("keywords", [])
        
        primary_kw = keywords[0] if keywords else "경제"
        query = keyword_to_query(primary_kw)
        
        shorts_path = f"output/images/img_{i+1}_shorts.jpg"
        longform_path = f"output/images/img_{i+1}_longform.jpg"
        
        print(f"     Image {i+1}: '{primary_kw}' ...")
        
        # 1. Unsplash 시도
        success = download_unsplash(query, shorts_path, SHORTS_WIDTH, SHORTS_HEIGHT)
        if success:
            download_unsplash(query, longform_path, LONGFORM_WIDTH, LONGFORM_HEIGHT)
            print(f"     → Downloaded from Unsplash")
            time.sleep(0.5)
        else:
            # 2. 전문 이미지 생성
            create_professional_image(title, keywords, shorts_path,
                                     SHORTS_WIDTH, SHORTS_HEIGHT, is_shorts=True)
            create_professional_image(title, keywords, longform_path,
                                     LONGFORM_WIDTH, LONGFORM_HEIGHT, is_shorts=False)
            print(f"     → Generated professional image")
        
        images.append({
            "news_index": i,
            "shorts_path": shorts_path,
            "longform_path": longform_path,
            "title": title,
            "keywords": keywords
        })
    
    return images


if __name__ == "__main__":
    test_news = [{
        "title": "미 연준, 기준금리 동결 결정",
        "keywords": ["연준", "금리", "인플레이션"]
    }]
    imgs = collect_images(test_news)
    print(f"Images: {imgs}")
