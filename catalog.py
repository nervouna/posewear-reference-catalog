"""Build a public pointer or refresh the assistant's private reference snapshot."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin

SITE = "https://posewear.pages.dev/"


def fetch(url):
    return subprocess.check_output(
        ["curl", "--fail", "--silent", "--show-error", "--location",
         "--max-time", "45", "--retry", "2", url]
    )


KINDS = ("pose", "costume", "portrait")


def discover(kind):
    page = fetch(SITE).decode()
    if kind != "pose":
        bundle = re.search(r'["\'](/assets/app\.[a-zA-Z0-9]+\.js)["\']', page)
        if not bundle:
            raise ValueError("首页缺少应用脚本")
        page = fetch(urljoin(SITE, bundle[1])).decode()
    path = re.search(rf'["\'](/assets/{kind}s\.[a-zA-Z0-9]+\.json)["\']', page)
    if not path:
        raise ValueError("PoseWear 首页缺少目录链接")
    return urljoin(SITE, path[1])


def refresh(mode, destination, pointer, kind="pose"):
    url = json.loads(fetch(pointer))["catalog_url"] if pointer else discover(kind)
    if not re.fullmatch(re.escape(SITE) + rf"assets/{kind}s\.[a-zA-Z0-9]+\.json", url):
        raise ValueError("无效的上游目录地址")
    rows = json.loads(fetch(url))
    records = []
    ids = set()
    for row in rows:
        key = row["id"]
        if key in ids or not re.fullmatch(r"[\w-]+", key):
            raise ValueError("条目 ID 重复或无效")
        ids.add(key)
        record = dict(id=key, zh=row["zh"], en=row["en"], source=urljoin(SITE, f"{kind}/{key}/"))
        records.append(record)
        if kind != "pose":
            prefix = "c" if kind == "costume" else "r"
            if not re.fullmatch(prefix + r"/m/[\w-]+\.webp", row["m"]):
                raise ValueError("未知预览图路径")
            record.update(title=row["ti"], image=urljoin(SITE, row["m"]),
                          category=row["cat"] if kind == "costume" else row["sec"])
            continue
        if not row["angles"]:
            raise ValueError("姿势缺少视角")
        angles = []
        for angle in row["angles"]:
            if not re.fullmatch(r"p/i/[\w./-]+\.webp", angle["i"]):
                raise ValueError("未知预览图路径")
            angles.append(dict(zh=angle["zh"], en=angle["en"], image=urljoin(SITE, angle["i"])))
        record.update(category=row["cat"], angles=angles)
    if not records:
        raise ValueError("目录为空")
    sample = records[0]
    preview = sample["angles"][0]["image"] if kind == "pose" else sample["image"]
    if fetch(preview)[8:12] != b"WEBP":
        raise ValueError("首张预览图无效")
    result = dict(version=1, catalog_url=url) if mode == "pointer" else records
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, delete=False, mode="w", encoding="utf8") as tmp:
        json.dump(result, tmp, ensure_ascii=False)
    Path(tmp.name).replace(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["pointer", "snapshot"])
    parser.add_argument("destination", type=Path)
    parser.add_argument("--pointer", help="已部署的 Pages JSON 地址")
    parser.add_argument("--kind", choices=KINDS, default="pose")
    args = parser.parse_args()
    refresh(args.mode, args.destination, args.pointer, args.kind)
