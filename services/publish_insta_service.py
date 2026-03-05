import os
import requests
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

def publish_to_instagram(video_url, caption):
    """
    Publishes a video (already uploaded to Azure Blob) as an Instagram Reel.
    Requires a public URL (video_url).
    """
    # Step 1: Create media container
    url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    data = {
        "media_type": "VIDEO",
        "video_url": video_url,  # public URL from Azure
        "caption": caption,
        "access_token": META_ACCESS_TOKEN,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    container_id = response.json()["id"]

    # Step 2: Publish container
    publish_url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    publish_data = {
        "creation_id": container_id,
        "access_token": META_ACCESS_TOKEN,
    }

    publish_resp = requests.post(publish_url, data=publish_data)
    publish_resp.raise_for_status()

    print("✅ Posted video to Instagram:", publish_resp.json())
    return publish_resp.json()
