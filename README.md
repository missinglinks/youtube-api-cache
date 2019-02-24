# YAC Youtube Api Wrapper with Caching

A REST API that provides easier access to YouTube video and comments data.
Retrieved data will be cached in a mongodb.

## Requriements

* Python 3.6/3.7
* MongoDB

For the moment, the tool only works from English or German speaking areas (becaue of frontend stuff). You need a proxy, if you run it elsewhere.

## Configuration

Create config.yaml:

```
# list of available youtube api keys
youtube_api_keys:
- your_key

# mongodb connection uri
mongodb:
  server: "mongodb://user:pwd@localhost:27017/test"
  db: "test"

proxy: 127.0.0.1:80
```

## Endpoints

### /channelId

Retrieve channel ID from slug.

Parameters:

* slug

Example:

```
GET http://localhost:5000/channelId?slug=user/TheSims
```

### /channel/<channel_id>

Retrieve channel metadata.

Paramters:

* refresh (optional): refresh=1 to retrieve new data and overwrite cache

### /channel/<channel_id>/related

Retrieve featured, related and subscribed channels.

Paramters:

* refresh (optional): refresh=1 to retrieve new data and overwrite cache

### /video/<video_id>

Retrieve video metadata.

Paramters:

* refresh (optional): refresh=1 to retrieve new data and overwrite cache

### /video/<video_id>/related

Retrieve recommended videos for the specified video id.

Paramters:

* source (optional): choose 'frontend' or 'api' as source for the recommmended videos. If the parameter is not set, 'frontend' is used as a default.
* refresh (optional): refresh=1 to retrieve new data and overwrite cache. Default is set to no refresh.
