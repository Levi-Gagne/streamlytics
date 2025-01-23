# app.py

#import openai
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
    st.title("Welcome to Streamlytics!")
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
