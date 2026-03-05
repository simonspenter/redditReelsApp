import shutil
from pathlib import Path
from dotenv import load_dotenv

from services.upload_service import upload_to_azure
from services.publish_fb_service import publish_to_facebook

load_dotenv()

READY_DIR = Path("output-content") / "ready"
POSTED_DIR = Path("output-content") / "posted"
FAILED_DIR = Path("output-content") / "failed"

for d in (READY_DIR, POSTED_DIR, FAILED_DIR):
    d.mkdir(parents=True, exist_ok=True)

def find_oldest_job() -> Path | None:
    jobs = [p for p in READY_DIR.iterdir() if p.is_dir()]
    if not jobs:
        return None
    return min(jobs, key=lambda p: p.stat().st_mtime)

def find_mp4(job_dir: Path) -> Path:
    mp4s = sorted(job_dir.glob("*.mp4"))
    if not mp4s:
        raise FileNotFoundError(f"No .mp4 file found in: {job_dir}")
    return mp4s[0]

def read_caption(job_dir: Path) -> str:
    p = job_dir / "caption.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return "New video 👇"

def move_job(job_dir: Path, destination_root: Path) -> Path:
    dest = destination_root / job_dir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(job_dir), str(dest))
    return dest

def main():
    job_dir = find_oldest_job()
    if not job_dir:
        print("✅ No jobs in output-content/ready. Nothing to post.")
        return

    print(f"🎯 Posting job: {job_dir.name}")

    video_path = find_mp4(job_dir)
    caption = read_caption(job_dir)

    try:
        # Always upload to Azure for Meta fetching (use SAS for safety)
        video_url = upload_to_azure(str(video_path), public=False)

        # Publish to Facebook
        result = publish_to_facebook(video_url, caption)
        print("✅ Facebook published:", result)

        # Optional: store/overwrite video_url.txt for recordkeeping
        (job_dir / "video_url.txt").write_text(video_url, encoding="utf-8")

        move_job(job_dir, POSTED_DIR)
        print("📦 Moved job to output-content/posted")

    except Exception as e:
        print("❌ Posting failed:", repr(e))
        move_job(job_dir, FAILED_DIR)
        print("📦 Moved job to output-content/failed")

if __name__ == "__main__":
    main()
