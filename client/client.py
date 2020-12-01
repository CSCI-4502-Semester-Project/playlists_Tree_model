import requests
import json

def load_config(path='conf.json'):
    f = open(path)
    config = json.load(f)
    f.close()
    return config

def run(playlist_id, r_type):
    config = load_config()['client']
    
    headers = {"Accept":"application/json", "Content-Type":"application/json"}
    params = {'playlist':playlist_id}

    response = requests.get(f'http://{config["url"]}:{config["port"]}/{r_type}/', params=params, headers=headers)
    
    if response.status_code == 200:
        if r_type == 'push':
            return True
        elif r_type == 'recommend':
            return response.json()['ret']
    else:
        return response.json()['ret']