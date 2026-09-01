"""생성된 초안을 사람이 검토하게 한다.

Slack Incoming Webhook(무료)으로 초안 도착 알림을 보내고,
실제 발행 승인은 터미널에서 사람이 직접 y/n로 확인하게 한다.
(Slack 메시지에 승인 버튼을 다는 것은 별도의 서버가 필요해 이 단계에서는 생략했다.)

Slack Webhook URL 발급: https://api.slack.com/apps → Incoming Webhooks 활성화 (무료)
"""
import os

import requests


def send_slack_notification(topic: str, post: dict) -> None:
    """Slack에 초안 도착 알림을 보낸다. SLACK_WEBHOOK_URL이 없으면 조용히 건너뛴다."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[알림] SLACK_WEBHOOK_URL이 설정되어 있지 않아 Slack 알림을 건너뜁니다.")
        return

    tags = ", ".join(post.get("tags", []))
    message = (
        f"*새 블로그 초안이 도착했습니다*\n"
        f"주제: {topic}\n"
        f"제목: {post['title']}\n"
        f"태그: {tags}\n"
        f"터미널에서 발행 승인을 기다리는 중입니다."
    )
    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()


def wait_for_console_approval(topic: str, post: dict) -> bool:
    """터미널에 초안을 출력하고 사람이 y/n로 발행 여부를 결정하게 한다."""
    print("\n" + "=" * 60)
    print(f"주제: {topic}")
    print(f"제목: {post['title']}")
    print("-" * 60)
    print(post["body"])
    print("-" * 60)
    print(f"태그: {', '.join(post.get('tags', []))}")
    print("=" * 60)

    answer = input("이 글을 네이버 블로그에 발행할까요? (y/n): ").strip().lower()
    return answer == "y"
