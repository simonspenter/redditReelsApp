import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Import services
from services.story_service import generate_story_and_caption
from services.voice_service import generate_voiceover
from services.thumbnail_service import generate_thumbnail_from_template
from services.video_service import build_final_video
from services.publish_fb_service import publish_to_facebook
from services.publish_insta_service import publish_to_instagram
from services.upload_service import upload_to_azure

import utils.pillow_fix

# =============== SETUP ===============
load_dotenv()
STORY_KEY = os.getenv("OPENAI_STORY_KEY")

client = OpenAI(api_key=STORY_KEY)

OUTPUT_DIR = os.path.join("output-content", "ready")
TEMP_DIR = "temp"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")  # fixed to match services

# Toggle publishing destinations
PUBLISH_TO_FB = True
PUBLISH_TO_IG = False

# =============== MAIN PIPELINE ===============
print("🚀 Starting video generation...")

# Timestamped output folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.join(OUTPUT_DIR, timestamp)
os.makedirs(output_dir, exist_ok=True)
print(f"📂 Output folder: {output_dir}")

# 1. Generate story + caption
story_text, caption_final, teaser = generate_story_and_caption(client, output_dir)

# 2. Generate thumbnail (needed for intro)
template_path = "assets/reddit-thumbnail-template.png"
thumbnail_path = generate_thumbnail_from_template(template_path, caption_final, output_dir)

# 3. Generate voiceover + subtitles
voice_path, audio_clip, teaser_end_time, subtitles_data = generate_voiceover(
    teaser, story_text, client, output_dir, TEMP_DIR
)

# 4. Build video
final_filename = f"{timestamp}.mp4"
final_path = build_final_video(
    output_dir, audio_clip, teaser_end_time, subtitles_data, thumbnail_path, filename=final_filename
)

print(f"✅ Final video saved: {final_path}")

# 4b. Save caption/metadata for the posting job
with open(os.path.join(output_dir, "caption.txt"), "w", encoding="utf-8") as f:
    f.write(caption_final)

with open(os.path.join(output_dir, "video_path.txt"), "w", encoding="utf-8") as f:
    f.write(final_path)

print("📦 Enqueued for posting (ready queue):", output_dir)

# Does NOT upload/post here. Posting will be handled by scheduled job(s).


# 5. Publish
# Upload once to Azure
azure_url = upload_to_azure(final_path, public=False)
print(f"☁️ Video uploaded to Azure: {azure_url}")

# Publish
if PUBLISH_TO_FB:
    publish_to_facebook(azure_url, caption_final)

if PUBLISH_TO_IG:
    publish_to_instagram(azure_url, caption_final)