import csv
import os
from dataclasses import dataclass, asdict
from googleapiclient.discovery import build
import isodate

# Set your YouTube Data API key here. You can also set YOUTUBE_API_KEY env var
API_KEY = os.environ.get("YOUTUBE_API_KEY", "API_KEY")

# Channel handle and optional ID
CHANNEL_HANDLE = "@AsliEngineering"
CHANNEL_ID = None  # set to a channel ID string to skip handle resolution

DAYS = 60  # number of days to complete the plan
DAILY_HOURS = 2  # hours of content per day

@dataclass
class Video:
    title: str
    link: str
    duration: int  # seconds
    tags: str
    highlights: str
    prerequisites: str


def resolve_channel_id(handle: str, api_key: str) -> str:
    """Resolve a YouTube channel ID from its handle."""
    service = build("youtube", "v3", developerKey=api_key)
    query = handle[1:] if handle.startswith("@") else handle
    resp = service.search().list(part="snippet", q=query, type="channel", maxResults=1).execute()
    if not resp.get("items"):
        raise RuntimeError(f"Channel not found for handle: {handle}")
    return resp["items"][0]["snippet"]["channelId"]


def fetch_videos(channel_id: str | None = None, api_key: str = API_KEY):
    """Return metadata for all videos on the channel using YouTube Data API."""
    service = build("youtube", "v3", developerKey=api_key)
    if not channel_id:
        channel_id = resolve_channel_id(CHANNEL_HANDLE, api_key)
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
        ids = [item["contentDetails"]["videoId"] for item in pl_response.get("items", [])]
        if not ids:
            break
        vid_request = service.videos().list(
            part="snippet,contentDetails",
            id=",".join(ids),
            maxResults=50,
        )
        vid_response = vid_request.execute()
        for item in vid_response.get("items", []):
            videos.append(
                {
                    "id": item["id"],
                    "title": item["snippet"].get("title", ""),
                    "snippet_tags": item["snippet"].get("tags", []),
                    "duration": int(
                        isodate.parse_duration(item["contentDetails"].get("duration", "PT0S")).total_seconds()
                    ),
                }
            )
        next_page = pl_response.get("nextPageToken")
        if not next_page:
            break
    return videos


def infer_tags(title: str, yt_tags: list[str]) -> str:
    title_lower = title.lower()
    topics = {
        "database": "database",
        "cache": "cache",
        "queue": "queue",
        "design": "system-design",
        "python": "python",
    }
    tags = [v for k, v in topics.items() if k in title_lower]
    for yt_tag in yt_tags:
        lt = yt_tag.lower()
        for key, val in topics.items():
            if key in lt and val not in tags:
                tags.append(val)
    return ",".join(tags) if tags else "general"


def infer_highlights(title: str) -> str:
    words = title.split()[:5]
    return " ".join(words)


def infer_prerequisites(title: str) -> str:
    if "advanced" in title.lower():
        return "basic knowledge required"
    return ""


def build_plan(videos, days: int = DAYS, daily_hours: int = DAILY_HOURS):
    daily_seconds = daily_hours * 3600
    plan = []
    day = 1
    day_time = 0
    day_count = 0
    for video in videos:
        if day > days:
            break
        duration = video.get("duration") or 0
        if (
            (day_time + duration > daily_seconds and day_count >= 2)
            or day_time >= daily_seconds
        ):
            day += 1
            day_time = 0
            day_count = 0
            if day > days:
                break
        v = Video(
            title=video.get("title", ""),
            link=f"https://www.youtube.com/watch?v={video.get('id')}",
            duration=duration,
            tags=infer_tags(video.get("title", ""), video.get("snippet_tags", [])),
            highlights=infer_highlights(video.get("title", "")),
            prerequisites=infer_prerequisites(video.get("title", "")),
        )
        plan.append({"day": day, **asdict(v)})
        day_time += duration
        day_count += 1
    return plan


def write_csv(plan, path: str = "daily_plan.csv"):
    if not plan:
        return
    fieldnames = ["day", "title", "link", "duration", "tags", "highlights", "prerequisites"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in plan:
            writer.writerow(item)


def main():
    videos = fetch_videos(CHANNEL_ID, API_KEY)
    plan = build_plan(videos, DAYS, DAILY_HOURS)
    write_csv(plan)
    print(f"Generated daily plan with {len(plan)} entries")


if __name__ == "__main__":
    main()
