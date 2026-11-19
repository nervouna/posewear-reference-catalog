"""Search a private PoseWear snapshot and emit JSON results."""
import argparse
import json
from pathlib import Path


def search(records, query, angle=None, limit=5):
    terms = query.casefold().split()
    results = []
    for record in records:
        fields = ("id", "zh", "en", "category", "title")
        text = " ".join(record.get(field, "") for field in fields).casefold()
        if not all(term in text for term in terms):
            continue
        if angle:
            matches = [view for view in record.get("angles", [])
                       if angle.casefold() in (view["zh"].casefold(), view["en"].casefold())]
            if not matches:
                continue
            record = dict(record, angles=matches)
        results.append(record)
        if len(results) >= limit:
            break
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("query", help="以空格分隔关键词，所有关键词都需匹配")
    parser.add_argument("--angle", help="姿势的完整视角名称，如 侧面 或 side view")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit 必须大于零")
    records = json.loads(args.snapshot.read_text(encoding="utf8"))
    print(json.dumps(search(records, args.query, args.angle, args.limit), ensure_ascii=False))
