# Setup

1. Enable YouTube Data API v3 in your Google API console
2. Get Google API OAuth 2.0 credentials with the scope "youtube.force-ssl"
3. Save client ID and client secret into client_secrets.json (see SAMPLE_client_secrets.json for the format, couple other things that need to be there)
4. `pip install -r requirements.txt`

Probably needs Python 3.something

# Usage

With a playlist.txt file looking like this:
```
https://youtu.be/eB9n7vuPBxk
https://youtu.be/sXoC2fXFGwg
https://youtu.be/pRWh7NaeDlM
https://youtu.be/LkMxDj8qJNQ
https://youtu.be/clYe9ChCuKs
https://youtu.be/qWbVNtdu5dg
https://youtu.be/ivbFTbGQwzY
https://youtu.be/Wi__R7WqB9w
https://youtu.be/CaRXfTXOGJI
https://youtu.be/1b5iBmwbF1k
```

Run `python playlist-maker.py PLAYLIST_ID` where PLAYLIST_ID is the ID of the playlist you wish to add the songs from playlist.txt to.

Console will ask you to load a URL to authorize your YouTube account, and you'll need to copy a code into the console after it's done. Make sure you're signing into the right account that owns the playlist - some Google accounts will have two different YouTube identities and you'll get 403 forbidden playlistItemsNotAccessible

With any luck, it'll add songs to the playlist until it reaches the end of the file or you run out of your quota

```
....
175 eVTXPUF4Oz4


Dam. I failed. <HttpError 403 when requesting https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&alt=json returned "The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.">
Here's the content: b'{\n "error": {\n  "errors": [\n   {\n    "domain": "youtube.quota",\n    "reason": "quotaExceeded",\n    "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n   }\n  ],\n  "code": 403,\n  "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n }\n}\n'
Here's the resp: {'vary': 'Origin, X-Origin', 'content-type': 'application/json; charset=UTF-8', 'date': 'Fri, 20 Mar 2020 12:08:58 GMT', 'expires': 'Fri, 20 Mar 2020 12:08:58 GMT', 'cache-control': 'private, max-age=0', 'x-content-type-options': 'nosniff', 'x-frame-options': 'SAMEORIGIN', 'content-security-policy': "frame-ancestors 'self'", 'x-xss-protection': '1; mode=block', 'server': 'GSE', 'alt-svc': 'quic=":443"; ma=2592000; v="46,43",h3-Q050=":443"; ma=2592000,h3-Q049=":443"; ma=2592000,h3-Q048=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,h3-T050=":443"; ma=2592000', 'transfer-encoding': 'chunked', 'status': '403', 'content-length': '437', '-content-encoding': 'gzip'}


You may have reached your quota for the day. Come back tomorrow.
```
