# streamlytics/pages/1_analytics_page.py


import streamlit as st
from datetime import datetime
from utils import display_recent_tracks_sidebar  # Import the utility function


# Fetch KPIs
def fetch_kpis(sp):
    """
    Fetch Spotify KPIs like total tracks, most recent artist, etc.
    """
    try:
        total_tracks = sp.current_user_saved_tracks(limit=1)['total']
        recently_played = sp.current_user_recently_played(limit=1)
        most_recent_artist = (
            recently_played['items'][0]['track']['artists'][0]['name']
            if recently_played['items']
            else "N/A"
        )
        total_playlists = sp.current_user_playlists(limit=1)['total']
        return total_tracks, most_recent_artist, total_playlists
    except Exception as e:
        st.error(f"Error fetching KPIs: {e}")
        return None, None, None

# Fetch Recently Played Tracks
def fetch_recent_tracks(sp, limit=25):  # Increased limit to 25
    """
    Fetch the user's recently played tracks.
    """
    try:
        recent_tracks = sp.current_user_recently_played(limit=limit)
        tracks = [
            {
                "name": item['track']['name'],
                "artist": ', '.join(artist['name'] for artist in item['track']['artists']),
                "played_at": item['played_at']
            }
            for item in recent_tracks['items']
        ]
        return tracks
    except Exception as e:
        st.error(f"Error fetching recently played tracks: {e}")
        return []

# Fetch Top Artists or Tracks
def fetch_user_top_data(sp, data_type='artists', time_range='medium_term', limit=50):
    """
    Fetch the user's top artists or tracks.
    """
    try:
        if data_type == 'artists':
            top_data = sp.current_user_top_artists(time_range=time_range, limit=limit)
            return [
                {
                    "name": artist['name'],
                    "popularity": artist['popularity']
                }
                for artist in top_data['items']
            ]
        elif data_type == 'tracks':
            top_data = sp.current_user_top_tracks(time_range=time_range, limit=limit)
            return [
                {
                    "name": track['name'],
                    "artist": ', '.join(artist['name'] for artist in track['artists']),
                    "album": track['album']['name'],
                    "popularity": track['popularity']
                }
                for track in top_data['items']
            ]
    except Exception as e:
        st.error(f"Error fetching top {data_type}: {e}")
        return []

# Format Date and Time
def format_datetime(played_at):
    """
    Formats Spotify's played_at timestamp to 'YYYY-MM-DD' and 'HH:MM'.
    """
    dt_object = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt_object.strftime("%Y-%m-%d"), dt_object.strftime("%H:%M")

# Dropdown Logic
def display_top_data(sp):
    """
    Display dropdowns for selecting top artists or tracks and their time range.
    """
    st.markdown(f"<label style='color: rgb(142, 231, 154);'>Choose to view:</label>", unsafe_allow_html=True)
    option = st.selectbox("", options=["Top Artists", "Top Tracks"], key="top_artists_tracks")

    st.markdown(f"<label style='color: rgb(142, 231, 154);'>Time Range:</label>", unsafe_allow_html=True)
    time_range = st.selectbox(
        "", options=["short_term", "medium_term", "long_term"], format_func=lambda x: x.replace("_", " ").capitalize(), key="time_range"
    )

    # Set limit to 50 for both Top Artists and Top Tracks
    if option == "Top Artists":
        top_artists = fetch_user_top_data(sp, data_type='artists', time_range=time_range, limit=50)
        for idx, artist in enumerate(top_artists, start=1):
            st.markdown(
                f"<b>#{idx}: <span style='color: rgb(142, 231, 154);'>{artist['name']}</span></b> (Popularity: {artist['popularity']})",
                unsafe_allow_html=True
            )
    else:
        top_tracks = fetch_user_top_data(sp, data_type='tracks', time_range=time_range, limit=50)
        for idx, track in enumerate(top_tracks, start=1):
            # Keep font and style consistent, adjust spacing for album line
            st.markdown(
                f"<b>#{idx}: <span style='color: rgb(142, 231, 154);'>{track['name']}</span></b> by {track['artist']}",
                unsafe_allow_html=True
            )
            # Use a single `st.markdown` to prevent extra blank lines
            st.markdown(
                f"&nbsp;&nbsp;&nbsp;&nbsp;- Album: {track['album']} (Popularity: {track['popularity']})",
                unsafe_allow_html=True
            )





# Main Analytics Page
def main():
    st.set_page_config(page_title="Spotify Analytics", layout="wide", initial_sidebar_state="expanded")

    # Set full-screen background color to black
    st.markdown(
        """
        <style>
        .main {
            background-color: rgb(0, 0, 0);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Green-colored title
    st.markdown("<h1 style='color: rgb(98, 201, 106); text-align: center;'>Spotify Analytics</h1>", unsafe_allow_html=True)

    # Check if Spotify client is available
    if "spotify_client" in st.session_state and st.session_state.spotify_client:
        sp = st.session_state.spotify_client

        # ----- Display Recently Played Tracks in Sidebar -----
        display_recent_tracks_sidebar(sp, limit=25)
        # ----- End of Sidebar Display -----

        # Fetch KPIs
        total_tracks, most_recent_artist, total_playlists = fetch_kpis(sp)

        # Display KPIs with gray bubble background
        st.markdown(
            f"""
            <div style='background-color: rgb(32, 32, 32); padding: 20px; border-radius: 15px;'>
                <h2 style='color: rgb(120, 216, 130); text-align: center;'>Key Performance Indicators</h2>
                <div style='display: flex; justify-content: space-around;'>
                    <div style='text-align: center;'>
                        <label style='color: rgb(142, 231, 154);'>Total Tracks in Library</label>
                        <h3 style='color: white;'>{total_tracks}</h3>
                    </div>
                    <div style='text-align: center;'>
                        <label style='color: rgb(142, 231, 154);'>Most Recent Artist</label>
                        <h3 style='color: white;'>{most_recent_artist}</h3>
                    </div>
                    <div style='text-align: center;'>
                        <label style='color: rgb(142, 231, 154);'>Total Playlists</label>
                        <h3 style='color: white;'>{total_playlists}</h3>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Display dropdown for top data
        display_top_data(sp)


    else:
        st.warning("Please log in to Spotify from the Home Page to view analytics.")

if __name__ == "__main__":
    main()
