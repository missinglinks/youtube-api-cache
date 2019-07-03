"""
YoutubeCache class
Caches all resources available via the rest api in mongodb
"""

from pymongo import MongoClient
from datetime import datetime
from .api import YouTubeApi
from .channel_relations import ChannelRelations
from .video_relations import VideoRelations

class YoutubeCache:

    def __init__(self, config):
        self._client = MongoClient(config["mongodb"]["server"])
        self._api = YouTubeApi(config)

        self.proxy = config["proxy"]

        self._db = self._client[config["mongodb"]["db"]]

        self.channels_db = self._db["channels"]
        self.slugs_db = self._db["slugs"]
        self.channel_relations_db = self._db["channel_relations"]
        self.videos_db = self._db["videos"]

    def slug_to_channel_id(self, slug, refresh):
        """
        Returns YouTube channel ID for :slug:
        """
        if "channel/" in slug:
            channel_id = slug.replace("channel/", "").strip()
            return channel_id
        elif "user/" in slug:
            
            doc = self.slugs_db.find_one( { "slug": slug } ) 
            if doc:
                print("channel {} found in cache".format(slug))
                return doc["channel_id"]
            else:
                channel_id = self._api.channel_id_by_username(slug.replace("user/", "").strip())
                timestamp = datetime.now().isoformat()
                data = {
                    "timestamp": timestamp,
                    "slug": slug,
                    "channel_id": channel_id
                }
                self.slugs_db.insert_one( data )
                return channel_id
        else:
            print("invalid slug")
            return None        



    def fetch_channel_data(self, channel_id, refresh):
        """
        Returns channel metadata for Youtube channel with id :channel_id:
        """
        if not refresh:
            doc = self.channels_db.find_one({ "channel_id": channel_id })
        else:
            self.channels_db.delete_one({ "channel_id": channel_id })
            doc = None
        
        if doc:
            print("{} metadata retrieved from cache".format(channel_id))
            del doc["_id"]
            return doc
        else:
            timestamp = datetime.now().isoformat()
            metadata = self._api.channel_data(channel_id)
            payload = {
                "timestamp": timestamp,
                "channel_id": channel_id,
                "data": metadata
            }
            self.channels_db.insert_one(payload)
            del payload["_id"]
            return payload

    def fetch_related_channels(self, channel_id, refresh):
        """
        Returns related, featured and subscribed channels for :channel_id:
        """
        if not refresh:
            doc = self.channel_relations_db.find_one({ "channel_id": channel_id })
        else:
            doc = None
            self.channel_relations_db.delete_one({ "channel_id": channel_id })

        if doc:
            del doc["_id"]
            print("Channel relations for {} fetched from cache".format(channel_id))
            return doc
        else:
            rel = ChannelRelations(channel_id, proxy=self.proxy)
            rel.fetch_channel_relations()
            timestamp = datetime.now().isoformat()
            payload = {
                "timestamp": timestamp,
                "channel_id": channel_id,
                "data": rel.to_json()
            }
            self.channel_relations_db.insert_one(payload)
            del payload["_id"]
            return payload

    def fetch_video_data(self, video_id, refresh):
        if not refresh:
            doc = self.videos_db.find_one({ "video_id": video_id })
        else:
            doc = None
            self.videos_db.delete_one({ "video_id": video_id })
        if doc:
            print("{} metadata retrieved from cache".format(video_id))
            del doc["_id"]
            return doc
        else:
            timestamp = datetime.now().isoformat()
            metadata = self._api.video_data(video_id)
            payload = {
                "timestamp": timestamp,
                "video_id": video_id,
                "data": metadata
            }
            self.videos_db.insert_one(payload)
            del payload["_id"]
            return payload

    def fetch_related_videos(self, video_id, source, refresh):
        """
        Returns recommended/related videos of video :video_id:
        Does not support caching at the moment (not sure if caching is 
        useful in this instance, since)
        """
        rel = VideoRelations(api=self._api)
        related_videos = rel.fetch_related_videos(video_id, source)
        return { "related_videos": related_videos }

    def fetch_uploaded_videos(self, channel_id, refresh):
        uploads = self._api.uploaded_videos(channel_id)
        payload = {
            "timestamp": datetime.now().isoformat(),
            "channel_id": channel_id,
            "uploads": uploads
        }
        return payload
