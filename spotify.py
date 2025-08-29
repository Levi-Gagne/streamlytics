# streamlytics/spotify.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# Spotify app configuration
SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
SPOTIFY_REDIRECT_URI = "https://streamlytics.streamlit.app"  # Using the redirect URL that works
SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)

def authenticate_spotify():
    """
    Authenticates the user with Spotify and returns a Spotipy client instance.
    """
    try:
        # Initialize the SpotifyOAuth object
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE
        )

        # Create the Spotify client with the authentication manager
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        # Test the connection by fetching the current user's profile
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
