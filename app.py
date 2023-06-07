import spotipy
from dotenv import dotenv_values
import openai
import json

config = dotenv_values(".env")

openai.api_key = config["OPENAI_API_KEY"]


def get_playlist(prompt, count=8):
    example_json = """
    [
    {"song": "Everybody Hurts", "artist": "R.E.M."},
    {"song": "Nothing Compares 2 U", "artist": "Sinead O'Connor"},
    {"song": "Hurt", "artist": "Johnny Cash"},
    {"song": "Someone Like You", "artist": "Adele"},
    {"song": "The Sound of Silence", "artist": "Simon & Garfunkel"},
    {"song": "Yesterday", "artist": "The Beatles"},
    {"song": "Tears In Heaven", "artist": "Eric Clapton"},
    {"song": "Everybody's Got to Learn Sometime", "artist": "Beck"},
    {"song": "I Will Remember You", "artist": "Sarah McLachlan"},
    {"song": "My Heart Will Go On", "artist": "Celine Dion"}
    ]
    """

    messages = [
        {
            "role": "system",
            "content": """You are a helpful playlist generating assistant.
        You should generate a list of songs and their artists according to a text prompt.
        Ypu should return a JSON array, where each element follows this format: {"song": <song_title>, "artist": <artist_name>}
        """,
        },
        {
            "role": "user",
            "content": "Generate a playlist of songs based on this prompt: super super sad songs",
        },
        {"role": "assistant", "content": example_json},
        {
            "role": "user",
            "content": "Generate a playlist of songs based on this prompt: high energy exciting dance songs",
        },
    ]

    res = openai.ChatCompletion.create(
        messages=messages, model="gpt-3.5-turbo", max_tokens=400
    )

    playlist = json.loads(["choices"][0]["message"]["content"])
    return playlist


songs = get_playlist("epic songs", 4)
print(songs)

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

# search_results = sp.search(q="Uptown Funk", type="track", limit=10)
# tracks = search_results["tracks"]["items"][0]["id"]

# created_playlist = sp.user_playlist_create(
#     current_user["id"], public=False, name="TESTIN PLAYLIST"
# )

# sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], tracks)
