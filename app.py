import argparse
import datetime
import logging
import os
import json

import openai
import spotipy
from dotenv import load_dotenv

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Simple command line utility")
    parser.add_argument("-p", type=str, help="The prompt to describing the playlist.")
    parser.add_argument(
        "-n", type=int, default="12", help="The number of songs to be added."
    )
    parser.add_argument(
        "-envfile",
        type=str,
        default=".env",
        required=False,
        help='A dotenv file with your environment variables: "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "OPENAI_API_KEY"',
    )

    args = parser.parse_args()
    load_dotenv(args.envfile)
    if any(
        [
            x not in os.environ
            for x in ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "OPENAI_API_KEY")
        ]
    ):
        raise ValueError(
            "Error: missing environment variables. Please check your env file."
        )
    if args.n not in range(1, 50):
        raise ValueError("Error: n should be between 0 and 50")

    openai.api_key = os.environ["OPENAI_API_KEY"]

    playlist_prompt = args.p
    count = args.n
    playlist = get_playlist(playlist_prompt, count)
    add_songs_to_spotify(playlist_prompt, playlist)


def get_playlist(prompt, count=8):
    example_json = """
    [
    {"song": "Everybody Hurts", "artist": "R.E.M."},
    {"song": "Nothing Compares 2 U", "artist": "Sinead O'Connor"},
    {"song": "Hurt", "artist": "Johnny Cash"},
    {"song": "Someone Like You", "artist": "Adele"},
    {"song": "The Sound of Silence", "artist": "Simon & Garfunkel"},
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
            "content": "Generate a playlist of {count} songs based on this prompt: {prompt}",
        },
    ]

    response = openai.ChatCompletion.create(
        messages=messages, model="gpt-4", max_tokens=400
    )

    playlist = json.loads(response["choices"][0]["message"]["content"])
    return playlist


def add_songs_to_spotify(playlist_prompt, playlist):
    # Sign up as a developer and register your app at https://developer.spotify.com/dashboard/applications

    # Step 1. Create an Application.

    # Step 2. Copy your Client ID and Client Secret.
    spotipy_client_id = os.environ[
        "SPOTIFY_CLIENT_ID"
    ]  # Use your Spotify API's keypair's Client ID
    spotipy_client_secret = os.environ[
        "SPOTIFY_CLIENT_SECRET"
    ]  # Use your Spotify API's keypair's Client Secret

    # Step 3. Click `Edit Settings`, add `http://localhost:9999` as as a "Redirect URI"
    spotipy_redirect_url = "http://localhost:9999"  # Your browser will return page not found at this step. We'll grab the URL and paste back in to our console

    # Step 4. Click `Users and Access`. Add your Spotify account to the list of users (identified by your email address)

    # Spotipy Documentation
    # https://spotipy.readthedocs.io/en/2.22.1/#getting-started


sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config["SPOTIFY_CLIENT_ID"],
        client_secret=config["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="http://localhost:9999",
        scope="playlist-modify-private",
    )
)

current_user = sp.current_user()

track_ids = []
assert current_user is not None

for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}"
    search_results = sp.search(q=query, type="track", limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])

created_playlist = sp.user_playlist_create(
    current_user["id"], public=False, name=args.p
)

sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], track_ids)
