# streamlytics/pages/3_download_statistics.py

import streamlit as st
import pandas as pd
from io import BytesIO

# Utility: Convert DataFrame to CSV
def convert_df_to_csv(df):
    """
    Convert a DataFrame to CSV bytes for download.
    """
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

# Fetch Playlists
def fetch_playlists(sp):
    """
    Fetch the user's playlists.
    """
    try:
        playlists = sp.current_user_playlists(limit=50)
        data = [{"Playlist Name": p["name"], "Total Tracks": p["tracks"]["total"], "URI": p["uri"]} for p in playlists["items"]]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching playlists: {e}")
        return pd.DataFrame()

# Fetch Songs in Playlists
def fetch_songs_in_playlists(sp, playlists_df):
    """
    Fetch songs from each playlist.
    """
    try:
        all_songs = []
        for _, row in playlists_df.iterrows():
            playlist_name = row.get("Playlist Name", "Unknown")
            playlist_uri = row.get("URI")
            
            if not playlist_uri:
                continue  # Skip if no URI is found
            
            # Fetch playlist tracks
            tracks_response = sp.playlist_tracks(playlist_uri)
            tracks = tracks_response.get("items", [])
            
            for track_item in tracks:
                # Get track information safely
                track = track_item.get("track")
                if not track:
                    continue  # Skip if track is None
                
                song_name = track.get("name", "Unknown")
                album = track.get("album", {})
                album_name = album.get("name", "Unknown")
                duration_ms = track.get("duration_ms", 0)
                
                # Convert duration from milliseconds to mm:ss format
                minutes = duration_ms // 60000
                seconds = (duration_ms % 60000) // 1000
                duration_formatted = f"{minutes}:{seconds:02d}"  # Ensure two-digit seconds
                
                # Safely extract artist names
                artists = track.get("artists", [])
                artist_names = ", ".join(
                    artist.get("name", "Unknown") for artist in artists if artist and artist.get("name")
                )
                
                # Append song information
                all_songs.append({
                    "Playlist Name": playlist_name,
                    "Song Name": song_name,
                    "Artist(s)": artist_names,
                    "Album": album_name,
                    "Duration": duration_formatted
                })

        return pd.DataFrame(all_songs)
    except Exception as e:
        st.error(f"Error fetching songs from playlists: {e}")
        return pd.DataFrame()



# Fetch Recently Played Tracks
def fetch_recently_played(sp):
    """
    Fetch recently played tracks.
    """
    try:
        tracks = sp.current_user_recently_played(limit=50)["items"]
        data = [
            {
                "Song Name": track["track"]["name"],
                "Artist(s)": ", ".join(artist["name"] for artist in track["track"]["artists"]),
                "Album": track["track"]["album"]["name"],
                "Played At": track["played_at"]
            }
            for track in tracks
        ]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching recently played tracks: {e}")
        return pd.DataFrame()

# Fetch All Saved Tracks
def fetch_all_saved_tracks(sp):
    """
    Fetch all saved tracks from the user's library.
    """
    try:
        tracks = []
        limit = 50
        offset = 0

        while True:
            response = sp.current_user_saved_tracks(limit=limit, offset=offset)
            tracks.extend(response['items'])
            if len(response['items']) < limit:
                break
            offset += limit

        data = [
            {
                "Song Name": item['track']['name'],
                "Artist(s)": ", ".join(artist["name"] for artist in item['track']['artists']),
                "Album": item['track']['album']['name']
            }
            for item in tracks
        ]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching saved tracks: {e}")
        return pd.DataFrame()

# Fetch All Saved Albums
def fetch_all_saved_albums(sp):
    """
    Fetch all saved albums from the user's library.
    """
    try:
        albums = []
        limit = 50
        offset = 0

        while True:
            response = sp.current_user_saved_albums(limit=limit, offset=offset)
            albums.extend(response['items'])
            if len(response['items']) < limit:
                break
            offset += limit

        data = [
            {
                "Album Name": album['album']['name'],
                "Artist(s)": ", ".join(artist["name"] for artist in album['album']['artists'])
            }
            for album in albums
        ]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching saved albums: {e}")
        return pd.DataFrame()

# Main Download Statistics Page
def main():
    st.set_page_config(page_title="Download Statistics", layout="wide")
    
    # Green shades for hierarchy
    green_shades = [
        "rgb(98, 201, 106)",  # Color 1
        "rgb(120, 216, 130)",  # Color 2
        "rgb(142, 231, 154)"   # Color 3
    ]

    # Apply green shades to headers
    st.markdown(f"<h1 style='color: {green_shades[0]}; text-align: center;'>Download Your Spotify Statistics</h1>", unsafe_allow_html=True)

    # Check if Spotify client exists in session state
    if "spotify_client" not in st.session_state or not st.session_state.spotify_client:
        st.warning("Please log in to Spotify from the Home Page to download data.")
        return

    sp = st.session_state.spotify_client

    # Fetch data
    st.markdown(f"<h3 style='color: {green_shades[2]};'>1. Playlists</h3>", unsafe_allow_html=True)
    playlists_df = fetch_playlists(sp)
    if not playlists_df.empty:
        st.write(playlists_df)
        csv_data = convert_df_to_csv(playlists_df)
        st.download_button(label="Download Playlists CSV", data=csv_data, file_name="playlists.csv", mime="text/csv")

    st.markdown(f"<h3 style='color: {green_shades[2]};'>2. Songs in Playlists</h3>", unsafe_allow_html=True)
    if not playlists_df.empty and st.button("Fetch Songs in Playlists"):
        songs_df = fetch_songs_in_playlists(sp, playlists_df)
        if not songs_df.empty:
            st.write(songs_df)
            csv_data = convert_df_to_csv(songs_df)
            st.download_button(label="Download Songs in Playlists CSV", data=csv_data, file_name="songs_in_playlists.csv", mime="text/csv")

    st.markdown(f"<h3 style='color: {green_shades[2]};'>3. Recently Played Tracks</h3>", unsafe_allow_html=True)
    if st.button("Fetch Recently Played Tracks"):
        recent_tracks_df = fetch_recently_played(sp)
        if not recent_tracks_df.empty:
            st.write(recent_tracks_df)
            csv_data = convert_df_to_csv(recent_tracks_df)
            st.download_button(label="Download Recently Played Tracks CSV", data=csv_data, file_name="recently_played_tracks.csv", mime="text/csv")

    st.markdown(f"<h3 style='color: {green_shades[2]};'>4. Saved Tracks</h3>", unsafe_allow_html=True)
    if st.button("Fetch Saved Tracks"):
        saved_tracks_df = fetch_all_saved_tracks(sp)
        if not saved_tracks_df.empty:
            st.write(saved_tracks_df)
            csv_data = convert_df_to_csv(saved_tracks_df)
            st.download_button(label="Download Saved Tracks CSV", data=csv_data, file_name="saved_tracks.csv", mime="text/csv")

    st.markdown(f"<h3 style='color: {green_shades[2]};'>5. Saved Albums</h3>", unsafe_allow_html=True)
    if st.button("Fetch Saved Albums"):
        saved_albums_df = fetch_all_saved_albums(sp)
        if not saved_albums_df.empty:
            st.write(saved_albums_df)
            csv_data = convert_df_to_csv(saved_albums_df)
            st.download_button(label="Download Saved Albums CSV", data=csv_data, file_name="saved_albums.csv", mime="text/csv")

if __name__ == "__main__":
    main()
