def main():
    import instaloader

    L = instaloader.Instaloader()
    L.login('kush.0911', 'Punit@123')  # Safe store credentials

    post = instaloader.Post.from_shortcode(L.context, 'CqnlnyUouPe')
    print(post.__dict__)
    print({
        "number_of_likes": post.likes,
        "number_of_comments": post.comments,
        "number_of_views": post.video_view_count if post.is_video else None,
        "user_id": post.owner_id,
        "user_followers": post.owner_profile.followers
    })  

    # import requests
    # from bs4 import BeautifulSoup

    # url = "https://www.instagram.com/p/DFsGrPXooLg/"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0'
    # }

    # res = requests.get(url, headers=headers)
    # soup = BeautifulSoup(res.text, 'html.parser')

    # # Try to extract from embedded JSON
    # import re, json
    # shared_data = re.search(r'window\._sharedData = (.*?);</script>', res.text)
    # print(shared_data)
    # if shared_data:
    #     data = json.loads(shared_data.group(1))
    #     post_data = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
    #     print("Likes:", post_data['edge_media_preview_like']['count'])
    #     print("Comments:", post_data['edge_media_to_parent_comment']['count'])
    #     print("Views:", post_data.get('video_view_count', 'N/A'))
    #     print("User ID:", post_data['owner']['id'])
    #     print("Username:", post_data['owner']['username'])



if __name__ == "__main__":
    main()
