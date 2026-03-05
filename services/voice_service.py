import os
import json
from openai import OpenAI
from moviepy.editor import AudioFileClip, vfx
from utils.subtitles import parse_whisper_segments

def generate_voiceover(teaser, story_text, client: OpenAI, output_dir, temp_dir, speed=1.2, voice="alloy"):
    """
    Generates TTS voiceover with OpenAI (teaser + story),
    applies speed adjustment, then transcribes with Whisper
    so subtitles stay in sync.

    Returns: (voice_path, audio_clip, teaser_end_time, subtitles_data)
    """
    voiceover_text = teaser + ". " + story_text

    # === 1. Generate TTS with OpenAI ===
    raw_path = os.path.join(temp_dir, "voice_raw.mp3")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=voiceover_text
    ) as response:
        response.stream_to_file(raw_path)

    print(f"🎤 Voiceover generated with OpenAI TTS (voice={voice})")

    # === 2. Load & speed up ===
    audio_clip = AudioFileClip(raw_path)
    if speed != 1.0:
        audio_clip = audio_clip.fx(vfx.speedx, speed)
        print(f"⚡ Voiceover playback speed adjusted to {speed}x")

    # Save sped-up version (this is now the "official" file)
    voice_path = os.path.join(temp_dir, "voice_sped.mp3")
    audio_clip.write_audiofile(voice_path, codec="mp3")

    audio_duration = audio_clip.duration
    print(f"🎧 Voiceover duration: {audio_duration:.1f} seconds")

    # === 3. Transcribe sped-up audio with Whisper ===
    print("📝 Transcribing voiceover with Whisper...")
    with open(voice_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json"
        )

    # Save raw Whisper output
    raw_json_path = os.path.join(output_dir, "whisper_raw.json")
    with open(raw_json_path, "w", encoding="utf-8") as jf:
        jf.write(json.dumps(transcript.model_dump(), indent=2, ensure_ascii=False))

    # Get actual teaser duration (first segment)
    all_segments = transcript.segments
    teaser_end_time = all_segments[0]["end"] if all_segments else 2.5

    # Build subtitles only for story part (skip teaser)
    story_segments = all_segments[1:]
    srt_path = os.path.join(temp_dir, "subs.srt")
    subtitles_data = parse_whisper_segments(story_segments, srt_path, min_words=2, max_words=4)

    print("💬 Whisper subtitles generated (story only)")

    return voice_path, audio_clip, teaser_end_time, subtitles_data
