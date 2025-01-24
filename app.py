# app.py

import streamlit as st
from spotify import authenticate_spotify

# Define green shades
green_shades = [
    "rgb(98, 201, 106)",    # Color 1
    "rgb(120, 216, 130)",   # Color 2
    "rgb(142, 231, 154)",   # Color 3
    "rgb(165, 241, 178)"    # Color 4
]

# Set up Streamlit page configuration
st.set_page_config(page_title="Streamlytics", layout="wide")

# Initialize session state for Spotify
if "spotify_client" not in st.session_state:
    st.session_state.spotify_client = None

# Main App
def main():
    # Apply global styles to set the page background to black
    st.markdown(
        """
        <style>
        /* Set the entire page background to black */
        body {
            background-color: rgb(0, 0, 0);
        }
        /* Optional: Adjust the main container's padding */
        .css-18e3th9 {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Title with grey box and Color 1, including bottom margin for spacing
    st.markdown(
        f"""
        <div style="
            background-color: rgb(32, 32, 32); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 20px;">
            <h1 style="color: {green_shades[0]};">Streamlytics</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Description box with app overview using Color 2, including bottom margin for spacing
    st.markdown(
        f"""
        <div style="
            background-color: rgb(32, 32, 32); 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px;">
            <h3 style="color: {green_shades[1]};">About the App</h3>
            <p style="color: white;">
                Streamlytics provides detailed insights into your Spotify activity, including playlists, songs, and listening history.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Features box with features list and descriptions using Color 3 and Color 4
    st.markdown(
        f"""
        <div style="
            background-color: rgb(32, 32, 32); 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px;">
            <h4 style="color: {green_shades[2]};">Features</h4>
            <ul style="color: white;">
                <li>
                    <strong style="color: {green_shades[3]};">Log in to Spotify</strong>: 
                    Securely authenticate your Spotify account to access your personal data.
                </li>
                <li>
                    <strong style="color: {green_shades[3]};">Explore Your Playlists</strong>: 
                    View and analyze all your Spotify playlists, including track details and statistics.
                </li>
                <li>
                    <strong style="color: {green_shades[3]};">View Recently Played Tracks</strong>: 
                    Keep track of the latest songs you've listened to with detailed playback information.
                </li>
                <li>
                    <strong style="color: {green_shades[3]};">Download Data for Analysis</strong>: 
                    Export your Spotify data in CSV format for offline analysis and insights.
                </li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add vertical space between the description and the button
    st.markdown("<br><br>", unsafe_allow_html=True)

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
