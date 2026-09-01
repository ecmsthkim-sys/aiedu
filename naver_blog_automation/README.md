# 네이버 블로그(보험 콘텐츠) 자동 작성·발행 자동화

무료 API/도구만으로 보험 관련 네이버 블로그 글을 AI가 작성하고, 사람이 한 번 검토한 뒤
자동으로 발행까지 하는 파이프라인입니다. 전체 설계 배경은 `/root/.claude/plans/lexical-pondering-kitten.md`
문서(대화에서 승인된 계획)를 참고하세요.

## 전체 흐름

```
topics.csv에서 주제 하나 뽑기
        ↓
content_generator.py  → Gemini API로 제목/본문/태그 생성
        ↓
image_generator.py    → Pollinations.ai로 대표 이미지 생성
        ↓
notify_review.py      → Slack 알림 + 터미널에서 사람이 y/n 승인
        ↓
naver_publisher.py    → Playwright로 네이버 블로그에 실제 발행
        ↓
topic_queue.py         → topics.csv에 발행완료 기록
```

`main.py`가 이 순서를 그대로 실행합니다.

## 1. 설치

```bash
cd naver_blog_automation
pip install -r requirements.txt
playwright install chromium   # 브라우저 자동화용 크로미움 설치 (무료)
```

## 2. 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채웁니다.

| 변수 | 어디서 발급받나 | 필수 여부 |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey (Google 계정만 있으면 무료 발급) | 필수 |
| `NAVER_BLOG_ID` | 본인 블로그 주소 `blog.naver.com/이 부분` | 필수 |
| `SLACK_WEBHOOK_URL` | https://api.slack.com/apps → Incoming Webhooks (무료) | 선택 (없으면 Slack 알림만 생략) |

`.env`는 절대 git에 커밋하지 마세요 (이미 `.gitignore`에 포함되어 있습니다).

## 3. 주제 목록 준비

`topics.csv`에 원하는 보험 주제를 자유롭게 추가/수정하세요. 형식:

```csv
topic,status,published_date,post_url
자동차보험료 비교하는 법,pending,,
```

`status`가 `pending`인 주제만 순서대로 발행 대상이 됩니다.

## 4. 실행

```bash
python main.py
```

처음 실행 시 네이버 로그인 세션이 없으면 브라우저 창이 뜨고, **직접 로그인**을 요청합니다
(캡차/2단계 인증 때문에 완전 자동 로그인은 지원하지 않습니다). 로그인 후 터미널에서
Enter를 누르면 세션이 `output/naver_session.json`에 저장되어 다음부터는 자동으로 재사용됩니다.

글 작성이 끝나면 터미널에 초안이 출력되고, `y`를 입력해야 실제로 네이버에 발행됩니다.

## 5. 매일 자동 실행하기 (스케줄링)

`crontab.example` 파일을 참고해서 `crontab -e`에 등록하면 매일 정해진 시간에 자동 실행됩니다.
단, 발행 승인은 여전히 터미널 입력(`y/n`)이 필요하므로, 완전 무인화를 원한다면
`notify_review.wait_for_console_approval` 부분을 자신의 승인 방식(예: 파일 플래그, DB 상태값)으로
바꿔야 합니다.

## 꼭 알아두어야 할 것 (리스크)

1. **네이버는 블로그 포스팅 공식 API를 제공하지 않습니다.** 그래서 `naver_publisher.py`는
   브라우저 자동화(Playwright)로 실제 화면을 조작합니다. 네이버가 에디터 화면 구조(UI)를
   바꾸면 이 스크립트의 선택자(selector)가 깨질 수 있어, 실행 전 브라우저 개발자도구(F12)로
   현재 구조를 확인하고 필요 시 `naver_publisher.py`의 선택자를 조정해야 합니다.
2. **과도하게 잦은 자동 발행은 네이버 이용약관상 계정 제재 위험이 있습니다.** 하루 1~2건
   정도로 사람이 쓰는 것과 비슷한 빈도를 유지하는 것을 권장합니다.
3. **보험 상품을 설명/추천하는 콘텐츠는 보험업법·금융소비자보호법상 광고 규정의 적용을
   받을 수 있습니다.** 그래서 이 파이프라인은 발행 전 반드시 사람이 검토(y/n 승인)하도록
   설계되어 있습니다. 이 단계를 생략하지 않는 것을 강력히 권장합니다.
