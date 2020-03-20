# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import sys
import datetime
import json
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


# Get the YouTube video ID from a URL

# initial version: http://stackoverflow.com/a/7936523/617185 \
#    by Mikhail Kashkin(http://stackoverflow.com/users/85739/mikhail-kashkin)

def get_yt_video_id(url):
    """Returns Video_ID extracting from the given url of Youtube
    
    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',
      
      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url
        
    query = urlparse(url)
    
    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0].rstrip()
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2].rstrip()
    elif 'youtu.be' in query.hostname:
        return query.path[1:].rstrip()
    else:
        raise ValueError

def confirm():
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}

    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")

def main():
    if len(sys.argv) != 2:
        print("Please provide playlist ID as the first parameter to the script")
        exit(1)

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_filename = "client_secrets.json"
    session_filename = "session.json"
    playlist_id = sys.argv[1].rstrip()

    print("Get ready to log in with the same Google account that owns this playlist.")
    print("Preparing to add playlist items to https://www.youtube.com/playlist?list=" + playlist_id)
    print("Does this playlist link look right?")
    if not confirm():
        exit(1)
    
    playlist_filename = "playlist.txt"
    added_playlist_filename = "added.txt"

    if os.path.isfile(session_filename):
        print("Loading session")
        with open(session_filename) as session_file:
            info = json.load(session_file)
            credentials = Credentials( 
                token=info['token'],
                refresh_token=info['refresh_token'],
                token_uri=info['token_uri'],
                client_id=info['client_id'],
                client_secret=info['client_secret'],
                scopes=info['scopes'],
            )
            credentials.expiry = datetime.datetime.fromisoformat(info['expiry'])

        if credentials.expired:
            print("Refreshing credentials")
            # don't forget to dump one more time after the refresh
            # also, some file-locking routines wouldn't be needless
            credentials.refresh(Request())
            info = { 
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat(),
            }

            with open(session_filename, 'w') as session_file:
                json.dump(info, session_file)
    else:
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_filename, scopes)
        credentials = flow.run_console()
        session = flow.authorized_session()
        print(session.get('https://www.googleapis.com/userinfo/v2/me').json())

        info = { 
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat(),
        }

        with open(session_filename, 'w') as session_file:
            json.dump(info, session_file)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    with open(playlist_filename) as f:
        i = 0
        for line in f:
            video_id = get_yt_video_id(line)
            with open(added_playlist_filename) as added_playlist_file:
                found = False
                for check_if_already_added in added_playlist_file:
                    #print(check_if_already_added)
                    if line.rstrip() in check_if_already_added:
                        print(i, "Already added", video_id)
                        found = True
            if not found:
                print(i, video_id)
                # exit(1)

                request = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "position": i,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                )
                try:
                    # print(request.body)
                    response = request.execute()

                    print(i, response)

                    if response and 'error' in response:
                        print("Dam. I failed.")
                        exit(1)
                    else:
                        with open(added_playlist_filename, 'a') as added_playlist_file:
                            added_playlist_file.writelines(line)
                except HttpError as e:
                    print(os.linesep)
                    print("Dam. I failed.", e)
                    print("Here's the content:", e.content)
                    print("Here's the resp:", e.resp)
                    print(os.linesep)
                    if "quotaExceeded" in str(e.content):
                        print("You may have reached your quota for the day. Come back tomorrow.")
                        exit(1)
                    elif "Forbidden" in str(e.content):
                        print("Assuming the video was deleted because the account was terminated.")
                        with open(added_playlist_filename, 'a') as added_playlist_file:
                            added_playlist_file.writelines(line.rstrip() + " # 403" + os.linesep)

                    elif e.resp.status != 404:
                        print("Check and see if https://youtu.be/"+video_id+" is available. If not, you will need to manually add that to added.txt to skip it. Otherwise, some other error I can't figure out. Dunno.")
                        exit(1)
                    else:
                        print("This video not found anymore?")
                        with open(added_playlist_filename, 'a') as added_playlist_file:
                            added_playlist_file.writelines(line.rstrip() + " # 404" + os.linesep)

            i = i + 1

if __name__ == "__main__":
    main()