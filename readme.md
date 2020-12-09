This is kind of a mess right now but here is a basic rundown of the pipeline

1) Server \
    This is where the tree and recommendation system is. Done this way so tree can be persistant in memory when testing. Client script just sends a request to the server and the server handles pretty much everything.
2) Client sends a Playlist ID
3) Server takes Playlist ID and queries to get the tracks and track features for playlist
4) Server preprocesses data. Gets rid of non-feature data, runs sklearn.preprocessing.scale on it, and reduces dimensionality using a PCA transform derived from data in EDA notebook in spotify_eda repo
5) Server pushed the cleaned data into the tree. The tree can be configured at start time for what model it used. It should be able to work plug and play style with and sklearn classifier. This is configured in ./server/initialize.py
5) Tree is then searched using classifiers at each node. When branch is hit a new classifier is made to distinguish between new leaf nodes. Tree currently does not go back up tree and re-train classifiers at each step it passed, may want to add this in if there is time.
6) The ID of the found playlist is then returned to the client. The client can then query to get the tracks of the playlist.
