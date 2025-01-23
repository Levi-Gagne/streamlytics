# app.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

from spotify import authenticate_spotify

# Spotify app configuration (hardcoded for now)
SPOTIFY_CLIENT_ID = "1dcbd7d4fafb480ab60d84c309ad5626"
SPOTIFY_CLIENT_SECRET = "49a0cae0cf834b1f84d6ac1090cec485"
SPOTIFY_REDIRECT_URI = "http://localhost:8080"  # For local testing
SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)

# Set up Streamlit page configuration
st.set_page_config(page_title="Streamlytics", layout="wide")

# Initialize session state for Spotify
if "spotify_client" not in st.session_state:
    st.session_state.spotify_client = None

# Main App
def main():
    # Title with grey box and color
    st.markdown(
        """
        <div style="background-color: rgb(32, 32, 32); padding: 20px; border-radius: 10px; text-align: center;">
            <h1 style="color: #4CAF50;">Streamlytics</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Description box with app overview and table of contents
    st.markdown(
        """
        <div style="background-color: rgb(32, 32, 32); padding: 15px; border-radius: 10px;">
            <h3 style="color: white;">About the App</h3>
            <p style="color: white;">Streamlytics provides detailed insights into your Spotify activity, including playlists, songs, and listening history.</p>
            <h4 style="color: white;">Features</h4>
            <ul style="color: white;">
                <li>Log in to Spotify</li>
                <li>Explore your playlists</li>
                <li>View recently played tracks</li>
                <li>Download data for analysis</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("Click the button below to log in to Spotify and start exploring your analytics.")

    # Login Button
    if st.button("Log in to Spotify"):
        try:
            auth_manager = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SPOTIFY_SCOPE,
                show_dialog=True  # Ensures the login dialog always appears
            )
            auth_url = auth_manager.get_authorize_url()
            st.markdown(f"[Click here to log in to Spotify]({auth_url})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error generating Spotify login link: {e}")

    # Check if logged in
    if st.session_state.spotify_client:
        st.success("You are logged in! Navigate to the Analytics Page for insights.")
    else:
        st.warning("Not logged in. Please log in to access Spotify data.")

if __name__ == "__main__":
    main()
