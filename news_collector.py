"""
📰 뉴스 수집 모듈
- 무료 RSS 피드를 활용해 오늘의 경제 뉴스를 수집합니다.
- 네이버 경제, 연합뉴스, 한국경제 RSS 활용
"""

import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

# 무료 경제 뉴스 RSS 피드 목록
RSS_FEEDS = [
    {
        "name": "네이버 경제",
        "url": "https://feeds.feedburner.com/naverfinance"
    },
    {
        "name": "연합뉴스 경제",
        "url": "https://www.yonhapnewstv.co.kr/browse/industry/feed/"
    },
    {
        "name": "한국경제",
        "url": "https://www.hankyung.com/feed/economy"
    },
    {
        "name": "매일경제",
        "url": "https://www.mk.co.kr/rss/30000001/"
    },
    {
        "name": "조선비즈",
        "url": "https://biz.chosun.com/site/data/rss/rss.xml"
    },
]

# 백업: 뉴스 API (무료 tier)
BACKUP_API_URL = "https://newsapi.org/v2/top-headlines"
NEWS_API_KEY = ""  # 무료 API 키 (https://newsapi.org 에서 발급, 하루 100건 무료)


def clean_text(text):
    """HTML 태그 및 특수문자 제거"""
    if not text:
        return ""
    # HTML 태그 제거
    text = BeautifulSoup(text, "html.parser").get_text()
    # 특수문자 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_keywords(title, summary):
    """뉴스에서 핵심 키워드 3개 추출"""
    # 경제 관련 중요 키워드 사전
    economy_keywords = [
        "금리", "주식", "코스피", "코스닥", "달러", "환율", "인플레이션", "물가",
        "GDP", "경기", "수출", "무역", "부동산", "반도체", "삼성", "SK하이닉스",
        "미국", "연준", "Fed", "기준금리", "채권", "ETF", "펀드", "투자",
        "원자재", "석유", "천연가스", "비트코인", "가상화폐", "IPO", "상장"
    ]

    full_text = f"{title} {summary}"
    found = []

    for kw in economy_keywords:
        if kw in full_text and kw not in found:
            found.append(kw)
        if len(found) >= 3:
            break

    # 키워드가 부족하면 제목에서 명사 추출 (간단 방식)
    if len(found) < 3:
        words = re.findall(r'[가-힣]{2,}', title)
        for w in words:
            if w not in found and len(w) >= 2:
                found.append(w)
            if len(found) >= 3:
                break

    return found[:3]


def collect_top_news(max_count=5):
    """
    오늘의 경제 뉴스를 수집합니다.
    Returns: list of dict {title, summary, keywords, source, url}
    """
    news_list = []
    seen_titles = set()

    print(f"  📡 RSS 피드 {len(RSS_FEEDS)}개 확인 중...")

    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:3]:  # 피드당 최대 3개
                title = clean_text(entry.get("title", ""))
                summary = clean_text(entry.get("summary", entry.get("description", "")))
                url = entry.get("link", "")

                # 중복 제거
                if title in seen_titles or len(title) < 5:
                    continue
                seen_titles.add(title)

                # 경제 관련 키워드가 있는 뉴스만 선택
                keywords = extract_keywords(title, summary)

                news_list.append({
                    "title": title,
                    "summary": summary[:300] if summary else title,
                    "keywords": keywords,
                    "source": feed_info["name"],
                    "url": url
                })

                if len(news_list) >= max_count:
                    break

        except Exception as e:
            print(f"  ⚠️  {feed_info['name']} 피드 오류: {e}")
            continue

        if len(news_list) >= max_count:
            break

    # 뉴스를 못 가져왔을 때 샘플 데이터 사용 (테스트용)
    if not news_list:
        print("  ⚠️  RSS 수집 실패. 샘플 데이터로 테스트합니다.")
        news_list = get_sample_news()

    # 상위 3개만 선택 (숏츠용 키워드 3개)
    top_3 = news_list[:3]

    print(f"  ✅ 오늘의 TOP 3 뉴스:")
    for i, news in enumerate(top_3, 1):
        print(f"     {i}. {news['title'][:40]}...")

    return top_3


def get_sample_news():
    """RSS 실패 시 테스트용 샘플 뉴스"""
    return [
        {
            "title": "미 연준, 기준금리 동결 결정... 시장 반응은?",
            "summary": "미국 연방준비제도(Fed)가 이번 FOMC 회의에서 기준금리를 현행 수준으로 유지하기로 결정했습니다. "
                       "이번 결정은 인플레이션 둔화 신호가 나타나고 있지만 아직 목표치인 2%에 도달하지 못했기 때문입니다. "
                       "월가에서는 올해 안에 금리 인하가 시작될 것으로 전망하고 있습니다.",
            "keywords": ["연준", "기준금리", "인플레이션"],
            "source": "샘플 뉴스",
            "url": ""
        },
        {
            "title": "삼성전자, 반도체 업황 회복에 실적 개선 기대감",
            "summary": "삼성전자가 글로벌 반도체 수요 회복에 힘입어 올해 실적이 크게 개선될 것으로 전망됩니다. "
                       "AI 반도체 수요 급증으로 HBM 메모리 판매가 늘고 있으며, D램 가격도 상승세를 보이고 있습니다. "
                       "증권가에서는 올해 영업이익이 30조원을 넘어설 것으로 예상하고 있습니다.",
            "keywords": ["삼성전자", "반도체", "HBM"],
            "source": "샘플 뉴스",
            "url": ""
        },
        {
            "title": "원·달러 환율 1,350원대... 수출 기업 영향은?",
            "summary": "원·달러 환율이 1,350원대에서 등락을 거듭하고 있습니다. "
                       "달러 강세가 지속되면서 수입 물가 상승 압력이 커지고 있으나, "
                       "수출 기업들은 환차익 효과를 누리고 있습니다. "
                       "한국은행은 환율 동향을 예의주시하며 시장 안정화 조치를 준비 중입니다.",
            "keywords": ["환율", "달러", "수출"],
            "source": "샘플 뉴스",
            "url": ""
        }
    ]


if __name__ == "__main__":
    news = collect_top_news()
    for n in news:
        print(f"\n제목: {n['title']}")
        print(f"키워드: {n['keywords']}")
        print(f"출처: {n['source']}")
