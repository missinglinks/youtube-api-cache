"""
VideoRelations class

Fetched recommended videos for a specific YouTube video.
Recommended videos can either be retrieved via the data API or the 
browser frontend.
"""

from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
import requests
import time
import re

class VideoRelations:

    YOUTUBE_VIDEO = "https://www.youtube.com/watch?v={video_id}"
    YOUTUBE_MORE_VIDEOS = "https://www.youtube.com/related_ajax?ctoken={token}"

    def __init__(self, api, proxy=""):
        self.api = api
        self.proxy = proxy

    def _normalize_name(self, name):
        split = "\\&*\"({[]})./!+?"
        for c in split:
            if name.find(c) == 0:
                name = name[1:]
            
            name = name.split(c)[0]
        return name

    def _parse_channel_id(self, html, channel_name):
        print(channel_name)
        #name = self._normalize_name(channel_name)
        #name = re.escape(channel_name)
        name = self._normalize_name(channel_name)
        print(name)
        res = s = re.search(
            r'text\\":\\".?.?{}.*?browseId\\":\\"(.*?)\\"'.format(name),
            html)
        channel_id = res.group(1)
        return channel_id


    def _from_frontend(self, video_id):
        """
        Retrieve recommendend videos from frontend (40 videos)
        """
        related_videos = []
            
        print(video_id)    
        while True:
            try:
                rsp = requests.get(self.YOUTUBE_VIDEO.format(video_id=video_id))
                break
            except:
                print("retry ...")
                time.sleep(2)
                continue
            
        html_text = rsp.text
        soup = BeautifulSoup(rsp.text, "html.parser")
        
        for li in soup.find_all("li", {"class":"related-list-item"}):
            link = li.find("a")["href"]
            video_id = link.split("=")[-1].split("&")[0]

            if len(video_id) != 11:
                continue

            info = li.find("a")

            title = info.find("span", {"class": "title"}).text.strip()

            try:
                channel = li.find("span", {"class": "stat attribution"}).text.strip()
            except:
                print("NO CHANNEL!\n")
                continue
            #channel = info.find("span", {"class": "stat attribution"}).text.strip()

            try:
                count = info.find("span", {"class": "stat view-count"}).text.strip()
            except:
                print("count parse error")
                print(info)
                count = ""

            if "Recommended" in count:
                continue

            channel_id = self._parse_channel_id(html_text, channel)

            related_videos.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "channel": channel,
                    "channel_id": channel_id,
                    "count": count
                })

        button = soup.find("button", {"id": "watch-more-related-button"})
        with open("tmp.txt", "w") as f:
            f.write(rsp.text)

        if not button:
            print("no related button")
            return related_videos        
        token = button["data-continuation"]

        rsp = requests.get(self.YOUTUBE_MORE_VIDEOS.format(token=token))
        data = rsp.json()
        more_soup = BeautifulSoup(data["body"]["watch-more-related"], "html.parser")
        for a in more_soup.find_all("a", { "class": "content-link" }):
            video_id = a["href"].split("?v=")[-1]
            related_videos.append(video_id)

        return related_videos

    def _from_api(self, video_id):
        """
        Retrieve all related videos from the API
        """
        related_videos = self.api.related_videos(video_id)
        return related_videos

    def fetch_related_videos(self, video_id, source):
        if source == "frontend":
            related_videos = self._from_frontend(video_id)
            return related_videos
        elif source == "api":
            related_videos = self._from_api(video_id)
            return related_videos
