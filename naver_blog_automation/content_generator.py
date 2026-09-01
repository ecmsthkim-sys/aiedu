"""무료 Gemini API로 보험 주제 블로그 글(제목/본문/태그)을 생성한다.

무료 API 키 발급: https://aistudio.google.com/apikey 에서 발급 후
GEMINI_API_KEY 환경변수(.env)로 설정한다.
"""
import json
import os

import google.generativeai as genai

MODEL_NAME = "gemini-1.5-flash"

PROMPT_TEMPLATE = """너는 보험 전문 블로거야. 아래 주제로 네이버 블로그 글을 써줘.

주제: {topic}

작성 규칙:
- 소제목(###) 3~4개, 각 소제목 아래 2~3문단
- 정보 제공 위주로 쓰고 광고처럼 쓰지 마
- 친근한 존댓말 톤 유지
- 특정 보험사나 특정 상품을 단정적으로 추천하지 말고,
  "~할 수 있습니다", "~것이 좋습니다" 같은 완곡한 표현을 사용해
  (보험업법·금융소비자보호법상 광고 규정을 고려한 표현)
- 마지막 줄에 네이버 블로그 태그로 쓸 키워드 5개를 콤마로 구분해서 제시

아래 JSON 형식으로만 응답해줘 (다른 설명 붙이지 마):
{{"title": "글 제목", "body": "마크다운 본문", "tags": ["태그1", "태그2"]}}
"""


def generate_post(topic: str) -> dict:
    """주제를 받아 {title, body, tags} 딕셔너리를 반환한다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다 (.env 확인).")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(
        PROMPT_TEMPLATE.format(topic=topic),
        generation_config={"response_mime_type": "application/json"},
    )
    data = json.loads(response.text)

    if not all(key in data for key in ("title", "body", "tags")):
        raise ValueError(f"예상한 필드(title/body/tags)가 응답에 없습니다: {data}")
    return data


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "자동차보험료 비교하는 법"
    post = generate_post(topic)
    print(json.dumps(post, ensure_ascii=False, indent=2))
