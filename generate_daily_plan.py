import csv
from datetime import timedelta
from dataclasses import dataclass, asdict
import yt_dlp

CHANNEL_URL = "https://www.youtube.com/@AsliEngineering/videos"
DAYS = 30  # number of days to complete the plan
DAILY_HOURS = 2  # hours of content per day

@dataclass
class Video:
    title: str
    link: str
    duration: int  # seconds
    tags: str
    highlights: str
    prerequisites: str


def fetch_videos(url=CHANNEL_URL):
    """Fetch videos from the given YouTube channel."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_info = ydl.extract_info(url, download=False)
        for entry in channel_info.get('entries', []):
            if not entry:
                continue
            # Fetch complete info for each video
            video = ydl.extract_info(entry.get('url'), download=False)
            videos.append(video)
    return videos


def infer_tags(title: str) -> str:
    title_lower = title.lower()
    topics = {
        'database': 'database',
        'cache': 'cache',
        'queue': 'queue',
        'design': 'system-design',
        'python': 'python',
    }
    tags = [v for k, v in topics.items() if k in title_lower]
    return ','.join(tags) if tags else 'general'


def infer_highlights(title: str) -> str:
    words = title.split()[:3]
    return ' '.join(words)


def infer_prerequisites(title: str) -> str:
    if 'advanced' in title.lower():
        return 'basic knowledge required'
    return ''


def build_plan(videos, days=DAYS, daily_hours=DAILY_HOURS):
    daily_seconds = daily_hours * 3600
    plan = []
    day = 1
    day_time = 0
    day_count = 0
    for video in videos:
        if day > days:
            break
        duration = video.get('duration') or 0
        if (day_time + duration > daily_seconds and day_count >= 2) or day_time >= daily_seconds:
            day += 1
            day_time = 0
            day_count = 0
            if day > days:
                break
        v = Video(
            title=video.get('title', ''),
            link=f"https://www.youtube.com/watch?v={video.get('id')}",
            duration=duration,
            tags=infer_tags(video.get('title', '')),
            highlights=infer_highlights(video.get('title', '')),
            prerequisites=infer_prerequisites(video.get('title', '')),
        )
        plan.append({'day': day, **asdict(v)})
        day_time += duration
        day_count += 1
    return plan


def write_csv(plan, path='daily_plan.csv'):
    if not plan:
        return
    fieldnames = ['day', 'title', 'link', 'duration', 'tags', 'highlights', 'prerequisites']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in plan:
            writer.writerow(item)


def main():
    videos = fetch_videos(CHANNEL_URL)
    plan = build_plan(videos, DAYS, DAILY_HOURS)
    write_csv(plan)
    print(f"Generated daily plan with {len(plan)} entries")


if __name__ == '__main__':
    main()
