import instaloader 

def main():
    L = instaloader.Instaloader()

    # Login with username and password


    # Load post by shortcode (URL format: https://www.instagram.com/p/CqnlnyUouPe/)
    # ⁠https://www.instagram.com/reel/DKyi_BfRRDn/?igsh=dXh6YmFweHJvZ3k2
    # https://www.instagram.com/reel/DKymZLvSdkA/?igsh=b2Zyb2JhcnNhOW91
    # https://www.instagram.com/reel/DKzfD2-qBSh/?igsh=ZWoxNHlkOWoxeXd4
    # https://www.instagram.com/p/DLPBnZ9uUkj/?utm_source=ig_web_copy_link
    # https://www.instagram.com/shubhamkaroti.fig/reel/C2pNtfVIxdx/
    # https://www.instagram.com/shivamkhodre/reel/DHSsK7NtV_Q/
    # https://www.instagram.com/reel/DLMa69noWxC/?utm_source=ig_web_copy_link

    # shortcode = 'CqnlnyUouPe'
    shortcode ="DLMa69noWxC"
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    post._obtain_metadata()

    profile = post.owner_profile

    print(profile)

    data = {
        "number_of_likes": post.likes,
        "number_of_comments": post.comments,
        "number_of_views": post.video_view_count if post.is_video else None,
        "user_id": post.owner_id,
        "user_username": profile.username,
        "user_full_name": profile.full_name,
        "user_followers": profile.followers,
        "user_followees": profile.followees,
    }

    print(data)

if __name__ == "__main__":
    main()


