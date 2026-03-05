import os
import random
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips, ImageClip
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.textclip import make_textclip_pillow

VIDEOS_DIR = "stock-videos"

def build_final_video(output_dir, audio_clip, teaser_end_time, subtitles_data, thumbnail_path, filename="final_video.mp4"):
    """
    Builds final video with stock footage, thumbnail popup, subtitles, and audio.
    Returns: final video path.
    """

    # Pick random stock video
    video_files = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(".mp4")]
    if not video_files:
        raise ValueError("No video files found in stock-videos/")
    chosen_file = random.choice(video_files)
    video_path = os.path.join(VIDEOS_DIR, chosen_file)
    video_clip = VideoFileClip(video_path)

    # Ensure enough room for voiceover
    max_start = max(0, video_clip.duration - audio_clip.duration)
    start_time = random.uniform(0, max_start)
    video_clip = video_clip.subclip(start_time, start_time + audio_clip.duration)

    print(f"🎬 Using {chosen_file} from {start_time:.1f}s to {start_time + audio_clip.duration:.1f}s")

    # Resize to 1080x1920
    target_w, target_h = 1080, 1920
    video_clip = video_clip.resize(height=target_h)
    if video_clip.w > target_w:
        x_center = video_clip.w / 2
        crop_x1 = x_center - target_w/2
        crop_x2 = x_center + target_w/2
        video_clip = video_clip.crop(x1=crop_x1, x2=crop_x2)

    # Thumbnail popup overlay
    thumb_clip = (
        ImageClip(thumbnail_path)
        .set_duration(teaser_end_time)
        .resize(width=video_clip.w * 0.8)
        .set_position(("center", "center"))
    )

    intro_with_card = CompositeVideoClip([
        video_clip.subclip(0, teaser_end_time),
        thumb_clip
    ])

    video_with_intro = concatenate_videoclips(
        [intro_with_card, video_clip.subclip(teaser_end_time)],
        method="compose"
    )

    # Subtitles start AFTER teaser
    generator = lambda txt: make_textclip_pillow(txt, size=video_with_intro.size)
    sub_start_time = max(0, teaser_end_time - 2)  # start a little earlier
    sub = SubtitlesClip(subtitles_data, generator).set_start(sub_start_time)


    # Combine everything
    final = CompositeVideoClip([video_with_intro, sub.set_pos(("center", 0.25 * video_with_intro.h))])
    final = final.set_audio(audio_clip)

    # Trim to max 60s
    max_duration = min(audio_clip.duration, 45)
    final = final.subclip(0, max_duration)

    # Use provided filename
    final_path = os.path.join(output_dir, filename)
    final.write_videofile(final_path, codec="libx264", audio_codec="aac")
    return final_path
