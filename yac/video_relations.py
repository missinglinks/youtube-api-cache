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

class VideoRelations:

    YOUTUBE_VIDEO = "https://www.youtube.com/watch?v={video_id}"
    YOUTUBE_MORE_VIDEOS = "https://www.youtube.com/related_ajax?ctoken={token}"

    def __init__(self, api, proxy=""):
        self.api = api
        self.proxy = proxy


    def _from_frontend(self, video_id):
        """
        Retrieve recommendend videos from frontend (40 videos)
        """
        related_videos = []

        rsp = requests.get(self.YOUTUBE_VIDEO.format(video_id="8GTEHJAZvjI"))
        soup = BeautifulSoup(rsp.text, "html.parser")
        button = soup.find("button", {"id": "watch-more-related-button"})
        token = button["data-continuation"]

        for li in soup.find_all("li", {"class":"related-list-item"}):
            link = li.find("a")["href"]
            video_id = link.split("=")[-1].split("&")[0]
            related_videos.append(video_id)

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
