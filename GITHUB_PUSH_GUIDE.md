# GitHub Push 가이드

## 📋 수정된 파일
- `video_maker.py` (자막 강화 버전)

## 🔄 GitHub에 업데이트하는 방법

### 방법 1: Git 명령어 (추천)

1. **Git 설치 확인**
   - Git이 없다면: https://git-scm.com/download/win 에서 설치
   - 명령 프롬프트에서 `git --version` 실행해서 확인

2. **프로젝트 폴더로 이동**
   ```bash
   cd C:\Users\jewin\Desktop\economic_youtube
   ```

3. **변경사항 확인**
   ```bash
   git status
   ```

4. **수정된 파일 추가**
   ```bash
   git add video_maker.py
   ```
   
   또는 모든 변경사항 추가:
   ```bash
   git add .
   ```

5. **커밋 (변경 내용 기록)**
   ```bash
   git commit -m "Fix: 자막이 확실하게 표시되도록 개선"
   ```

6. **GitHub에 푸시**
   ```bash
   git push origin main
   ```
   
   (또는 브랜치가 master라면: `git push origin master`)

---

### 방법 2: GitHub Desktop (GUI)

1. GitHub Desktop 설치: https://desktop.github.com/
2. 저장소 열기: File → Add Local Repository
3. 폴더 선택: `C:\Users\jewin\Desktop\economic_youtube`
4. 왼쪽에서 변경된 파일 확인
5. 하단에 커밋 메시지 입력: "자막 표시 개선"
6. "Commit to main" 버튼 클릭
7. 상단 "Push origin" 버튼 클릭

---

### 방법 3: GitHub 웹사이트 직접 업로드

1. https://github.com/Wintersoldje/ecnomic_youtube 접속
2. `video_maker.py` 파일 클릭
3. 연필 아이콘(Edit) 클릭
4. 전체 내용 삭제 후 새 내용 붙여넣기
5. 하단 "Commit changes" 클릭

---

## 📦 주요 변경 사항

### video_maker.py 개선점
✅ 자막 박스 투명도 증가 (더 진하게)
✅ 텍스트 크기 조정 (숏츠 56px, 롱폼 46px)
✅ 자막 위치 최적화 (하단 고정)
✅ 구간별 자막 매칭 로직 개선
✅ RGB 변환으로 호환성 향상

---

## 🚀 업데이트 후 테스트

push 완료 후 다시 실행:
```bash
python main.py
```

이제 영상에 자막이 선명하게 표시됩니다!

---

## ❓ Git 처음 사용하는 경우

1. **Git 사용자 정보 설정** (최초 1회만)
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **GitHub 인증** (최초 1회만)
   - HTTPS 방식: GitHub 계정으로 로그인
   - SSH 방식: SSH 키 생성 및 등록 필요

---

## 🔍 문제 해결

### "git is not recognized" 오류
→ Git 설치 필요: https://git-scm.com/download/win

### "Permission denied" 오류
→ GitHub 로그인 필요 (HTTPS) 또는 SSH 키 설정 필요

### "conflict" 오류
→ 웹에서 파일을 수정했다면:
```bash
git pull origin main
git push origin main
```

---

도움이 필요하면 언제든 물어보세요! 🙂
