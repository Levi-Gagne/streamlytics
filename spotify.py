# streamlytics/spotify.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# Spotify Configuration (from Streamlit Secrets)
SPOTIFY_CLIENT_ID = st.secrets["spotify"]["client_id"]
SPOTIFY_CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
SPOTIFY_REDIRECT_URI = st.secrets["spotify"]["redirect_url"]
SPOTIFY_SCOPE = st.secrets["spotify"]["scope"]

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
            cache_path=".streamlit/spotify_oauth_cache"  # Cache tokens in a persistent file
        )
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        return spotify
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None
