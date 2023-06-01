import spotipy

spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=
        client_secret=
        redirect_uri="http://localhost:9999"
    )
)