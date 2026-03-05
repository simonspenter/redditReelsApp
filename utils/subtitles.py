def format_time(seconds: float) -> str:
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def parse_whisper_segments(segments, srt_path: str, min_words=2, max_words=4):
    """
    Break Whisper segments into random 2–4 word chunks with proportional timing.
    """
    import random
    subtitles_data = []
    counter = 1

    with open(srt_path, "w", encoding="utf-8") as f:
        for seg in segments:
            start, end, text = float(seg["start"]), float(seg["end"]), seg["text"].strip()
            words = text.split()
            if not words:
                continue

            duration = end - start
            idx = 0
            while idx < len(words):
                chunk_size = random.randint(min_words, max_words)
                chunk_words = words[idx:idx + chunk_size]
                chunk_text = " ".join(chunk_words)

                chunk_start = start + (idx / len(words)) * duration
                chunk_end = start + ((idx + len(chunk_words)) / len(words)) * duration

                subtitles_data.append(((chunk_start, chunk_end), chunk_text))
                f.write(f"{counter}\n{format_time(chunk_start)} --> {format_time(chunk_end)}\n{chunk_text}\n\n")
                counter += 1
                idx += chunk_size

    return subtitles_data
