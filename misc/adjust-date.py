import os
from plexapi.server import PlexServer

videos = []

baseurl = 'http://plex.int.stangl.co.za:32400/'
token = os.environ.get('PLEX_TOKEN')

if not token:
    raise EnvironmentError("Environment variable 'PLEX_TOKEN' is not set.")

plex = PlexServer(baseurl, token)
library = plex.library.section("Movies")

for video in videos:
    video = library.get(title=video)
    updates = {"addedAt.value": "2022-01-01 11:19:43"}
    video.edit(**updates)