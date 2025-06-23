from googleapiclient.discovery import build

api_key = 'AIzaSyDx6PYq0LLXlxdoy5wIk_xla7DiNItZ9mQ'
youtube = build('youtube', 'v3', developerKey=api_key)

video_id = '4XUp3X422OQ'  # Example video

# Get video stats
video_response = youtube.videos().list(
    part='statistics,snippet',
    id=video_id
).execute()

video = video_response['items'][0]
stats = video['statistics']
snippet = video['snippet']

print("Views:", stats.get('viewCount'))
print("Likes:", stats.get('likeCount'))
print("Comments:", stats.get('commentCount'))
print("User ID (Channel ID):", snippet['channelId'])

# Get channel (user) subscriber count
channel_response = youtube.channels().list(
    part='statistics',
    id=snippet['channelId']
).execute()

subs = channel_response['items'][0]['statistics']['subscriberCount']
print("User Followers (Subscribers):", subs)
