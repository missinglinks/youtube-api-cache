"""
YAC - A simple youtube wrapper as rest api with caching 
"""


from flask import Flask, request
from flask_restful import Resource, Api

from yac import load_config
from yac.channel_relations import ChannelRelations
from yac.cache import YoutubeCache

CONFIG_FILE = "config.yaml"

app = Flask(__name__)
yac = Api(app)

CONFIG = load_config(CONFIG_FILE)
CACHE = YoutubeCache(CONFIG)


class ChannelData(Resource):
    def get(self, channel_id):
        refresh = request.args.get('refresh')
        return CACHE.fetch_channel_data(channel_id, refresh=refresh)

class VideoData(Resource):
    def get(self, video_id):
        refresh = request.args.get('refresh')
        return CACHE.fetch_video_data(video_id, refresh=refresh)        

class SlugConvert(Resource):
    def get(self):
        refresh = request.args.get('refresh')
        slug = request.args.get('slug')
        return {'channel_id': CACHE.slug_to_channel_id(slug, refresh=refresh) }

class RelatedChannels(Resource):
    def get(self, channel_id):
        refresh = request.args.get('refresh')
        return CACHE.fetch_related_channels(channel_id, refresh=refresh)

class RelatedVideos(Resource):
    def get(self, video_id):
        refresh = request.args.get('refresh')
        source = request.args.get('source')
        if not source:
            source = "frontend"
        return CACHE.fetch_related_videos(video_id, source, refresh=refresh)

class Playlist(Resource):
    def get(self, playlist_id):
        refresh = request.args.get('refresh')
        return { 'foo': 'bar' }

class Uploads(Resource):
    def get(self, video_id):
        refresh = requests.args.get('refresh')
        sort = requests.args.get('sort')
        if not sort:
            sort = 'date'
        return { 'foo': 'bar' }


# helpers
yac.add_resource(SlugConvert, '/channelId')
# channel endpoints
yac.add_resource(ChannelData, '/channel/<string:channel_id>')
yac.add_resource(RelatedChannels, '/channel/<string:channel_id>/related')
yac.add_resource(Uploads, '/channel/<string:channel_id>/uploads')
# video endpoints
yac.add_resource(VideoData, '/video/<string:video_id>')
yac.add_resource(RelatedVideos, '/video/<string:video_id>/related')
# playlist enpoints
yac.add_resource(Playlist, '/playlist/<string:playlist_id>')


if __name__ == '__main__':
    app.run(debug=True)