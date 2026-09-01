"""Playwright로 네이버 블로그에 로그인하고 글을 발행한다.

주의: 네이버 블로그 에디터(스마트에디터 ONE)는 iframe 구조이고 UI가 수시로 바뀐다.
아래 선택자(selector)는 참고용 기준값이며, 실제 사용 전 브라우저 개발자도구(F12)로
직접 확인 후 조정이 필요할 수 있다.

로그인은 캡차/2단계 인증 때문에 완전 자동화가 어려울 수 있어,
최초 1회는 사람이 직접 로그인하게 하고 그 세션(쿠키)을 저장해서 재사용한다.
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

STORAGE_STATE_PATH = Path(__file__).parent / "output" / "naver_session.json"
LOGIN_URL = "https://nid.naver.com/nidlogin.login"


def ensure_logged_in_session() -> None:
    """세션 파일이 없으면 브라우저를 띄워 사람이 직접 로그인하게 하고 세션을 저장한다."""
    if STORAGE_STATE_PATH.exists():
        return

    STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("저장된 네이버 로그인 세션이 없습니다. 브라우저 창에서 직접 로그인해주세요.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)

        input("로그인을 완료한 뒤, 이 터미널에서 Enter를 눌러주세요...")

        context.storage_state(path=str(STORAGE_STATE_PATH))
        browser.close()
    print(f"로그인 세션을 저장했습니다: {STORAGE_STATE_PATH}")


def publish_post(blog_id: str, title: str, body: str, tags: list[str], image_path: Path | None = None) -> str:
    """네이버 블로그에 글을 발행하고 발행된 글 URL을 반환한다."""
    ensure_logged_in_session()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(STORAGE_STATE_PATH))
        page = context.new_page()

        page.goto(f"https://blog.naver.com/{blog_id}")

        # 네이버 블로그 홈은 iframe#mainFrame 안에 실제 콘텐츠가 들어있다.
        main_frame = page.frame_locator("iframe#mainFrame")
        main_frame.get_by_role("link", name="글쓰기").click()
        page.wait_for_timeout(2000)

        # 새 글 작성 시 "이어서 작성하시겠습니까" 같은 팝업이 뜰 수 있어 취소 처리
        cancel_button = page.get_by_role("button", name="취소")
        if cancel_button.is_visible():
            cancel_button.click()

        editor_frame = page.frame_locator("iframe#mainFrame")

        # 제목 입력
        editor_frame.locator(".se-title-text .se-text-paragraph").click()
        editor_frame.locator(".se-title-text .se-text-paragraph").fill(title)

        # 본문 입력 (마크다운 소제목 ### 은 일반 텍스트로 들어가므로 필요 시 서식 지정 로직 보강 필요)
        editor_frame.locator(".se-main-container .se-text-paragraph").first.click()
        for line in body.split("\n"):
            page.keyboard.type(line)
            page.keyboard.press("Enter")

        if image_path is not None:
            # 스마트에디터의 사진 삽입 버튼 → 파일 선택 다이얼로그
            with page.expect_file_chooser() as fc_info:
                editor_frame.get_by_role("button", name="사진").click()
            fc_info.value.set_files(str(image_path))
            page.wait_for_timeout(2000)

        # 발행 버튼 → 태그 입력 → 최종 발행
        editor_frame.get_by_role("button", name="발행").click()
        page.wait_for_timeout(1000)

        tag_input = editor_frame.locator("input.tag_input")
        for tag in tags:
            tag_input.fill(tag)
            tag_input.press("Enter")

        editor_frame.get_by_role("button", name="발행", exact=True).click()
        page.wait_for_timeout(3000)

        post_url = page.url
        browser.close()
        return post_url


if __name__ == "__main__":
    blog_id = os.environ.get("NAVER_BLOG_ID")
    if not blog_id:
        raise RuntimeError("NAVER_BLOG_ID 환경변수가 설정되어 있지 않습니다 (.env 확인).")

    url = publish_post(
        blog_id=blog_id,
        title="테스트 제목",
        body="테스트 본문입니다.",
        tags=["테스트"],
    )
    print(f"발행 완료: {url}")
