"""topics.csv에서 아직 발행하지 않은 주제를 순서대로 꺼내고, 발행 완료 표시를 남긴다."""
import csv
import datetime
from pathlib import Path

DEFAULT_CSV_PATH = Path(__file__).parent / "topics.csv"
FIELDNAMES = ["topic", "status", "published_date", "post_url"]


def _read_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_rows(csv_path: Path, rows: list[dict]) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def get_next_topic(csv_path: Path = DEFAULT_CSV_PATH) -> str | None:
    """status가 pending인 첫 번째 주제를 반환한다. 없으면 None."""
    rows = _read_rows(csv_path)
    for row in rows:
        if row["status"] == "pending":
            return row["topic"]
    return None


def mark_done(topic: str, post_url: str = "", csv_path: Path = DEFAULT_CSV_PATH) -> None:
    """해당 주제를 발행완료로 표시하고 발행일/URL을 기록한다."""
    rows = _read_rows(csv_path)
    for row in rows:
        if row["topic"] == topic and row["status"] == "pending":
            row["status"] = "done"
            row["published_date"] = datetime.date.today().isoformat()
            row["post_url"] = post_url
            break
    else:
        raise ValueError(f"pending 상태의 주제를 찾을 수 없습니다: {topic}")
    _write_rows(csv_path, rows)


if __name__ == "__main__":
    next_topic = get_next_topic()
    print(f"다음 주제: {next_topic}" if next_topic else "더 이상 발행할 주제가 없습니다.")
