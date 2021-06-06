import youtube_dl
import requests
import concurrent.futures

class Reddit:

    def set_baseUrl(sub):
        url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/'+sub+'?rtj=only&redditWebClient=web2x&app=web2x-client-production&allow_over18=1&include=identity&sort=new&layout=compact'
        return url

    def set_recUrl(sub, token, dist):
        url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/'+sub+'?rtj=only&redditWebClient=web2x&app=web2x-client-production&allow_over18=1&include=identity&after='+token+'&dist='+str(dist)+'&layout=compact&sort=new'
        return url

    def get_posts(sub, token=None, dist=25):
        if token:
            url = Reddit.set_recUrl(sub, token, dist)
        else:
            url = Reddit.set_baseUrl(sub)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            posts = response.json()
        else:
            print(response.json())
            exit(response.status_code)
        return posts

    def count_posts(sub, token=None, dist=25, count=0, loop=0):
        if token:
            response = Reddit.get_posts(sub, token, dist)
        else:
            response = Reddit.get_posts(sub)
        count = count+(len(response['postIds'])-1)
        loop += 1
        if response['token']:
            print('Accessing page '+str(loop)+'... Total Posts count: '+str(count))
            Reddit.count_posts(sub, response['token'], response['dist'], count, loop)
        else:
            print('Total Posts: '+str(count))

    def download_media(sub, token=None, dist=25):
        if token:
            response = Reddit.get_posts(sub, token, dist)
        else:
            response = Reddit.get_posts(sub)
        Reddit.download_worker(response['posts'], sub)
        if response['token']:
            Reddit.download_media(sub, response['token'], response['dist'])

    def download_worker(posts, sub):
        urls = []
        for key, value in posts.items():
            if value['media']:
                if value['media']['type'] == "image" or value['media']['type'] == "gifvideo":
                    url = value['media']['content']
                    urls.append(url)
                elif value['media']['type'] == "gallery":
                    for gallery_key, gallery_value in value['media']['mediaMetadata'].items():
                        ext = gallery_value['m'].replace("image/", ".")
                        filename = str(gallery_key + ext)
                        url = "https://i.redd.it/" + filename
                        urls.append(url)
                elif value['media']['type'] == "video":
                    video = value['media']['scrubberThumbSource'].split("DASH")
                    url = video[0] + "DASH_" + str(value['media']['height']) + ".mp4"
                    urls.append(url)
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            sub_url = {executor.submit(Reddit.download_me, url, sub) for url in urls}

    def download_me(url, path):
        ydl_opts = {
            'outtmpl': '%s \%(extractor)s-%(id)s-%(title)s.%(ext)s'.replace("%s ", path),
            'ignoreerrors': True,
            'no_warnings': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])