import os
import requests
from dotenv import load_dotenv

load_dotenv()

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
META_USER_ACCESS_TOKEN = os.getenv("META_USER_ACCESS_TOKEN")

GRAPH = "https://graph.facebook.com/v24.0"
GRAPH_VIDEO = "https://graph-video.facebook.com/v24.0"

def get_page_access_token():
    r = requests.get(
        f"{GRAPH}/me/accounts",
        params={"fields": "id,access_token", "access_token": META_USER_ACCESS_TOKEN},
        timeout=30,
    )
    r.raise_for_status()

    for page in r.json().get("data", []):
        if page["id"] == FB_PAGE_ID:
            return page["access_token"]

    raise RuntimeError("Page not found in /me/accounts. Check FB_PAGE_ID and token.")

def publish_to_facebook(video_url, caption, title=None):
    """
    Publishes a video (already uploaded to Azure Blob) to Facebook Page via file_url.
    """
    page_token = get_page_access_token()

    url = f"{GRAPH_VIDEO}/{FB_PAGE_ID}/videos"
    data = {
        "file_url": video_url,
        "description": caption,
        "access_token": page_token,
    }
    if title:
        data["title"] = title

    response = requests.post(url, data=data, timeout=300)
    response.raise_for_status()

    print("✅ Posted video to Facebook:", response.json())
    return response.json()
