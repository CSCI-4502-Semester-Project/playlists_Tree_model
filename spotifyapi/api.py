import requests
import pprint
import json
import time

def get_user_profile(user_id, authorizer, verbose=False):
    """ Gets the specified user profile.

    Args:
        user_id (str): Username of Spotify user.
        authorizer (SpotifyAuth): Spotify API Authorization module.
        verbose (bool, optional): More detailed logs. Defaults to False.

    Returns:
        [dict, None]: Returns the user profile in dictionary of JSON format as returned by the server. Returns None if request failed.
    """
    while(True): # need to add loop incase of rate limiting, otherwise it shouldn't really be necessary
        spotify_endpoint = 'https://api.spotify.com/v1/users/{user_id}'

        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(spotify_endpoint.format(user_id=user_id), headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 404:
            print('Error. User {user_id} not found.'.format(user_id=user_id))
            return None
        elif response.status_code == 401:
            print('Access token expired, refreshing...')
            authorizer.refresh()
            headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None


def get_user_playlists(user_id, authorizer, verbose=False):
    """ Gets all public playlists from a user.

    Args:
        user_id (str): Username of Spotify user.
        authorizer (SpotifyAuth): Spotify API Authorization module.
        verbose (bool, optional): More detailed logs. Defaults to False.

    Returns:
        [dict, None]: Dictionary containing all of the users public playlists where each subdictionary is in JSON format as returned by the server. Returns None if request failed.
    """
    spotify_endpoint = 'https://api.spotify.com/v1/users/{user_id}/playlists'

    # there's a limit to the number of playlists that can be downloaded at a time
    # keep downloading playlists until we run out (next = null)
    playlists = {'items':None} 
    while True:
        params = {'limit': 50}
        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(spotify_endpoint.format(user_id=user_id), headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if playlists['items'] is None:
                playlists['items'] = data['items']
            else:
                playlists['items'] += data['items']
            
            if data['next'] is None:
                return playlists ## look here for how we get out! ##
            else:
                spotify_endpoint = data['next']
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 404:
            print('Error. User {user_id} not found.'.format(user_id=user_id))
            return None
        elif response.status_code == 401:
            print('Access token expired, refreshing...')
            authorizer.refresh()
            headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None


def track_indexes(track_out, authorizer, verbose=False):
    """ Returns a list of all of the track ID's for a given playlist.

    Args:
        track_out (str): Track GET URL. Found in a playlist's `tracks` field.
        authorizer (SpotifyAuth): Spotify API Authorization module.
        verbose (bool, optional): More detailed logs. Defaults to False.

    Returns:
        [list, None]: Returns a list of all of the track ID's for a given playlist that are not None. Returns None if the request failed.
    """
    href = track_out['href']
    track_ids = [''] * track_out['total']

    index = 0

    while href is not None:
        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(href, headers=headers)

        if response.status_code == 200:
            tracks = response.json()
            for track in tracks['items']:
                if track is None or track['track'] is None:
                    continue
                track_ids[index] = track['track']['id']
                #track_ids.append(ntrack)
                index += 1
            href = tracks['next']
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 404:
            if verbose:
                print('Warning {}: Problem with getting tracks from playlists, verify url {} is correct.'.format(response.status_code, href))
            return None
        elif response.status_code == 401:
            print('Access token expired, refreshing...')
            authorizer.refresh()
            headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None

    return [x for x in track_ids if x is not None] # filters out None values that can sometimes occur


def track_features(tracks, authorizer, verbose=False):
    """ Returns the features for given Spotify tracks.

    Args:
        tracks (list): List of Spotify track ID's
        authorizer (SpotifyAuth): Spotify API Authorization module.
        verbose (bool, optional): More detailed logs. Defaults to False.

    Returns:
        [zip, None]: Returns a zip object of a `track_id` and its associated `track_features`. Returns None if request failed.
    """
    spotify_endpoint = 'https://api.spotify.com/v1/audio-features'
    headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}

    remainder = len(tracks)
    offset = 0
    stride = 100
    features = []
    while remainder > 0:
        params = {'ids': ','.join(tracks[offset:offset + stride])} # spotify can only process 100 tracks at a time

        response = requests.get(spotify_endpoint, params=params, headers=headers)

        if response.status_code == 200:
            features += response.json()['audio_features']
            offset += stride
            remainder -= stride
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 401:
            print('Access token expired, refreshing...')
            authorizer.refresh()
            headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text))
            return None

    return zip(tracks, features)


def playlist_track_ids(playlist_id, authorizer, verbose=False):
    """ Gets all track id's of a given playlist.

    Args:
        playlist_id (str): Playlist id.
        authorizer ([type]): Spotify API Authorization module.
        verbose (bool, optional): More detailed logs. Defaults to False.

    Returns:
        [list, None]: Returns a list of all non-None track ID's in the playlist. Returns None if request failed.
    """
    spotify_endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    params = {'fields':'items(track(id)),next,total'} # only get id's of tracks, and total number of tracks in playlist
    headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}

    tracks = None
    index = 0
    
    # stops when no more pages left
    while spotify_endpoint:
        response = requests.get(spotify_endpoint, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            
            # allocate array for tracks
            if tracks is None:
                tracks = [''] * data['total']
            
            # add tracks to array
            for track in data['items']:
                i = track['track']['id']
                tracks[index] = i
                index += 1

            # move forward in paging
            spotify_endpoint = data['next']
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 401:
            print('Access token expired, refreshing...')
            authorizer.refresh()
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text))
            return None

    return [t for t in tracks if t is not None] # filter out null tracks