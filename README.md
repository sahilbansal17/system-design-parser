# system-design-parser

Utilities to gather system design related material. The repository now includes a script that builds a daily learning plan from [Arpit Bhayani's](https://www.youtube.com/@AsliEngineering/videos) YouTube channel using the YouTube Data API.

## Requirements

Install python dependencies using pip:

```bash
pip install -r requirements.txt
```

If package installation fails with a `TypeError` mentioning `canonicalize_version()` when generating metadata, upgrade your packaging tools first:

```bash
python3 -m pip install --upgrade pip setuptools packaging
```

## Usage

1. Obtain a YouTube Data API key. Create a project in [Google Cloud Console](https://console.cloud.google.com/), enable **YouTube Data API v3**, then create an API key.
2. Edit `generate_daily_plan.py` and set `API_KEY` to your key. The script can also look up the channel ID automatically from the handle `@AsliEngineering`.
3. Run the generator:

```bash
python generate_daily_plan.py
```

The script downloads metadata for all available videos on the channel and creates `daily_plan.csv`. The plan spreads the videos across 30 days with about two hours of material per day (customizable in the script variables). Each CSV row contains:

- `day` – day number in the schedule
- `title` – video title
- `link` – URL to the video
- `duration` – length in seconds
- `tags` – inferred topic tags
- `highlights` – short bullet of the video
- `prerequisites` – background required if any

You can adjust the number of days or daily hours by editing `DAYS` and `DAILY_HOURS` at the top of the script.

## Finding a channel ID

If you want to target another channel, open its page in a browser, view page source, and search for `"channelId"`. Copy the value that starts with `UC`. Set this ID in `CHANNEL_ID` or provide the channel handle in `CHANNEL_HANDLE` and the script will resolve it automatically.
