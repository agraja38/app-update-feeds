#!/usr/bin/env python3
"""Sync the public FetchLater feed from the latest public feed release."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "fetchlater" / "update.json"
REPO = "agraja38/app-update-feeds"
PUBLIC_TAG_PREFIX = "fetchlater-v"


def run_gh(args: list[str]) -> Any:
    result = subprocess.run(
        ["gh", *args],
        check=True,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(result.stdout)


def version_key(tag: str) -> tuple[int, ...]:
    version = tag.removeprefix(PUBLIC_TAG_PREFIX).removeprefix("v")
    return tuple(int(part) for part in version.split("."))


def public_tag(tag: str) -> str:
    if tag.startswith(PUBLIC_TAG_PREFIX):
        return tag
    return f"fetchlater-{tag}"


def latest_tag() -> str:
    configured_tag = os.environ.get("FETCHLATER_TAG", "").strip()
    if configured_tag:
        return public_tag(configured_tag)

    releases = run_gh(
        [
            "release",
            "list",
            "--repo",
            REPO,
            "--limit",
            "100",
            "--json",
            "tagName",
        ]
    )
    fetchlater_releases = [
        release["tagName"]
        for release in releases
        if release["tagName"].startswith(PUBLIC_TAG_PREFIX)
    ]
    if not fetchlater_releases:
        raise RuntimeError(f"No releases found in {REPO}.")
    return max(fetchlater_releases, key=version_key)


def platform_for(name: str) -> str | None:
    if name.endswith((".app.zip", ".dmg")):
        return "macOS"
    if name.endswith(".exe"):
        return "Windows"
    return None


def arch_for(name: str) -> str:
    if "_aarch64" in name or "_arm64" in name:
        return "arm64"
    if "_x64" in name:
        return "x64"
    return "universal"


def download_from(asset: dict[str, Any]) -> dict[str, Any] | None:
    name = asset["name"]
    platform = platform_for(name)
    if platform is None or not name.startswith("FetchLater_"):
        return None

    download = {
        "name": name,
        "platform": platform,
        "arch": arch_for(name),
        "url": asset["url"],
        "sizeBytes": asset["size"],
    }
    if name.endswith((".app.zip", ".exe")):
        download["updateAsset"] = True
    return download


def main() -> None:
    tag = latest_tag()
    release = run_gh(
        [
            "release",
            "view",
            tag,
            "--repo",
            REPO,
            "--json",
            "assets,body,publishedAt,tagName,url",
        ]
    )

    downloads = [
        download
        for asset in release["assets"]
        if (download := download_from(asset)) is not None
    ]
    downloads.sort(
        key=lambda item: (
            ["macOS", "Windows"].index(item["platform"]),
            item["arch"],
            item["name"],
        )
    )

    if not downloads:
        raise RuntimeError(f"No FetchLater release assets found on {tag}.")

    version = release["tagName"].removeprefix(PUBLIC_TAG_PREFIX)
    notes = release.get("body") or f"FetchLater {release['tagName']} release."
    manifest = {
        "version": version,
        "tag": release["tagName"],
        "publishedAt": release["publishedAt"],
        "releaseNotesURL": release["url"],
        "notes": notes,
        "downloads": downloads,
    }

    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEED_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Synced FetchLater feed to {release['tagName']}.")


if __name__ == "__main__":
    main()
