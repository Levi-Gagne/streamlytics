# streamlytics/spotify.py

from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# Spotify Config (from Streamlit Secrets)
SPOTIFY_CLIENT_ID = st.secrets["spotify"]["client_id"]
SPOTIFY_CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
SPOTIFY_REDIRECT_URI = st.secrets["spotify"]["redirect_url"]
SPOTIFY_SCOPE = st.secrets["spotify"]["scope"]

def authenticate_spotify():
    """
    Authenticates the user with Spotify and returns a Spotipy client instance.
    """
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    )
    return spotipy.Spotify(auth_manager=auth_manager)

# Main Streamlit App
if "spotify_client" not in st.session_state:
    st.session_state.spotify_client = None

if st.button("Log in to Spotify"):
    st.session_state.spotify_client = authenticate_spotify()

if st.session_state.spotify_client:
    st.success("Logged in! Now you can explore your Spotify data.")
else:
    st.warning("Please log in to Spotify.")
