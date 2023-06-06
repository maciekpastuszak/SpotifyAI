import spotipy
from dotenv import dotenv_values

config = dotenv_values(".env")


sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config["SPOTIFY_CLIENT_ID"],
        client_secret=["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="http://localhost:9999",
        scope="playlist-modify-private",
    )
)

current_user = sp.current_user()
assert current_user is not None
search_results = sp.search(q="Uptown Funk", type="track", limit=10)
tracks = search_results["tracks"]["items"][0]["id"]

created_playlist = sp.user_playlist_create(
    current_user["id"], public=False, name="TESTIN PLAYLIST"
)

sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], tracks)
