"""전체 파이프라인을 순서대로 실행한다.

주제 선택 → AI 글 작성 → AI 이미지 생성 → Slack 알림 + 사람 검토 → 네이버 블로그 발행 → 발행 이력 기록
"""
from pathlib import Path

from dotenv import load_dotenv

import content_generator
import image_generator
import naver_publisher
import notify_review
import topic_queue

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "output"


def run_once() -> None:
    topic = topic_queue.get_next_topic()
    if topic is None:
        print("발행할 주제가 더 이상 없습니다. topics.csv에 주제를 추가해주세요.")
        return

    print(f"[1/5] 주제 선택: {topic}")

    print("[2/5] AI 글 작성 중...")
    post = content_generator.generate_post(topic)

    print("[3/5] AI 이미지 생성 중...")
    image_path = image_generator.generate_image(topic, OUTPUT_DIR / "image.png")

    print("[4/5] 검토 요청 중...")
    notify_review.send_slack_notification(topic, post)
    approved = notify_review.wait_for_console_approval(topic, post)

    if not approved:
        print("발행이 취소되었습니다. 주제는 다음 실행 때 다시 시도됩니다.")
        return

    print("[5/5] 네이버 블로그에 발행 중...")
    blog_id = _require_env("NAVER_BLOG_ID")
    post_url = naver_publisher.publish_post(
        blog_id=blog_id,
        title=post["title"],
        body=post["body"],
        tags=post.get("tags", []),
        image_path=image_path,
    )

    topic_queue.mark_done(topic, post_url)
    print(f"발행 완료: {post_url}")


def _require_env(name: str) -> str:
    import os

    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} 환경변수가 설정되어 있지 않습니다 (.env 확인).")
    return value


if __name__ == "__main__":
    run_once()
