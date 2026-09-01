"""API 키 없이 무료로 쓸 수 있는 Pollinations.ai로 블로그 대표 이미지를 생성한다."""
import urllib.parse
from pathlib import Path

import requests

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
DEFAULT_STYLE_SUFFIX = ", flat illustration, minimal, soft colors, no text"


def generate_image(topic: str, out_path: Path, width: int = 1024, height: int = 576) -> Path:
    """주제를 바탕으로 이미지를 생성해 out_path에 저장하고 그 경로를 반환한다."""
    prompt = urllib.parse.quote(topic + DEFAULT_STYLE_SUFFIX)
    url = POLLINATIONS_URL.format(prompt=prompt)

    response = requests.get(url, params={"width": width, "height": height}, timeout=60)
    response.raise_for_status()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(response.content)
    return out_path


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "자동차보험료 비교하는 법"
    saved_to = generate_image(topic, Path(__file__).parent / "output" / "sample_image.png")
    print(f"이미지 저장됨: {saved_to}")
