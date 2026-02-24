"""
✍️ 스크립트 생성 모듈 (개선 버전)
- 쇼츠: 3초 안에 훅, 빠른 전개
- 롱폼: 자연스러운 톤, 상세 설명
- 유튜브 스타일의 자연스러운 대본
"""

from datetime import datetime
import os


def format_date_kr():
    """오늘 날짜 한글 포맷"""
    now = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return f"{now.month}월 {now.day}일 {weekdays[now.weekday()]}요일"


def generate_shorts_script(news_list):
    """
    숏츠용 스크립트 (훅이 강하고 빠른 전개)
    3초 안에 시선 사로잡기!
    """
    date_str = format_date_kr()
    
    # 키워드 수집
    all_keywords = []
    for n in news_list:
        all_keywords.extend(n.get("keywords", [])[:1])
    top_keywords = all_keywords[:3]
    
    script = []
    
    # 강력한 오프닝 (3초 이내!)
    script.append({
        "text": f"오늘 꼭 알아야 할 경제 뉴스 3가지!",
        "pause": 0.2,
        "subtitle": f"{date_str} 경제 핵심 뉴스"
    })
    
    # 키워드 미리보기
    kw_text = " ".join([f"#{k}" for k in top_keywords])
    script.append({
        "text": f"{', '.join(top_keywords)}! 지금 바로 시작합니다!",
        "pause": 0.3,
        "subtitle": kw_text
    })
    
    # 각 뉴스 (빠르게!)
    for i, news in enumerate(news_list, 1):
        title = news["title"]
        summary = news["summary"]
        
        # 핵심만 40자로 압축
        core = compress_text(summary, 40)
        
        # 뉴스 제목
        script.append({
            "text": f"{i}번! {title[:20]}",
            "pause": 0.3,
            "subtitle": f"[{i}] {title[:22]}"
        })
        
        # 한 문장 설명
        script.append({
            "text": core,
            "pause": 0.4,
            "subtitle": core[:30]
        })
    
    # 빠른 클로징
    script.append({
        "text": "더 자세한 내용은 영상 설명란 확인! 구독 좋아요!",
        "pause": 0.2,
        "subtitle": "[구독 & 좋아요]"
    })
    
    return script


def generate_longform_script(news_list):
    """
    롱폼용 스크립트 (자연스럽고 친근한 톤)
    """
    date_str = format_date_kr()
    
    script = []
    
    # 자연스러운 인사
    script.append({
        "text": f"안녕하세요! {date_str} 경제 뉴스입니다. "
                f"오늘은 정말 중요한 소식들이 많은데요, "
                f"하나씩 쉽게 풀어서 설명해 드릴게요.",
        "pause": 1.0,
        "subtitle": f"{date_str} 경제 뉴스"
    })
    
    # 각 뉴스 상세
    for i, news in enumerate(news_list, 1):
        title = news["title"]
        summary = news["summary"]
        keywords = news.get("keywords", [])
        
        # 뉴스 소개
        kw_text = " ".join([f"#{k}" for k in keywords[:2]])
        script.append({
            "text": f"자, {i}번째 뉴스입니다. "
                    f"오늘의 키워드는 {keywords[0] if keywords else '이 뉴스'}인데요.",
            "pause": 0.7,
            "subtitle": f"[{i}/{len(news_list)}] {kw_text}"
        })
        
        # 제목
        script.append({
            "text": f"{title} 라는 소식입니다.",
            "pause": 0.6,
            "subtitle": title[:35]
        })
        
        # 본문 (2-3문장으로 나누기)
        sentences = split_sentences(summary)
        for j, sent in enumerate(sentences[:3]):
            pause = 0.8 if j < len(sentences) - 1 else 1.0
            script.append({
                "text": sent,
                "pause": pause,
                "subtitle": sent[:35]
            })
        
        # 간단 정리
        script.append({
            "text": f"정리하면, {keywords[0] if keywords else '이 뉴스'}와 관련해서 "
                    f"주목할 필요가 있겠습니다.",
            "pause": 1.0,
            "subtitle": f"[핵심] {keywords[0] if keywords else ''}"
        })
    
    # 친근한 마무리
    script.append({
        "text": "오늘 경제 뉴스 어떠셨나요? "
                "매일 아침 새로운 소식으로 찾아오고 있으니까 "
                "구독 좋아요 꼭 눌러주시고요, "
                "내일 또 만나요! 감사합니다!",
        "pause": 0.5,
        "subtitle": "[구독하고 내일 또 만나요]"
    })
    
    return script


def compress_text(text, max_len=40):
    """텍스트를 짧게 압축"""
    if not text:
        return ""
    sentences = text.split(". ")
    first = sentences[0].strip()
    if len(first) > max_len:
        return first[:max_len] + "..."
    return first


def split_sentences(text, max_count=3):
    """문장 단위 분리"""
    import re
    sents = re.split(r'[.!?]\s+', text)
    sents = [s.strip() for s in sents if len(s.strip()) > 5]
    return sents[:max_count]


def generate_scripts(news_list):
    """
    숏츠 + 롱폼 스크립트 생성
    """
    shorts = generate_shorts_script(news_list)
    longform = generate_longform_script(news_list)
    
    # 통계
    shorts_text = " ".join([p["text"] for p in shorts])
    longform_text = " ".join([p["text"] for p in longform])
    
    print(f"  ✅ Shorts script: {len(shorts_text)} chars ({len(shorts)} parts)")
    print(f"  ✅ Longform script: {len(longform_text)} chars ({len(longform)} parts)")
    
    # 파일 저장
    os.makedirs("output", exist_ok=True)
    
    with open("output/script_shorts.txt", "w", encoding="utf-8") as f:
        f.write("=== SHORTS SCRIPT ===\n\n")
        for i, p in enumerate(shorts, 1):
            f.write(f"[{i}] {p['subtitle']}\n")
            f.write(f"    {p['text']}\n\n")
    
    with open("output/script_longform.txt", "w", encoding="utf-8") as f:
        f.write("=== LONGFORM SCRIPT ===\n\n")
        for i, p in enumerate(longform, 1):
            f.write(f"[{i}] {p['subtitle']}\n")
            f.write(f"    {p['text']}\n\n")
    
    return {"shorts": shorts, "longform": longform}


if __name__ == "__main__":
    test_news = [{
        "title": "미 연준, 기준금리 동결",
        "summary": "미국 연준이 기준금리를 현행 수준으로 유지했습니다.",
        "keywords": ["연준", "금리"],
        "source": "test"
    }]
    
    scripts = generate_scripts(test_news)
    print("\n=== SHORTS ===")
    for p in scripts["shorts"]:
        print(f"{p['text']}")
