# streamlytics/spotify.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# Spotify app configuration (hardcoded for now)
SPOTIFY_CLIENT_ID = "1dcbd7d4fafb480ab60d84c309ad5626"
SPOTIFY_CLIENT_SECRET = "49a0cae0cf834b1f84d6ac1090cec485"
SPOTIFY_REDIRECT_URI = "http://localhost:8080"  # For local testing
# Update to "https://streamlytics.streamlit.app" when deployed

SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)

def authenticate_spotify():
    """
    Authenticates the user with Spotify and returns a Spotipy client instance.
    Handles token caching and session management for Streamlit Cloud.
    """
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE,
            cache_path=".streamlit/spotify_oauth_cache"  # Cache tokens locally
        )
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        return spotify
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None
