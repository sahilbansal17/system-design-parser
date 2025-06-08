import csv
from dataclasses import dataclass, asdict
from googleapiclient.discovery import build
import isodate

CHANNEL_ID = "UC2UXDak6o7rBm23k3Vv5dww"  # Arpit Bhayani's channel ID
API_KEY = "YOUR_API_KEY"  # set your YouTube Data API key here
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


def fetch_videos(channel_id=CHANNEL_ID, api_key=API_KEY):
    """Return metadata for all videos on the channel using YouTube Data API."""
    service = build("youtube", "v3", developerKey=api_key)
    # retrieve the uploads playlist id
    chan_resp = service.channels().list(part="contentDetails", id=channel_id).execute()
    uploads_id = chan_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page = None
    while True:
        pl_request = service.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page,
        )
        pl_response = pl_request.execute()
        ids = [item["contentDetails"]["videoId"] for item in pl_response["items"]]
        if not ids:
            break
        vid_request = service.videos().list(
            part="snippet,contentDetails",
            id=",".join(ids),
            maxResults=50,
        )
        vid_response = vid_request.execute()
        for item in vid_response["items"]:
            videos.append({
                "id": item["id"],
                "title": item["snippet"].get("title", ""),
                "duration": int(isodate.parse_duration(item["contentDetails"].get("duration", "PT0S")).total_seconds()),
            })
        next_page = pl_response.get("nextPageToken")
        if not next_page:
            break
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
    videos = fetch_videos()
    plan = build_plan(videos, DAYS, DAILY_HOURS)
    write_csv(plan)
    print(f"Generated daily plan with {len(plan)} entries")


if __name__ == '__main__':
    main()
