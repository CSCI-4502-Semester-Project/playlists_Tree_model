from flask import Flask, request
import threading
import json
import time
import os
import signal
import pickle as pk
import time

# spotify wranglers
from spotifyapi.authorization import SpotifyAuth
import spotifyapi.api as spotify_api

# data processing
from server.processing import process_features

# recommendation system
# from server.initialize import init_tree
naive_bayes_tree = None
svm_tree = None
neural_net_tree = None
random_forest_tree = None

pca_reducer = None

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from treemodel.tree import Tree

# objects for server handling
app_server = Flask(__name__)
kill_serv = threading.Event()
server_thread, kill_thread, auth, config = None, None, None, None


#
# Server request handling
#

@app_server.route('/callback/')
def auth_callback():
    global auth
    auth_code = ''
    try:
        auth_code = request.args['code']
    except:
        return 'Authentication Failure'

    auth.get_tokens(auth_code)
    auth.refresh()
    return 'Done authorizing, close tab...'

@app_server.route('/kill/')
def kill_server():
    kill_serv.set()
    return 'Server is kill.'

@app_server.route('/recommendation/')
def playlist_recommendation():
    # pretty much exact same thing as push, but with return flag set true for recommendation tree
    if request.method == 'GET':
        if isinstance(request.args.get('playlist'), str):
            # if the request is a string then assume it is a playlist id
            # in that case we either need to 
            #   1) poll spotify for the tracks / features
            #   2) or load up tracks from disk and poll spotify for features
            #   
            # it is probably easier to just poll spotify for the relevant data
            # only load from disk if it is from the 1_million playlists dataset

            playlist_id = request.args.get('playlist')

            # check if a '1mil' playlist
            if playlist_id[0:2] == 'm_':
                src = config['playlist_source']
                track_ids = None
                try:
                    f = open(f'{src}{playlist_id}.INDEX', 'r')
                    num_tracks = int(f.readline())
                    track_ids = ['']*num_tracks
                    for i, t in enumerate(f.readlines()):
                        track_ids[i] = t
                    f.close()
                except:
                    return {
                        'type': 'recommend',
                        'ret': 'Could not find non-Spotify Playlist in database.'
                    }, 404
                
                track_features = spotify_api.track_features(track_ids, auth)
                if track_features is None:
                    print(f'Track Features Error with Spotify API.')                    
                    return {
                        'type': 'recommend',
                        'ret': 'Bad Track Features.'
                    }, 400

                data = process_features(track_features)
                reduced_data = pca_reducer.transform(data)
                recommendation = None # recommendation_tree.push(reduced_data, playlist_id, ret=True)

                return {
                    'type': 'recommend',
                    'ret': recommendation
                }, 200        
            else:
                track_ids = spotify_api.playlist_track_ids(playlist_id, auth)
                if track_ids is None:
                    print(f'Track IDs Error with Spotify API. Playlist ID = {playlist_id}')
                    return {
                        'type': 'recommend',
                        'ret': 'Bad Track IDs.'
                    }, 400

                track_features = spotify_api.track_features(track_ids, auth)
                if track_features is None:
                    print(f'Track Features Error with Spotify API.')                    
                    return {
                        'type': 'recommend',
                        'ret': 'Bad Track Features.'
                    }, 400

                data = process_features(track_features)
                reduced_data = pca_reducer.transform(data)
                recommendation = None # recommendation_tree.push(reduced_data, playlist_id, ret=True)

                return {
                    'type': 'recommend',
                    'ret': recommendation
                }, 200
        else:
            # error, only accepting playlist id's, not raw tracks or track features. Not enough time to implement
            return {
                'type': 'recommend',
                'ret': 'Only Accepting Playlist ID\'s.'
            }, 400
    
@app_server.route('/push/')
def playlist_push():
    if request.method == 'GET':
        if isinstance(request.args.get('playlist'), str):
            # if the request is a string then assume it is a playlist id
            # in that case we either need to 
            #   1) poll spotify for the tracks / features
            #   2) or load up tracks from disk and poll spotify for features
            #   
            # it is probably easier to just poll spotify for the relevant data
            # only load from disk if it is from the 1_million playlists dataset

            playlist_id = request.args.get('playlist')

            # check if a '1mil' playlist
            if playlist_id[0:2] == 'm_':
                src = config['playlist_source']
                track_ids = None
                try:
                    f = open(f'{src}{playlist_id}.INDEX', 'r')
                    num_tracks = int(f.readline())
                    track_ids = ['']*num_tracks
                    for i, t in enumerate(f.readlines()):
                        track_ids[i] = t.split('\n')[0]
                    f.close()
                except:
                    return {
                        'type': 'push',
                        'ret': 'Could not find non-Spotify Playlist in database.'
                    }, 404
                
                track_features = spotify_api.track_features(track_ids, auth)
                if track_features is None:
                    print(f'Track Features Error with Spotify API.')                    
                    return {
                        'type': 'push',
                        'ret': 'Bad Track Features.'
                    }, 400

                data = process_features(track_features)
                reduced_data = pca_reducer.transform(data)

                # starttime = time.time()
                # data = naive_bayes_tree.push(reduced_data, playlist_id)
                # elapsed = time.time() - starttime
                # if data:
                #     data = (elapsed, ) + data
                #     log('NaiveBayes.csv', ', '.join(str(v) for v in data))


                # starttime = time.time()
                # data = svm_tree.push(reduced_data, playlist_id)
                # elapsed = time.time() - starttime
                # if data:
                #     data = (elapsed, ) + data
                #     log('SVM.csv', ', '.join(str(v) for v in data))

                starttime = time.time()
                data = neural_net_tree.push(reduced_data, playlist_id)
                elapsed = time.time() - starttime
                if data:
                    data = (elapsed, ) + data
                    log('NeuralNet.csv', ', '.join(str(v) for v in data))

                starttime = time.time()
                data = random_forest_tree.push(reduced_data, playlist_id)
                elapsed = time.time() - starttime
                if data:
                    data = (elapsed, ) + data
                    log('RandomForest.csv', ', '.join(str(v) for v in data))

                return {
                    'type': 'push',
                    'ret': None
                }, 200          
            else:
                track_ids = spotify_api.playlist_track_ids(playlist_id, auth)
                if track_ids is None:
                    print(f'Track IDs Error with Spotify API. Playlist ID = {playlist_id}')
                    return {
                        'type': 'push',
                        'ret': 'Bad Track IDs.'
                    }, 400

                track_features = spotify_api.track_features(track_ids, auth)
                if track_features is None:
                    print(f'Track Features Error with Spotify API.')                    
                    return {
                        'type': 'push',
                        'ret': 'Bad Track Features.'
                    }, 400

                data = process_features(track_features)
                reduced_data = pca_reducer.transform(data)
                # recommendation_tree.push(reduced_data, playlist_id, ret=False)

                return {
                    'type': 'push',
                    'ret': None
                }, 200
        else:
            # error, only accepting playlist id's, not raw tracks or track features. Not enough time to implement
            return {
                'type': 'push',
                'ret': 'Only Accepting Playlist ID\'s.'
            }, 400


#
# Helper server and authorization functions
#

def log(file, msg):
    f = open('trial_logs/' + file, 'a')
    f.write(msg + '\n')
    f.close()


def load_config(path='conf.json'):
    f = open(path)
    config = json.load(f)
    f.close()
    return config


def flask_thread(url, port):
    if url:
        app_server.run(host=url, port=port)


def killer():
    kill_serv.wait() # get the ok to kill the server
    time.sleep(0.5) # wait a little bit for it to finish responding
    os.kill(os.getpid(), signal.SIGTERM) # end the program


#
# Main function
#

def main():
    global config, auth, naive_bayes_tree, svm_tree, neural_net_tree, decision_tree_tree, random_forest_tree, adaboost_tree, kneighbors_tree, pca_reducer
    
    config = load_config()['server']

    # start a thread we will use to kill the server when done
    kill_thread = threading.Thread(target=killer)
    kill_thread.start()

    # start server for callback and recommendation requests
    server_thread = threading.Thread(target=flask_thread, args=(config['url'], config['port']))
    server_thread.start()

    # spotify authorizer
    auth = SpotifyAuth(f'http://{config["url"]}:{config["port"]}{config["callback"]}')
    auth.authorize()

    # load dimensionality reducer
    pca_reducer = pk.load(open('pca_reduce.pkl', 'rb'))

    # recommendation trees
    # naive_bayes_tree = Tree(GaussianNB, **{})
    # svm_tree = Tree(SVC, **{})
    # neural_net_tree = Tree(MLPClassifier, **{'hidden_layer_sizes':(5, 5, 5), 'learning_rate_init':0.01, 'max_iter':1000})
    # random_forest_tree = Tree(RandomForestClassifier, **{})


    #log('NaiveBayes.csv', 'ElapsedTime, Score, FitTime, AvgBranchTime, AvgConf, LeftBranches, RightBranches')
    #log('SVM.csv', 'ElapsedTime, Score, FitTime, AvgBranchTime, AvgConf, LeftBranches, RightBranches')
    #log('NeuralNet.csv', 'ElapsedTime, Score, FitTime, AvgBranchTime, AvgConf, LeftBranches, RightBranches')
    #log('RandomForest.csv', 'ElapsedTime, Score, FitTime, AvgBranchTime, AvgConf, LeftBranches, RightBranches')


main() # get it done!