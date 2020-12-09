import pandas as pd
from sklearn import preprocessing

def process_features(track_features):
    """Processes the raw output of spotifyapi.api.track_features(...)

    Args:
        track_features (zip): zip object of track id and tracks features.
    
    Returns:
        [panda.DataFrame, None] Returns a formatted dataframe containing only the scaled feature data, using sklearn.preprocessing. Returns None if processing failed. 
    """
    features = [f for _, f in track_features if f is not None]
    df = pd.DataFrame(features).drop(["type", "id", "uri", "track_href", "analysis_url"], axis=1)

    return pd.DataFrame(preprocessing.scale(df), columns=df.columns)

    