"""Build a public pointer or refresh the assistant's private pose snapshot."""
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


def discover():
    page = fetch(SITE).decode()
    path = re.search(r'["\'](/assets/poses\.[a-zA-Z0-9]+\.json)["\']', page)
    if not path:
        raise ValueError("PoseWear 首页缺少姿势目录链接")
    return urljoin(SITE, path[1])


def refresh(mode, destination, pointer):
    url = json.loads(fetch(pointer))["catalog_url"] if pointer else discover()
    if not re.fullmatch(re.escape(SITE) + r"assets/poses\.[a-zA-Z0-9]+\.json", url):
        raise ValueError("无效的上游目录地址")
    rows = json.loads(fetch(url))
    poses = []
    ids = set()
    for row in rows:
        key = row["id"]
        if key in ids or not re.fullmatch(r"[\w-]+", key) or not row["angles"]:
            raise ValueError("姿势 ID 重复、无效或缺少视角")
        ids.add(key)
        angles = []
        for angle in row["angles"]:
            if not re.fullmatch(r"p/i/[\w./-]+\.webp", angle["i"]):
                raise ValueError("未知预览图路径")
            angles.append(dict(zh=angle["zh"], en=angle["en"], image=urljoin(SITE, angle["i"])))
        poses.append(dict(id=key, zh=row["zh"], en=row["en"], category=row["cat"],
                          source=urljoin(SITE, f"pose/{key}/"), angles=angles))
    if not poses or not fetch(poses[0]["angles"][0]["image"]).startswith(b"RIFF"):
        raise ValueError("姿势目录为空或首张预览图无效")
    result = dict(version=1, catalog_url=url) if mode == "pointer" else poses
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, delete=False, mode="w", encoding="utf8") as tmp:
        json.dump(result, tmp, ensure_ascii=False)
    Path(tmp.name).replace(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["pointer", "snapshot"])
    parser.add_argument("destination", type=Path)
    parser.add_argument("--pointer", help="已部署的 Pages JSON 地址")
    args = parser.parse_args()
    refresh(args.mode, args.destination, args.pointer)
