from downloader import Reddit

if __name__ == '__main__':
    subreddit = input("Subreddit Name: \n")
    try:
        response = Reddit.download_media(subreddit)
    except Exception as e:
        print(e)
