# streamlytics/spotify.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st


'''
# Spotify app configuration
SPOTIFY_CLIENT_ID     = "1dcbd7d4fafb480ab60d84c309ad5626"
SPOTIFY_CLIENT_SECRET = "49a0cae0cf834b1f84d6ac1090cec485"
SPOTIFY_REDIRECT_URI  = "http://localhost:8080"

SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)
'''

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_SCOPE = os.getenv("SPOTIFY_SCOPE")

# Spotify Authentication
def authenticate_spotify():
    """
    Authenticates the user with Spotify and returns a Spotipy client instance.
    """
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE
        )
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test connection by fetching current user's profile
        user = spotify.current_user()
        st.success(f"Logged in as {user['display_name']}")
        st.write(f"Email: {user.get('email', 'N/A')}")
        return spotify
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
