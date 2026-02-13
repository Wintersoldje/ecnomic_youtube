"""
✍️ 스크립트 생성 모듈
- 뉴스를 받아 숏츠(60초)와 롱폼(3~5분) 스크립트를 자동 생성합니다.
- 완전 무료 (AI API 없이 템플릿 방식으로 생성)
"""

from datetime import datetime


def format_date_korean():
    """오늘 날짜를 한국어로 반환"""
    now = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return f"{now.year}년 {now.month}월 {now.day}일 {weekdays[now.weekday()]}요일"


def generate_shorts_script(news_list):
    """
    숏츠용 스크립트 생성 (60초, 빠른 템포)
    3개 뉴스의 핵심만 압축
    """
    date_str = format_date_korean()
    keywords_all = []
    for n in news_list:
        keywords_all.extend(n.get("keywords", [])[:1])
    keywords_all = keywords_all[:3]

    # 오프닝
    script_parts = []
    script_parts.append({
        "text": f"안녕하세요! 오늘 {date_str}, 꼭 알아야 할 경제 뉴스 3가지, 지금 바로 시작합니다!",
        "pause": 0.5,
        "subtitle": f"[{date_str}] 경제 뉴스 TOP 3"
    })

    # 키워드 미리보기
    kw_text = " · ".join([f"#{k}" for k in keywords_all])
    script_parts.append({
        "text": f"오늘의 키워드는! {', '.join(keywords_all)}입니다!",
        "pause": 0.3,
        "subtitle": kw_text
    })

    # 각 뉴스 요약 (뉴스당 약 15초)
    for i, news in enumerate(news_list, 1):
        title = news["title"]
        summary = news["summary"]

        # 요약문을 60자 이내로 압축
        short_summary = summarize_short(summary)

        script_parts.append({
            "text": f"뉴스 {i}번! {title}",
            "pause": 0.4,
            "subtitle": f"[뉴스 {i}] {title[:25]}..."
        })
        script_parts.append({
            "text": short_summary,
            "pause": 0.5,
            "subtitle": short_summary[:40]
        })

    # 클로징
    script_parts.append({
        "text": "더 자세한 내용은 롱폼 영상에서 확인하세요! 구독과 좋아요 꾹! 눌러주세요!",
        "pause": 0.3,
        "subtitle": "[구독 & 좋아요 눌러주세요!]"
    })

    return script_parts


def generate_longform_script(news_list):
    """
    롱폼용 스크립트 생성 (3~5분, 상세한 설명)
    """
    date_str = format_date_korean()

    script_parts = []

    # 인트로
    script_parts.append({
        "text": f"안녕하세요, 매일 경제 뉴스를 쉽고 빠르게 전달해 드리는 채널입니다. "
                f"오늘은 {date_str}, 꼭 알아야 할 경제 뉴스를 하나하나 자세히 살펴보겠습니다. "
                f"끝까지 시청하시면 오늘 경제 흐름이 한눈에 보이실 겁니다!",
        "pause": 1.0,
        "subtitle": f"[{date_str}] 경제 뉴스 분석"
    })

    # 각 뉴스 상세 설명
    for i, news in enumerate(news_list, 1):
        title = news["title"]
        summary = news["summary"]
        keywords = news.get("keywords", [])
        source = news.get("source", "")

        # 섹션 시작
        script_parts.append({
            "text": f"자, 그럼 {i}번째 뉴스부터 살펴보겠습니다. "
                    f"오늘의 핵심 키워드는 {', '.join(keywords[:2])}입니다.",
            "pause": 0.8,
            "subtitle": f"[뉴스 {i}/{len(news_list)}] {'  '.join(['#'+k for k in keywords[:2]])}"
        })

        # 제목 소개
        script_parts.append({
            "text": f"제목은 {title} 인데요.",
            "pause": 0.6,
            "subtitle": title[:45]
        })

        # 본문 설명
        sentences = split_into_sentences(summary)
        for j, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            script_parts.append({
                "text": sentence,
                "pause": 0.7 if j < len(sentences) - 1 else 1.0,
                "subtitle": sentence[:45]
            })

        # 핵심 정리
        script_parts.append({
            "text": f"정리하자면, {title[:20]}에 대해서 가장 중요한 포인트는 {keywords[0] if keywords else '이 뉴스'}와 관련된 변화를 주목해야 한다는 것입니다.",
            "pause": 1.2,
            "subtitle": f"[핵심] {keywords[0] if keywords else ''}의 변화에 주목!"
        })

    # 마무리 & 전망
    script_parts.append({
        "text": "오늘 경제 뉴스, 어떠셨나요? 매일 아침 중요한 경제 소식을 빠르게 정리해 드리고 있으니, "
                "구독 버튼을 눌러두시면 놓치지 않을 수 있습니다. "
                "좋아요와 댓글도 큰 힘이 됩니다. 내일도 더 알찬 소식으로 찾아오겠습니다. 감사합니다!",
        "pause": 0.5,
        "subtitle": "[구독] 매일 경제 뉴스 받아보세요!"
    })

    return script_parts


def summarize_short(text, max_len=80):
    """텍스트를 짧게 요약 (숏츠용)"""
    if not text:
        return ""
    # 첫 문장만 사용
    sentences = text.split(". ")
    first = sentences[0].strip()
    if len(first) > max_len:
        return first[:max_len] + "..."
    return first


def split_into_sentences(text, max_sentences=4):
    """문장 단위로 분리"""
    import re
    sentences = re.split(r'(?<=[.!?])\s+|(?<=다\.)\s+|(?<=요\.)\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences[:max_sentences]


def generate_scripts(news_list):
    """
    숏츠와 롱폼 스크립트를 모두 생성합니다.
    Returns: {shorts: [...], longform: [...]}
    """
    shorts = generate_shorts_script(news_list)
    longform = generate_longform_script(news_list)

    # 스크립트 미리보기
    shorts_text = " ".join([p["text"] for p in shorts])
    longform_text = " ".join([p["text"] for p in longform])

    print(f"  ✅ 숏츠 스크립트: 약 {len(shorts_text)}자 ({len(shorts)}개 파트)")
    print(f"  ✅ 롱폼 스크립트: 약 {len(longform_text)}자 ({len(longform)}개 파트)")

    # 스크립트 파일로 저장 (참고용)
    os.makedirs("output", exist_ok=True)
    with open("output/script_shorts.txt", "w", encoding="utf-8") as f:
        for part in shorts:
            f.write(f"[자막] {part['subtitle']}\n")
            f.write(f"[음성] {part['text']}\n\n")

    with open("output/script_longform.txt", "w", encoding="utf-8") as f:
        for part in longform:
            f.write(f"[자막] {part['subtitle']}\n")
            f.write(f"[음성] {part['text']}\n\n")

    return {"shorts": shorts, "longform": longform}


import os

if __name__ == "__main__":
    # 테스트
    sample_news = [
        {
            "title": "미 연준, 기준금리 동결 결정",
            "summary": "미국 연방준비제도가 기준금리를 현행 수준으로 유지했습니다. 인플레이션 둔화 신호가 나타나고 있습니다.",
            "keywords": ["연준", "기준금리", "인플레이션"],
            "source": "테스트"
        }
    ]
    scripts = generate_scripts(sample_news)
    print("\n--- 숏츠 스크립트 미리보기 ---")
    for p in scripts["shorts"]:
        print(f"음성: {p['text']}")
        print(f"자막: {p['subtitle']}\n")
