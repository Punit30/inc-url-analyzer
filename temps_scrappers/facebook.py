# from facebook_scraper import get_posts
# import yt_dlp
# import re

# def extract_post_id_from_url(url: str) -> str:
#     """
#     Extract post ID or video ID from Facebook post/reel/video URL.
#     """
#     import re

#     # Pattern 1: facebook.com/{page}/posts/{post_id}
#     match = re.search(r'/posts/(\d+)', url)
#     if match:
#         return match.group(1)

#     # Pattern 2: facebook.com/story.php?story_fbid={post_id}&id={page_id}
#     match = re.search(r'story_fbid=(\d+)', url)
#     if match:
#         return match.group(1)

#     # Pattern 3: facebook.com/{page}/videos/{video_id}
#     match = re.search(r'/videos/(\d+)', url)
#     if match:
#         return match.group(1)

#     # ✅ Pattern 4: facebook.com/reel/{video_id}
#     match = re.search(r'/reel/(\d+)', url)
#     if match:
#         return match.group(1)

#     return None


# def get_facebook_post_data(post_url: str):
#     post_id = extract_post_id_from_url(post_url)
#     if not post_id:
#         raise ValueError("Could not extract post ID from URL.")

#     # facebook-scraper only supports page-name feed scanning,
#     # so we use yt-dlp for video or fallback to scraping page if needed

#     data = {
#         "post_url": post_url,
#         "text": None,
#         "likes": None,
#         "comments": None,
#         "shares": None,
#         "views": None
#     }

#     try:
#         # Try yt-dlp for video posts — works even if it's not a video
#         with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
#             info = ydl.extract_info(post_url, download=False)
#             data.update({
#                 "text": info.get("description"),
#                 "views": info.get("view_count"),
#                 "likes": info.get("like_count"),
#                 "comments": info.get("comment_count"),
#                 "uploader": info.get("uploader"),
#             })
#             return data
#     except Exception as e:
#         pass  # fallback to facebook-scraper

#     # Fallback to facebook-scraper (slower, page feed required)
#     print("Trying fallback scraping...")

#     # You need the page name to search posts
#     match = re.search(r'facebook\.com/([^/?&]+)', post_url)
#     if not match:
#         raise ValueError("Could not extract page name.")

#     page_name = match.group(1)
    
#     for post in get_posts(page_name, pages=5):
#         if str(post.get("post_id")) == post_id:
#             data.update({
#                 "text": post.get("text", "")[:150],
#                 "likes": post.get("likes"),
#                 "comments": post.get("comments"),
#                 "shares": post.get("shares"),
#             })
#             return data
    
#     return {"error": "Post not found."}

# import re

# def parse_reel_stats_from_uploader(uploader: str):
#     """
#     Extracts views and likes from uploader string, e.g.
#     '411K views · 1K reactions | Title | Page Name'
#     """
#     views = None
#     likes = None

#     if uploader:
#         views_match = re.search(r'([\d,.KMB]+)\s+views', uploader)
#         likes_match = re.search(r'([\d,.KMB]+)\s+reactions', uploader)

#         def parse_num(s):
#             s = s.replace(',', '')
#             if 'K' in s:
#                 return int(float(s.replace('K', '')) * 1_000)
#             elif 'M' in s:
#                 return int(float(s.replace('M', '')) * 1_000_000)
#             elif 'B' in s:
#                 return int(float(s.replace('B', '')) * 1_000_000_000)
#             return int(s)

#         if views_match:
#             views = parse_num(views_match.group(1))
#         if likes_match:
#             likes = parse_num(likes_match.group(1))

#     return views, likes


# post_url = "https://www.facebook.com/reel/1197337455481587"
# data = get_facebook_post_data(post_url)
# print(data)


import yt_dlp
import re

def parse_reel_stats_from_uploader(uploader: str):
    """
    Extracts view count and like count (reactions) from uploader string like:
    '411K views · 1K reactions | Some title | Page Name'
    """
    views = None
    likes = None

    if uploader:
        views_match = re.search(r'([\d,.KMB]+)\s+views', uploader)
        likes_match = re.search(r'([\d,.KMB]+)\s+reactions', uploader)

        def parse_num(s):
            s = s.replace(',', '')
            if 'K' in s:
                return int(float(s.replace('K', '')) * 1_000)
            elif 'M' in s:
                return int(float(s.replace('M', '')) * 1_000_000)
            elif 'B' in s:
                return int(float(s.replace('B', '')) * 1_000_000_000)
            return int(s)

        if views_match:
            views = parse_num(views_match.group(1))
        if likes_match:
            likes = parse_num(likes_match.group(1))

    return views, likes

def get_facebook_reel_data(post_url: str):
    """
    Fetches views, likes, comments, and description from a public Facebook Reel using yt-dlp
    """
    data = {
        "post_url": post_url,
        "text": None,
        "likes": None,
        "comments": None,
        "shares": None,
        "views": None,
        "uploader": None
    }

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(post_url, download=False)
            print(info.__dict__)

            # Parse stats from uploader text
            uploader_text = info.get("uploader", "")
            views, likes = parse_reel_stats_from_uploader(uploader_text)

            data.update({
                "text": info.get("description"),
                "views": views or info.get("view_count"),
                "likes": likes or info.get("like_count"),
                "comments": info.get("comment_count"),
                "shares": None,  # Not available for reels
                "uploader": uploader_text,
            })

    except Exception as e:
        print("Error extracting Facebook reel:", str(e))

    return data

# Example usage
if __name__ == "__main__":
    post_url = "https://www.facebook.com/reel/19HCHSBaQR/"
    result = get_facebook_reel_data(post_url)
    print(result)
