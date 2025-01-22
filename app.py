import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load configuration from secrets.toml
REDIRECT_URI = st.secrets["redirect_url"]
CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
SCOPE = st.secrets["scope"]

# Streamlit app title
st.title("Spotify Dashboard")
st.write("Log in to explore your Spotify data and insights.")

# Initialize SpotifyOAuth
@st.cache_resource
def get_spotify_client():
    """
    Authenticates with Spotify and returns a Spotipy client.
    """
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    return spotipy.Spotify(auth_manager=auth_manager)

# Spotify Login
if "spotify_client" not in st.session_state:
    if st.button("Log in to Spotify"):
        try:
            spotify_client = get_spotify_client()
            user_info = spotify_client.current_user()
            st.session_state["spotify_client"] = spotify_client
            st.session_state["user_info"] = user_info
            st.success(f"Logged in as {user_info['display_name']}")
        except Exception as e:
            st.error(f"Failed to authenticate: {e}")

# Show User Info and Options
if "spotify_client" in st.session_state:
    spotify_client = st.session_state["spotify_client"]
    user_info = st.session_state["user_info"]

    # Display basic user info
    st.subheader("Your Spotify Profile")
    st.write(f"**Name:** {user_info['display_name']}")
    st.write(f"**Email:** {user_info.get('email', 'N/A')}")
    st.write(f"**Country:** {user_info['country']}")
    st.write(f"**Subscription Type:** {user_info['product']}")

    # Show user's playlists
    if st.button("Show My Playlists"):
        playlists = spotify_client.current_user_playlists()
        st.subheader("Your Playlists")
        if playlists['items']:
            for playlist in playlists['items']:
                st.write(f"- {playlist['name']} ({playlist['tracks']['total']} tracks)")
        else:
            st.write("No playlists found.")

    # Add more features as needed
    if st.button("Explore My Top Tracks"):
        st.subheader("Your Top Tracks")
        top_tracks = spotify_client.current_user_top_tracks(limit=10)
        if top_tracks["items"]:
            for idx, track in enumerate(top_tracks["items"], 1):
                st.write(f"{idx}. {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")
        else:
            st.write("No top tracks found.")
