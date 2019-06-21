"""
Simple wrapper for youtube data api
"""

from apiclient.discovery import build

class YouTubeApi:

    def __init__(self, config):

        self._api_keys = config["youtube_api_keys"]
        self._current_api_key = self._api_keys[0]
    
        self._yt = build("youtube", "v3", developerKey=self._current_api_key)

    def channel_id_by_username(self, username):
        """
        Returns channel id for channel with username :username:
        """
        meta = self._yt.channels().list(
            part="id",
            forUsername=username,
        ).execute()  
        try:
            return meta["items"][0]["id"]
        except:
            return None       

    def channel_data(self, channel_id):
        """
        Returns all publicly available metadata for :channel_id:
        """
        meta = self._yt.channels().list(
            part="id,snippet,contentDetails,brandingSettings,localizations,statistics,status,topicDetails",
            id=channel_id,
        ).execute()  
        try:
            return meta["items"][0]
        except:
            print("channel <{}> metadata not available found".format(channel_id))
            return None

    def video_data(self, video_id):
        """
        Returns all publicly available metadata for :video_id:
        """
        meta = self._yt.videos().list(
            part="id,snippet,contentDetails,liveStreamingDetails,statistics",
            id=video_id
        ).execute()
        try:
            return meta["items"][0]
        except:
            print("video {} metada not available".format(video_id))
            return None


    def related_videos(self, video_id):
        related_videos = []
        next_page = None
        while True:

            related = self._yt.search().list(
                type="video",
                part="id",
                maxResults=50,
                relatedToVideoId=video_id,
                pageToken=next_page
            ).execute()

            related_videos += related["items"]
            if "nextPageToken" in related and len(related["items"]) > 0:
                next_page = related["nextPageToken"]
            else:
                break 
        return  [ x["id"]["videoId"] for x in related_videos ] 

    def uploaded_videos(self, channel_id):
        uploads = self.channel_data(channel_id)["contentDetails"]["relatedPlaylists"]["uploads"]
        video_ids = []
        next_page = None
        while True:

            cmd = self._yt.playlistItems().list(
                playlistId=uploads,
                part="snippet,status",
                maxResults=50,
                pageToken=next_page
            )
            playlist_page = youtube_api_call(cmd)

            video_ids += [ x["snippet"]["resourceId"]["videoId"] for x in playlist_page["items"] ]
            
            if "nextPageToken" in playlist_page:
                next_page = playlist_page["nextPageToken"]
            else:
                break
        return video_ids