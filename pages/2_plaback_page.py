# streamlytics/pages/2_plaback_page.py


import streamlit as st
import spotipy
from spotipy.exceptions import SpotifyException

# Fetch User Playlists Function
def fetch_user_playlists(sp):
    """
    Fetch the user's playlists and return their names and URIs.
    """
    try:
        playlists = sp.current_user_playlists(limit=50)
        return [{"name": playlist["name"], "uri": playlist["uri"]} for playlist in playlists["items"]]
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

# Play Playlist Function
def play_playlist(sp, playlist_uri):
    """
    Start playback of a playlist using its URI.
    """
    try:
        devices = sp.devices()
        device_id = None
        for device in devices["devices"]:
            if device["is_active"]:
                device_id = device['id']
                break

        if not device_id:
            st.error("No active device found. Please open Spotify on your desired device and try again.")
            return

        sp.start_playback(device_id=device_id, context_uri=playlist_uri)
        st.success(f"Now playing the selected playlist on your active device.")
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Switch Song Function
def switch_song(sp, song_name, artist_name):
    """
    Search for a song by its name and artist, retrieve its URI, and play it.
    """
    try:
        results = sp.search(q=f"track:{song_name} artist:{artist_name}", type="track", limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        if not tracks:
            st.warning(f"No song found for '{song_name}' by '{artist_name}'.")
            return

        track = tracks[0]
        track_uri = track['uri']
        track_name = track['name']
        track_artist = ', '.join(artist['name'] for artist in track['artists'])
        st.info(f"Found '{track_name}' by '{track_artist}'. Preparing to play...")

        devices = sp.devices()
        device_id = None
        for device in devices['devices']:
            if device['is_active']:
                device_id = device['id']
                break

        if not device_id:
            st.error("No active device found. Please open Spotify on your desired device and try again.")
            return

        sp.start_playback(device_id=device_id, uris=[track_uri])
        st.success(f"Now playing '{track_name}' by '{track_artist}' on your active device.")
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Fetch Saved Podcasts
def fetch_saved_podcasts(sp, limit=20):
    """
    Fetch the user's saved podcasts.
    """
    try:
        shows = sp.current_user_saved_shows(limit=limit)["items"]
        return [
            {
                "Name": show["show"]["name"],
                "Publisher": show["show"]["publisher"],
                "Total Episodes": show["show"]["total_episodes"],
                "Show ID": show["show"]["id"]
            }
            for show in shows
        ]
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

# Fetch Latest Podcast Episode
def fetch_latest_episode(sp, show_id):
    """
    Fetch the latest episode of a specific podcast show.
    """
    try:
        episodes = sp.show_episodes(show_id, limit=1, offset=0)["items"]
        if episodes:
            episode = episodes[0]
            return {
                "Name": episode["name"],
                "Release Date": episode["release_date"],
                "Spotify URL": episode["external_urls"]["spotify"],
                "URI": episode["uri"]
            }
        else:
            st.warning("No episodes found for the selected podcast.")
            return None
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return None

# Play Podcast Episode
def play_episode(sp, episode_uri):
    """
    Play a specific podcast episode by its URI.
    """
    try:
        devices = sp.devices()
        device_id = None
        for device in devices["devices"]:
            if device['is_active']:
                device_id = device['id']
                break

        if not device_id:
            st.error("No active device found. Please open Spotify on your desired device and try again.")
            return

        sp.start_playback(device_id=device_id, uris=[episode_uri])
        st.success("Now playing the selected podcast episode on your active device.")
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Get Currently Playing Content
def get_current_playing_content(sp):
    """
    Retrieve what the user is currently playing (music, podcast, audiobook, or other).
    """
    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback['is_playing']:
            content_type = current_playback['currently_playing_type']
            item = current_playback['item']

            if content_type == "track":
                return {
                    "type": "Music",
                    "name": item["name"],
                    "artists": ", ".join(artist["name"] for artist in item["artists"]),
                    "spotify_url": item["external_urls"]["spotify"]
                }
            elif content_type == "episode":
                return {
                    "type": "Podcast",
                    "name": item["name"],
                    "show_name": item["show"]["name"],
                    "publisher": item["show"]["publisher"],
                    "spotify_url": item["external_urls"]["spotify"]
                }
            else:
                return {"type": "Other", "description": "Unknown content is playing."}
        else:
            return {"type": "None"}
    except SpotifyException as e:
        st.error(f"Spotify API error: {e}")
        return {"type": "Error"}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"type": "Error"}

# Main Playback Page
def main():
    st.set_page_config(page_title="Playback Controls", layout="wide")

    # Green shades for hierarchy
    green_shades = [
        "rgb(98, 201, 106)",  # Color 1
        "rgb(120, 216, 130)",  # Color 2
        "rgb(142, 231, 154)",  # Color 3
        "rgb(165, 241, 178)"   # Color 4
    ]

    # Apply green shades to headers
    st.markdown(f"<h1 style='color: {green_shades[0]}; text-align: center;'>Playback Control</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: {green_shades[1]}; text-align: center;'>Control Your Spotify Playback</h2>", unsafe_allow_html=True)

    # Check if Spotify client exists in session state
    if "spotify_client" not in st.session_state or not st.session_state.spotify_client:
        st.warning("Please log in to Spotify from the Home Page to control playback.")
        return

    sp = st.session_state.spotify_client

    # Show currently playing content
    current_playing = get_current_playing_content(sp)

    if current_playing["type"] == "Music":
        st.info(
            f"Currently playing music: '{current_playing['name']}' by {current_playing['artists']}. "
            f"[Listen on Spotify]({current_playing['spotify_url']})"
        )
    elif current_playing["type"] == "Podcast":
        st.info(
            f"Currently playing podcast: '{current_playing['name']}' from '{current_playing['show_name']}' "
            f"by {current_playing['publisher']}. [Listen on Spotify]({current_playing['spotify_url']})"
        )
    elif current_playing["type"] == "Other":
        st.warning("Currently playing unknown content.")
    else:
        st.warning("Nothing is currently playing.")

    # Playback Controls
    st.markdown(f"<h3 style='color: {green_shades[2]};'>Playback Controls</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous"):
            try:
                sp.previous_track()
                st.success("Skipped to the previous track.")
            except SpotifyException as e:
                st.error(f"Spotify API error: {e}")
    with col2:
        if st.button("Pause/Resume"):
            try:
                current_playback = sp.current_playback()
                if current_playback and current_playback['is_playing']:
                    sp.pause_playback()
                    st.success("Playback paused.")
                else:
                    sp.start_playback()
                    st.success("Playback resumed.")
            except SpotifyException as e:
                st.error(f"Spotify API error: {e}")
    with col3:
        if st.button("Next"):
            try:
                sp.next_track()
                st.success("Skipped to the next track.")
            except SpotifyException as e:
                st.error(f"Spotify API error: {e}")

    # Input for changing song
    st.markdown(f"<h3 style='color: {green_shades[2]};'>Change Song</h3>", unsafe_allow_html=True)
    st.markdown(f"<label style='color: {green_shades[3]};'>Song Name</label>", unsafe_allow_html=True)
    song_name = st.text_input("", key="song_name_input")
    st.markdown(f"<label style='color: {green_shades[3]};'>Artist Name</label>", unsafe_allow_html=True)
    artist_name = st.text_input("", key="artist_name_input")
    if st.button("Play Song"):
        if song_name and artist_name:
            switch_song(sp, song_name, artist_name)
        else:
            st.warning("Please enter both a song name and an artist name.")

    # Dropdown for podcasts
    st.markdown(f"<h3 style='color: {green_shades[2]};'>Saved Podcasts</h3>", unsafe_allow_html=True)
    st.markdown(f"<label style='color: {green_shades[3]};'>Select a Podcast</label>", unsafe_allow_html=True)
    saved_podcasts = fetch_saved_podcasts(sp)
    if saved_podcasts:
        podcast_names = [podcast["Name"] for podcast in saved_podcasts]
        selected_podcast = st.selectbox("", podcast_names, key="podcast_dropdown")

        if st.button("Play Latest Episode"):
            podcast = next((pod for pod in saved_podcasts if pod["Name"] == selected_podcast), None)
            if podcast:
                latest_episode = fetch_latest_episode(sp, podcast["Show ID"])
                if latest_episode:
                    st.info(
                        f"Playing the latest episode: '{latest_episode['Name']}' "
                        f"(Released: {latest_episode['Release Date']}). "
                        f"[Listen on Spotify]({latest_episode['Spotify URL']})"
                    )
                    play_episode(sp, latest_episode["URI"])
    else:
        st.warning("No saved podcasts found in your library.")

if __name__ == "__main__":
    main()
