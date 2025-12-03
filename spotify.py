# streamlytics/spotify.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

config = st.secrets["spotify"]

SPOTIFY_CLIENT_ID = config["client_id"]
SPOTIFY_CLIENT_SECRET = config["client_secret"]
SPOTIFY_REDIRECT_URI = config.get("redirect_uri", "https://streamlytics.streamlit.app")

SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)

def authenticate_spotify():
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE,
        )
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        user = spotify.current_user()
        st.success(f"Connection successful! Logged in as {user['display_name']}")
        st.write(f"Email: {user.get('email', 'N/A')}")
        st.write(f"Country: {user['country']}")
        st.write(f"Subscription: {user['product']}")
        return spotify
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return None
    except Exception as e:
        st.error(f"Failed to connect: {e}")
        return None