"""
🖼️ 이미지 수집 모듈
- Unsplash API (무료 50회/시간) 또는 Pixabay API (무료)로 관련 이미지를 수집합니다.
- API 없을 때는 무료 경제 관련 기본 이미지를 생성합니다.
"""

import os
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import io
import time

# Unsplash API (무료 - https://unsplash.com/developers 에서 발급)
UNSPLASH_ACCESS_KEY = ""  # 여기에 발급받은 키 입력 (무료 50회/시간)

# Pixabay API (무료 - https://pixabay.com/api/docs/ 에서 발급)
PIXABAY_API_KEY = ""  # 여기에 발급받은 키 입력 (무료)

# 숏츠 해상도 (9:16)
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1920

# 롱폼 해상도 (16:9)
LONGFORM_WIDTH = 1920
LONGFORM_HEIGHT = 1080

# 경제 키워드 → 영어 검색어 매핑
KEYWORD_MAP = {
    "금리": "interest rate money bank",
    "주식": "stock market trading",
    "코스피": "korean stock exchange",
    "달러": "dollar currency exchange",
    "환율": "currency exchange forex",
    "인플레이션": "inflation economy prices",
    "물가": "shopping prices consumer",
    "GDP": "economy growth graph",
    "수출": "shipping cargo export",
    "부동산": "real estate building",
    "반도체": "semiconductor chip technology",
    "삼성": "technology electronics",
    "연준": "federal reserve bank",
    "채권": "bond investment finance",
    "ETF": "investment portfolio finance",
    "비트코인": "bitcoin cryptocurrency",
    "기준금리": "central bank rate",
}

# 기본 경제 이미지 검색어 (키워드 매핑 없을 때)
DEFAULT_QUERIES = [
    "economy finance chart",
    "business growth money",
    "stock market trading",
    "financial news graph",
]


def _load_korean_font(size):
    """한글 출력 가능한 폰트를 우선 로드하고, 없으면 기본 폰트 사용"""
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",         # 맑은 고딕
        "C:/Windows/Fonts/malgunbd.ttf",       # 맑은 고딕 Bold
        "C:/Windows/Fonts/NanumGothic.ttf",    # 나눔고딕(설치된 경우)
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _safe_draw_text(draw, xy, text, fill, font):
    """구버전 Pillow/기본 폰트 환경에서도 텍스트 렌더링이 죽지 않도록 안전 처리"""
    try:
        draw.text(xy, text, fill=fill, font=font)
    except Exception:
        # 기본 폰트가 latin-1만 지원하는 경우를 위한 최종 폴백
        fallback = text.encode("latin-1", errors="replace").decode("latin-1")
        draw.text(xy, fallback, fill=fill, font=ImageFont.load_default())


def keyword_to_query(keyword):
    """한국어 키워드를 영어 검색어로 변환"""
    for k, v in KEYWORD_MAP.items():
        if k in keyword:
            return v
    return "economy business finance"


def download_image_unsplash(query, save_path, width=1080, height=1080):
    """Unsplash에서 이미지 다운로드"""
    if not UNSPLASH_ACCESS_KEY:
        return False
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.unsplash.com/photos/random?query={encoded_query}&orientation=landscape"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            img_url = data["urls"]["regular"]
            
            img_response = requests.get(img_url, timeout=15)
            if img_response.status_code == 200:
                img = Image.open(io.BytesIO(img_response.content))
                img = img.resize((width, height), Image.LANCZOS)
                img.save(save_path)
                return True
    except Exception as e:
        print(f"     Unsplash 오류: {e}")
    return False


def download_image_pixabay(query, save_path, width=1080, height=1080):
    """Pixabay에서 이미지 다운로드"""
    if not PIXABAY_API_KEY:
        return False
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={encoded_query}&image_type=photo&per_page=3"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                img_url = hits[0]["webformatURL"]
                img_response = requests.get(img_url, timeout=15)
                if img_response.status_code == 200:
                    img = Image.open(io.BytesIO(img_response.content))
                    img = img.resize((width, height), Image.LANCZOS)
                    img.save(save_path)
                    return True
    except Exception as e:
        print(f"     Pixabay 오류: {e}")
    return False


def create_placeholder_image(title, keywords, save_path, width=1080, height=1080, is_shorts=False):
    """
    API 없을 때 텍스트 기반 플레이스홀더 이미지 생성
    깔끔하고 전문적인 경제 뉴스 스타일
    """
    # 배경색 - 뉴스마다 다른 색상 (경제 느낌)
    colors = [
        ("#1a237e", "#e3f2fd"),  # 짙은 파랑 + 연한 파랑
        ("#004d40", "#e0f2f1"),  # 짙은 초록 + 연한 초록
        ("#bf360c", "#fbe9e7"),  # 짙은 빨강 + 연한 빨강
        ("#37474f", "#eceff1"),  # 짙은 회색 + 연한 회색
        ("#4a148c", "#f3e5f5"),  # 짙은 보라 + 연한 보라
    ]

    # 해시로 색상 선택 (같은 뉴스는 같은 색상)
    color_idx = hash(title) % len(colors)
    bg_color, text_bg_color = colors[color_idx]

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    def draw_rounded_box(x1, y1, x2, y2, radius, fill):
        """
        Pillow 구버전 호환: rounded_rectangle 미지원이면 일반 사각형으로 대체
        """
        rounded_fn = getattr(draw, "rounded_rectangle", None)
        if callable(rounded_fn):
            rounded_fn([x1, y1, x2, y2], radius=radius, fill=fill)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=fill)

    # 배경 패턴 (격자 선)
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill="#ffffff10", width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill="#ffffff10", width=1)

    # 상단 바
    bar_h = int(height * 0.10)
    draw.rectangle([0, 0, width, bar_h], fill="#ffffff20")
    title_font = _load_korean_font(60 if is_shorts else 50)
    meta_font = _load_korean_font(34 if is_shorts else 30)

    # 상단 텍스트 (이모지 없이)
    _safe_draw_text(
        draw,
        (int(width * 0.05), int(bar_h * 0.25)),
        "[TODAY] Economic News",
        fill="white",
        font=meta_font,
    )

    # 키워드 태그들 (이모지 없이)
    y_pos = int(height * 0.14)
    x_pos = int(width * 0.05)
    for kw in keywords[:3]:
        tag_text = "#" + kw
        tag_w = len(tag_text) * 20 + 24
        draw_rounded_box(x_pos, y_pos, x_pos + tag_w, y_pos + 46, radius=22, fill="#ffffff30")
        _safe_draw_text(draw, (x_pos + 12, y_pos + 9), tag_text, fill="white", font=meta_font)
        x_pos += tag_w + 12

    # 제목 텍스트 (중앙)
    y_center = int(height * 0.34)

    # 제목 배경
    draw.rectangle(
        [int(width * 0.05), y_center - 18,
         int(width * 0.95), y_center + int(height * 0.28)],
        fill="#ffffff15"
    )

    # 제목을 여러 줄로 분리 (이모지 포함 문자 제거)
    safe_title = "".join(c for c in title if ord(c) < 0x10000)
    max_chars = 16 if is_shorts else 20
    lines = []
    tmp = safe_title
    while len(tmp) > max_chars:
        lines.append(tmp[:max_chars])
        tmp = tmp[max_chars:]
    if tmp:
        lines.append(tmp)

    font_size = 60 if is_shorts else 50
    line_h    = font_size + 18
    for i, line in enumerate(lines[:4]):
        _safe_draw_text(
            draw,
            (int(width * 0.07), y_center + 10 + i * line_h),
            line,
            fill="white",
            font=title_font,
        )

    # 하단 정보 바 (이모지 없이)
    bottom_y = int(height * 0.88)
    draw.rectangle([0, bottom_y, width, height], fill="#00000050")

    from datetime import datetime
    date_str = datetime.now().strftime("%Y.%m.%d")
    _safe_draw_text(draw, (int(width * 0.05), bottom_y + 20), date_str, fill="#ffffffcc", font=meta_font)

    img.save(save_path, quality=95)
    return True


def collect_images(news_list):
    """
    각 뉴스에 맞는 이미지를 수집합니다.
    Returns: list of {shorts_path, longform_path, news_index}
    """
    os.makedirs("output/images", exist_ok=True)
    images = []

    for i, news in enumerate(news_list):
        title = news["title"]
        keywords = news.get("keywords", [])
        
        # 검색어 구성
        primary_keyword = keywords[0] if keywords else "경제"
        query = keyword_to_query(primary_keyword)

        # 숏츠용 이미지 (9:16)
        shorts_img_path = f"output/images/img_{i+1}_shorts.jpg"
        # 롱폼용 이미지 (16:9)
        longform_img_path = f"output/images/img_{i+1}_longform.jpg"

        print(f"     이미지 {i+1}: '{primary_keyword}' 관련...")

        # 1. Unsplash 시도
        success = download_image_unsplash(query, shorts_img_path, SHORTS_WIDTH, SHORTS_HEIGHT)
        if success:
            download_image_unsplash(query, longform_img_path, LONGFORM_WIDTH, LONGFORM_HEIGHT)
            time.sleep(0.5)
        else:
            # 2. Pixabay 시도
            success = download_image_pixabay(query, shorts_img_path, SHORTS_WIDTH, SHORTS_HEIGHT)
            if success:
                download_image_pixabay(query, longform_img_path, LONGFORM_WIDTH, LONGFORM_HEIGHT)
            else:
                # 3. 플레이스홀더 이미지 생성 (항상 성공)
                create_placeholder_image(
                    title, keywords, shorts_img_path,
                    SHORTS_WIDTH, SHORTS_HEIGHT, is_shorts=True
                )
                create_placeholder_image(
                    title, keywords, longform_img_path,
                    LONGFORM_WIDTH, LONGFORM_HEIGHT, is_shorts=False
                )
                print(f"     → 텍스트 이미지 생성 완료")

        images.append({
            "news_index": i,
            "shorts_path": shorts_img_path,
            "longform_path": longform_img_path,
            "title": title,
            "keywords": keywords
        })

    return images


if __name__ == "__main__":
    sample_news = [
        {
            "title": "미 연준, 기준금리 동결",
            "keywords": ["연준", "금리", "인플레이션"]
        }
    ]
    imgs = collect_images(sample_news)
    print(f"생성된 이미지: {imgs}")
