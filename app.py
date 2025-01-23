# app.py

# app.py


import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

from spotify import authenticate_spotify

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
            <h4 style="color: white;">Table of Contents</h4>
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
        st.session_state.spotify_client = authenticate_spotify()

    # Check if logged in
    if st.session_state.spotify_client:
        st.success("You are logged in! Navigate to the Analytics Page for insights.")
    else:
        st.warning("Not logged in. Please log in to access Spotify data.")

if __name__ == "__main__":
    main()
