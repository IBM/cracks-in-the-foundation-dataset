#!/usr/bin/env python3
"""Fetch HF publisher-analytics download counts for ibm-research/cif-dataset
and write a small summary JSON consumed by the static site's front-end.

Requires env var HF_TOKEN. Never hardcode the token.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone

import pandas as pd
import requests

ANALYTICS_URL = (
    "https://huggingface.co/organizations/ibm-research/"
    "settings/publisher-analytics/download-breakdown"
)
REPO_NAME = "ibm-research/cif-dataset"
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "data", "downloads.json",
)
REQUEST_TIMEOUT_S = 30
MAX_RETRIES = 3
RETRY_BACKOFF_S = 5


def fetch_csv_bytes(token: str) -> bytes:
    headers = {"Authorization": f"Bearer {token}"}
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(ANALYTICS_URL, headers=headers, timeout=REQUEST_TIMEOUT_S)
        except requests.RequestException as exc:
            last_exc = exc
            print(f"[update_downloads] attempt {attempt} network error: {exc}", file=sys.stderr)
        else:
            if resp.status_code == 200:
                return resp.content
            print(
                f"[update_downloads] attempt {attempt} got HTTP {resp.status_code}: "
                f"{resp.text[:300]!r}",
                file=sys.stderr,
            )
            last_exc = RuntimeError(f"HTTP {resp.status_code}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF_S * attempt)
    raise SystemExit(f"[update_downloads] failed to fetch analytics CSV: {last_exc}")


def compute_summary(csv_bytes: bytes) -> dict:
    df = pd.read_csv(io.BytesIO(csv_bytes))

    required_cols = {"repoName", "timestamp", "downloads"}
    missing = required_cols - set(df.columns)
    if missing:
        raise SystemExit(
            f"[update_downloads] analytics CSV missing expected columns: {sorted(missing)}"
        )

    df_cif = df[df["repoName"] == REPO_NAME].copy()
    if df_cif.empty:
        raise SystemExit(
            f"[update_downloads] no rows found for repoName={REPO_NAME!r}; "
            "refusing to overwrite downloads.json with empty data"
        )

    df_cif["timestamp"] = pd.to_datetime(df_cif["timestamp"])
    total_downloads = int(df_cif["downloads"].sum())
    latest_date = df_cif["timestamp"].max()
    cutoff_date = latest_date - pd.Timedelta(days=30)
    last_30_downloads = int(df_cif[df_cif["timestamp"] >= cutoff_date]["downloads"].sum())

    return {
        "total_downloads": total_downloads,
        "last_30_days_downloads": last_30_downloads,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_json_atomic(data: dict, path: str) -> None:
    out_dir = os.path.dirname(path)
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".downloads-", suffix=".json", dir=out_dir)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def main() -> int:
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("[update_downloads] HF_TOKEN env var is not set", file=sys.stderr)
        return 1

    csv_bytes = fetch_csv_bytes(token)
    summary = compute_summary(csv_bytes)
    write_json_atomic(summary, OUTPUT_PATH)

    print(f"[update_downloads] wrote {OUTPUT_PATH}: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
