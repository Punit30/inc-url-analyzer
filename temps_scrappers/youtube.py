import re
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build

api_key = 'AIzaSyDx6PYq0LLXlxdoy5wIk_xla7DiNItZ9mQ'
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_video_id(url: str) -> str:
    """
    Extracts YouTube video ID from any YouTube URL format
    """
    parsed_url = urlparse(url)

    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/embed/')[1]
        elif parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/shorts/')[1]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path.lstrip('/')

    return None


def fetch_youtube_data(video_url: str):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Video data
    video_response = youtube.videos().list(
        part='statistics,snippet',
        id=video_id
    ).execute()

    if not video_response['items']:
        raise ValueError("No video found.")

    video = video_response['items'][0]
    stats = video['statistics']
    snippet = video['snippet']
    channel_id = snippet['channelId']

    # Channel data
    channel_response = youtube.channels().list(
        part='statistics,snippet',
        id=channel_id
    ).execute()

    if not channel_response['items']:
        raise ValueError("No channel found.")

    channel = channel_response['items'][0]
    channel_stats = channel['statistics']
    channel_snippet = channel['snippet']

    # Combined Data
    return {
        "video_id": video_id,
        "video_title": snippet.get('title'),
        "views": stats.get('viewCount'),
        "likes": stats.get('likeCount'),
        "comments": stats.get('commentCount'),
        "user_id": channel_id,
        "user_name": channel_snippet.get('title'),
        "user_description": channel_snippet.get('description'),
        "user_subscribers": channel_stats.get('subscriberCount'),
        "user_country": channel_snippet.get('country', 'N/A'),
        "user_published_at": channel_snippet.get('publishedAt')
    }

# -------------------
# 🔍 Example Usage
# -------------------
if __name__ == "__main__":
    video_url = "https://youtu.be/JAmGgadALQQ?si=3uD4EiRtBpyyJ7d5"  # You can use any format: /watch, /shorts, youtu.be
    data = fetch_youtube_data(video_url)

    for k, v in data.items():
        print(f"{k}: {v}")
