# streamlytics/coverArt.py

import streamlit as st
import requests
import os

def save_image(url, folder, filename):
    """
    Downloads an image from a URL and saves it to the specified folder with the given filename.
    """
    try:
        # Make sure the folder exists
        os.makedirs(folder, exist_ok=True)

        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        file_path = os.path.join(folder, filename)
        with open(file_path, "wb") as img_file:
            for chunk in response.iter_content(1024):
                img_file.write(chunk)
        
        print(f"Image saved: {file_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

def search_musicbrainz(performer, song):
    """
    Searches MusicBrainz for an album MBID using performer and song.
    We'll do a simplified query: 'artist:"{performer}" AND release:"{song}"'
    (You might refine this further in production.)
    """
    base_url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "query": f'artist:"{performer}" AND release:"{song}"',
        "fmt": "json"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if "releases" in data and len(data["releases"]) > 0:
            return data["releases"][0]["id"]  # First matching release MBID
    except Exception as e:
        print(f"MusicBrainz search error for {performer} - {song}: {e}")
    return None

def fetch_cover_art(mbid):
    """
    Given a MusicBrainz release MBID, fetch the first cover art image URL from the Cover Art Archive.
    """
    cover_art_url = f"https://coverartarchive.org/release/{mbid}"
    try:
        response = requests.get(cover_art_url)
        response.raise_for_status()
        data = response.json()
        if "images" in data and len(data["images"]) > 0:
            return data["images"][0]["image"]
    except Exception as e:
        print(f"Cover Art Archive error for {mbid}: {e}")
    return None

def fetch_cover_art_for_week(df, selected_date, limit=10, save_folder="data/cover_art/"):
    """
    Fetches cover art for the top 'limit' songs from the given chart date 
    and saves/displays them one by one in Streamlit, with a progress bar.
    """
    date_mask = df["chart_date"] == selected_date
    top_songs = df[date_mask].sort_values("chart_position").head(limit)

    # Initialize progress bar at 0
    progress_bar = st.progress(0)

    # Convert top_songs to a list for easier enumeration
    top_songs_list = top_songs.to_dict(orient="records")
    total_songs = len(top_songs_list)

    for i, row in enumerate(top_songs_list, start=1):
        performer = row["performer"]
        song_title = row["song"]

        st.write(f"**Processing {song_title} by {performer}...**")
        
        mbid = search_musicbrainz(performer, song_title)
        if mbid:
            cover_url = fetch_cover_art(mbid)
            if cover_url:
                # 1) Display the cover art live in Streamlit
                st.image(cover_url, caption=f"{performer} - {song_title}")

                # 2) Save the cover art locally
                filename = f"{performer} - {song_title}.jpg".replace("/", "-")
                save_image(cover_url, save_folder, filename)
            else:
                st.write("No cover art URL found.")
        else:
            st.write("No MBID found in MusicBrainz.")

        st.write("---")  # A horizontal rule for spacing

        # Update the progress bar
        progress_percent = int((i / total_songs) * 100)
        progress_bar.progress(progress_percent)
    
    st.success("Cover art fetching completed!")
