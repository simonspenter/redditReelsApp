"""
test_azure_access.py

Uploads a local video to Azure Blob Storage and prints:
- a "public" URL (no SAS query params)
- a SAS URL (time-limited signed URL)

Then it optionally tests whether each URL is readable via HTTP GET.

Usage:
    python test_azure_access.py "C:\\path\\to\\video.mp4"

Or edit DEFAULT_VIDEO_PATH below and just run:
    python test_azure_access.py
"""

import sys
import os
import requests
from dotenv import load_dotenv

# Adjust this import to match your project structure:
# If upload_service.py sits next to this file, this will work as-is.
from services.upload_service import upload_to_azure

load_dotenv()

DEFAULT_VIDEO_PATH = r"C:\Users\Simon\Documents\Kodning\coding projects\content-generator-agent\output-content\2025-09-25_15-03-01\2025-09-25_15-03-01.mp4"


def http_check(url: str) -> tuple[bool, int | None, str | None]:
    """
    Returns (ok, status_code, error_snippet).
    Some blobs may redirect; allow redirects.
    """
    try:
        r = requests.get(url, stream=True, allow_redirects=True, timeout=30)
        # Read a tiny bit so we know it actually responds with body
        _ = next(r.iter_content(chunk_size=1024), b"")
        return (200 <= r.status_code < 300, r.status_code, None)
    except Exception as e:
        return (False, None, str(e)[:200])


def main():
    video_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VIDEO_PATH

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    print(f"🎬 Using video: {video_path}")

    print("\n--- Upload #1: public=True (no SAS in URL) ---")
    public_url = upload_to_azure(video_path, public=True)
    print("PUBLIC URL:")
    print(public_url)

    print("\n--- Upload #2: public=False (SAS URL) ---")
    sas_url = upload_to_azure(video_path, public=False)
    print("SAS URL:")
    print(sas_url)

    print("\n--- Quick HTTP checks (from this machine) ---")
    ok, code, err = http_check(public_url)
    print(f"PUBLIC check: ok={ok}, status={code}, err={err}")

    ok, code, err = http_check(sas_url)
    print(f"SAS check:    ok={ok}, status={code}, err={err}")

    print("\n✅ Next step:")
    print("Open each URL in an INCOGNITO browser window.")
    print("- If PUBLIC URL works in incognito -> container is public (anonymous blob access enabled).")
    print("- If PUBLIC fails but SAS works -> container is private (recommended). Use public=False for Meta posting.")


if __name__ == "__main__":
    main()
