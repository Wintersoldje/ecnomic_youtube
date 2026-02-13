# 📈 경제 유튜브 자동화 시스템

> 매일 경제 뉴스를 자동으로 수집하고, **숏츠** + **롱폼** 영상을 자동으로 만들어 드립니다!

---

## 🗂️ 파일 구조

```
economic_youtube/
├── main.py              ← 메인 실행 파일 (여기서 시작!)
├── news_collector.py    ← 경제 뉴스 RSS 수집
├── script_generator.py  ← 영상 스크립트 자동 생성
├── tts_generator.py     ← 한국어 음성(TTS) 생성
├── image_collector.py   ← 관련 이미지 수집/생성
├── video_maker.py       ← 최종 영상 제작
├── install.bat          ← 최초 1회 설치 (더블클릭)
├── run.bat              ← 매일 실행 (더블클릭)
└── output/              ← 완성된 영상 저장 위치
    ├── shorts_video.mp4     ← 유튜브 숏츠 업로드용
    ├── longform_video.mp4   ← 유튜브 롱폼 업로드용
    ├── script_shorts.txt    ← 숏츠 스크립트 (참고용)
    └── script_longform.txt  ← 롱폼 스크립트 (참고용)
```

---

## 🚀 처음 설치하기

### 필수 조건
- **Python 3.10 이상** 설치 필요 → [python.org](https://python.org)에서 다운로드
- **Windows 10/11** PC

### 설치 순서

**1단계: Python 설치**
1. [https://python.org](https://python.org) 접속
2. 최신 Python 다운로드 및 설치
3. ⚠️ 설치 시 **"Add Python to PATH"** 반드시 체크!

**2단계: ffmpeg 설치** (영상 제작 필수)
```
명령 프롬프트(cmd)를 관리자로 실행 후:
winget install ffmpeg
```
또는 [ffmpeg.org](https://ffmpeg.org) 에서 수동 설치

**3단계: 패키지 설치**
```
install.bat 더블클릭
```

---

## ▶️ 매일 사용하기

```
run.bat 더블클릭
```

또는 명령 프롬프트에서:
```bash
python main.py
```

**약 5~10분 후** `output/` 폴더에 영상 2개가 완성됩니다!

---

## 📱 영상 스펙

| 구분 | 해상도 | 시간 | 특징 |
|------|--------|------|------|
| 숏츠 | 1080 × 1920 (9:16) | 60초 이내 | 1.3배속, 키워드 자막 |
| 롱폼 | 1920 × 1080 (16:9) | 3~5분 | 자연스러운 속도, 상세 자막 |

---

## 🔑 (선택) API 키 설정으로 품질 업그레이드

API 없이도 작동하지만, 아래 무료 API를 설정하면 더 좋은 이미지를 사용할 수 있습니다.

### 이미지 품질 향상 (둘 중 하나만)

**Unsplash API** (무료, 시간당 50회)
1. [https://unsplash.com/developers](https://unsplash.com/developers) 접속
2. 무료 계정 생성 후 Access Key 발급
3. `image_collector.py` 파일 열기
4. `UNSPLASH_ACCESS_KEY = ""` 부분에 키 입력

**Pixabay API** (무료, 하루 100회)
1. [https://pixabay.com/api/docs/](https://pixabay.com/api/docs/) 접속
2. 무료 계정 생성 후 API Key 발급
3. `image_collector.py` 파일에 입력

---

## 🛠️ 문제 해결

### "ModuleNotFoundError" 오류
```
install.bat 를 다시 실행하세요
```

### "ffmpeg not found" 오류
```
cmd 관리자 실행 후:
winget install ffmpeg
```
그 후 PC 재시작

### 뉴스를 가져오지 못할 때
- 인터넷 연결 확인
- 샘플 데이터로 자동 대체되어 테스트 가능

### 음성이 이상할 때
- gTTS는 구글 TTS를 사용하므로 인터넷 필요
- VPN 사용 중이라면 잠시 끄고 시도

---

## 💡 수익화 전략

### 구독자 확보 팁
- **매일 같은 시간** 업로드 (예: 매일 오전 8시)
- 숏츠는 **조회수 증가** → 롱폼 유입 유도
- 영상 설명란에 뉴스 출처 링크 추가
- 해시태그: #경제뉴스 #주식 #재테크 #투자

### 수익화 조건 달성 로드맵
```
구독자 500명 + 최근 90일 조회수 3,000시간
→ 유튜브 파트너 프로그램(YPP) 신청
→ 광고 수익 시작!
```

### 추가 수익원 (나중에 추가 가능)
- 네이버 블로그 + 애드포스트 연동
- 카카오 뷰 크리에이터
- 뉴스레터 구독 (스티비, 메일리)

---

## 📅 자동화 설정 (윈도우 작업 스케줄러)

매일 자동으로 실행하려면:

1. `Windows + R` → `taskschd.msc` 입력
2. "작업 만들기" 클릭
3. 트리거: "매일 오전 7:00"
4. 동작: `run.bat` 파일 실행
5. 완료! 매일 아침 자동으로 영상이 만들어집니다.

---

## ⚖️ 저작권 안내

- 이미지: Unsplash/Pixabay 무료 이미지 (상업적 이용 가능)
- 음성: Google TTS (유튜브 수익화 가능)
- 뉴스 내용: 인용/요약 범위 내 사용 (출처 명시 권장)

---

*Made with ❤️ for Korean Economic YouTubers*
