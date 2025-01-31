# streamlytics/pages/5_cover_art.py

import os
import json
import streamlit as st
from spotify import authenticate_spotify  # Spotify authentication handled elsewhere
from spotify_cover_art import save_image
from image_processing import list_available_fonts, create_ultra_high_res_poster, generate_billboard_poster, generate_album_collage


# ---------------------------------------------------------------
# Define a color dictionary for quick reference
colors = {
    "header1": "#E17C3E",  # R225 G124 B62
    "header2": "#DC4D40",  # R220 G77 B64
    "header3": "#94B0C5",  # R148 G176 B197
    "header4": "#8F9056",  # R143 G144 B86
    "header5": "#DEC4AF",  # R222 G196 B175
    "header6": "#EEADD8",  # R238 G173 B216
    "header7": "#201729",  # R32 G23 B41
}
# ---------------------------------------------------------------

# Ensure the main directory exists for saving JSON files
DATA_FOLDER = "json/"  # Save in the json directory
os.makedirs(DATA_FOLDER, exist_ok=True)  # Ensure the directory exists
COVER_ART_FOLDER = "data/cover_art/"  # Folder for saving cover art images
FONTS_FOLDER = "fonts"  # Folder for font files


def fetch_user_playlists(sp):
    """
    Fetches the user's playlists and returns a dictionary with playlist names and their IDs.
    """
    playlists = sp.current_user_playlists(limit=50)
    playlist_dict = {item['name']: item['id'] for item in playlists['items']}
    return playlist_dict


def fetch_playlist_tracks(sp, playlist_id):
    """
    Fetches detailed track metadata for a given playlist ID.
    """
    playlist_tracks = []
    results = sp.playlist_tracks(
        playlist_id,
        fields="items(track(name,artists(name),album(name,release_date,images),duration_ms,explicit,popularity,external_urls(spotify)))"
    )
    for item in results['items']:
        track = item['track']
        album_images = track['album']['images']
        # Choose the largest image if available
        largest_image_url = album_images[0]['url'] if album_images else None

        track_info = {
            "name": track['name'],
            "artists": [artist['name'] for artist in track['artists']],
            "album": {
                "name": track['album']['name'],
                "release_date": track['album']['release_date'],
                "image_url": largest_image_url,
            },
            "duration_ms": track['duration_ms'],
            "explicit": track['explicit'],
            "popularity": track['popularity'],
            "track_url": track['external_urls']['spotify']
        }
        playlist_tracks.append(track_info)
    return playlist_tracks


def save_to_json(data, filename):
    """
    Saves the given data to a JSON file.
    """
    file_path = os.path.join(DATA_FOLDER, filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    return file_path


def download_images_from_json(json_path, playlist_name):
    """
    Downloads album images based on track data in the given JSON file.
    Saves images in the folder: `data/cover_art/{playlist_name}`.
    """
    json_path = os.path.join(DATA_FOLDER, os.path.basename(json_path))  # Ensure correct JSON path

    # Ensure folder exists for the playlist
    playlist_folder = os.path.join(COVER_ART_FOLDER, playlist_name.replace(" ", "_"))
    os.makedirs(playlist_folder, exist_ok=True)

    # Read the JSON data
    with open(json_path, "r") as f:
        tracks = json.load(f)

    for track in tracks:
        album = track.get("album", {})
        image_url = album.get("image_url")
        if image_url:
            # Construct the filename
            filename = f"{track['artists'][0]} - {album['name']}.jpg".replace("/", "-")
            save_image(image_url, playlist_folder, filename)

    st.success(f"Album images saved to {playlist_folder}")



def main():
    # Ensure Spotify is authenticated
    if "spotify_client" not in st.session_state or st.session_state.spotify_client is None:
        st.error("Please log in to Spotify from the home page.")
        return

    sp = st.session_state.spotify_client

    # Ensure JSON directory exists for all steps
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Main page header
    st.markdown(
        f"<h1 style='text-align: center; color: {colors['header1']};'>Create a Poster from Album Art</h1>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # 1. Pull Playlist Information
    st.markdown(f"<h2 style='color: {colors['header2']}'>1. Pull Playlist Information</h2>", unsafe_allow_html=True)
    playlists = fetch_user_playlists(sp)

    if not playlists:
        st.warning("No playlists found. Please create some playlists in your Spotify account.")
        return

    selected_playlist = st.selectbox("Select a Playlist", list(playlists.keys()))

    if selected_playlist:
        st.markdown(f"**Selected Playlist:** {selected_playlist}", unsafe_allow_html=True)

        if st.button("Fetch Playlist Data"):
            playlist_id = playlists[selected_playlist]
            tracks = fetch_playlist_tracks(sp, playlist_id)

            if tracks:
                json_filename = f"{selected_playlist.replace(' ', '_').lower()}_tracks.json"
                json_path = save_to_json(tracks, json_filename)
                st.success(f"Playlist data saved to {json_path}")
            else:
                st.warning("No tracks found in the selected playlist.")

        st.markdown("---")

        # 2. Download Playlist Cover Art
        st.markdown(f"<h2 style='color: {colors['header2']}'>2. Download Playlist Cover Art</h2>", unsafe_allow_html=True)
        json_filename = f"{selected_playlist.replace(' ', '_').lower()}_tracks.json"
        json_path = os.path.join(DATA_FOLDER, json_filename)  # Fix: Ensure it looks in json directory

        if os.path.exists(json_path):
            if st.button("Download Images"):
                download_images_from_json(json_path, selected_playlist)

    st.markdown("---")

    # 3. Create Poster from Cover Art
    st.markdown(f"<h2 style='color: {colors['header2']}'>3. Create Poster from Cover Art</h2>", unsafe_allow_html=True)
    folders = [folder for folder in os.listdir(COVER_ART_FOLDER) if os.path.isdir(os.path.join(COVER_ART_FOLDER, folder))]

    if not folders:
        st.warning("No album art folders found. Download images first.")
        return

    selected_folder = st.selectbox("Select an Album Art Folder", folders)
    folder_path = os.path.join(COVER_ART_FOLDER, selected_folder)

    # Font Selection
    try:
        available_fonts = list_available_fonts(FONTS_FOLDER)
        font_names = [os.path.basename(font) for font in available_fonts]
        selected_font_name = st.selectbox("Select a Font", font_names)
        font_path = available_fonts[font_names.index(selected_font_name)]
    except ValueError as e:
        st.error(str(e))
        return

    # Poster Text Input
    custom_text = st.text_input("Enter Text for the Poster", value="2023")
    background_color = st.color_picker("Select Background Color", value="#FFFFFF")
    download_option = st.radio("Download the Poster?", ("No", "Yes"), index=0)

    if st.button("Generate Ultra High-Res Poster"):
        output_poster_path = os.path.join(folder_path, f"{custom_text.replace(' ', '_')}_poster.jpg")
        try:
            poster = create_ultra_high_res_poster(
                folder_path=folder_path,
                output_path=output_poster_path,
                text=custom_text,
                font_path=font_path,
                font_size=1500,
                padding=500,
                max_canvas_size=15000,
                background_color=background_color
            )
            st.success(f"Poster created successfully: {output_poster_path}")
            st.image(poster, caption="Generated Poster", use_container_width=True)

            if download_option == "Yes":
                with open(output_poster_path, "rb") as file:
                    st.download_button("Download Poster", data=file, file_name=os.path.basename(output_poster_path), mime="image/jpeg")

        except Exception as e:
            st.error(f"Error creating poster: {e}")

    st.markdown("---")

    # **Step 4: Create Spotify Poster**
    st.markdown(f"<h2 style='color: {colors['header2']}'>4. Create Spotify Poster</h2>", unsafe_allow_html=True)

    # Step 4.1: Select a Spotify Cover Art Album
    st.markdown(
        f"<p style='color: {colors['header3']}; font-weight:bold; margin:0;'>Select Spotify Cover Art Album</p>",
        unsafe_allow_html=True
    )
    spotify_folders = [
        folder for folder in os.listdir(COVER_ART_FOLDER)
        if os.path.isdir(os.path.join(COVER_ART_FOLDER, folder))
    ]

    if not spotify_folders:
        st.warning("No Spotify cover art albums found. Please download cover art first.")
        return

    selected_spotify_folder = st.selectbox("", spotify_folders)
    spotify_folder_path = os.path.join(COVER_ART_FOLDER, selected_spotify_folder)

    # Step 4.2: Select a Font for Spotify Poster
    st.markdown(
        f"<p style='color: {colors['header3']}; font-weight:bold; margin:0;'>Select a Font for Spotify Poster</p>",
        unsafe_allow_html=True
    )
    try:
        selected_spotify_font_name = st.selectbox("", font_names)
        spotify_font_path = available_fonts[font_names.index(selected_spotify_font_name)]
    except ValueError as e:
        st.error(str(e))
        return

    # Step 4.3: Enter Spotify Poster Title and Subtitle
    st.markdown(
        f"<p style='color: {colors['header3']}; font-weight:bold; margin:0;'>Enter Title and Subtitle for Spotify Poster</p>",
        unsafe_allow_html=True
    )
    spotify_main_title = st.text_input("", value="Spotify Playlist Poster")
    spotify_subtitle = st.text_input("", value=f"Generated from {selected_playlist}")

    # Step 4.4: Select Background Color for Spotify Poster
    spotify_background_color = st.color_picker("", value="#C8B4FF")

    # Step 4.5: Download Spotify Poster Option
    spotify_download_option = st.radio("", ("No", "Yes"), index=0)

    # Step 4.6: Image Effects Selection
    st.markdown(
        f"<p style='color: {colors['header3']}; font-weight:bold; margin:0;'>Select Image Effect for Spotify Poster</p>",
        unsafe_allow_html=True
    )
    image_effect = st.radio(
        "Select an effect to apply to the album art:",
        ("None", "Beveled Edges", "Rounded Corners"),
        index=0
    )
    bevel_width = st.slider("Bevel Width", min_value=1, max_value=20, value=10) if image_effect == "Beveled Edges" else None
    corner_radius = st.slider("Corner Radius", min_value=5, max_value=100, value=30) if image_effect == "Rounded Corners" else None

    # Step 4.7: Generate Spotify Poster Button
    if st.button("Generate Spotify Poster"):
        spotify_output_poster_path = f"poster_{selected_spotify_folder}.jpg"

        try:
            generate_billboard_poster(
                folder_path=spotify_folder_path,
                output_path=spotify_output_poster_path,
                font_path=spotify_font_path,
                title=spotify_main_title,
                subtitle=spotify_subtitle,
                background_color=spotify_background_color,
                image_effect=image_effect,
                bevel_width=bevel_width if bevel_width else 10,
                corner_radius=corner_radius if corner_radius else 30
            )

            st.success(f"Spotify Poster created successfully: {spotify_output_poster_path}")
            st.image(spotify_output_poster_path, caption="Generated Spotify Poster", use_column_width=True)

            if spotify_download_option == "Yes":
                with open(spotify_output_poster_path, "rb") as file:
                    st.download_button(
                        label="Download Spotify Poster",
                        data=file,
                        file_name=os.path.basename(spotify_output_poster_path),
                        mime="image/jpeg"
                    )

        except Exception as e:
            st.error(f"Error creating Spotify poster: {e}")

    st.markdown("---")
    
    # Step 5: Download Album Collage Only (New Section)
    st.markdown(f"<h2 style='color: {colors['header2']}'>5. Download Album Collage Only</h2>", unsafe_allow_html=True)

    spotify_folders = [folder for folder in os.listdir(COVER_ART_FOLDER) if os.path.isdir(os.path.join(COVER_ART_FOLDER, folder))]
    if not spotify_folders:
        st.warning("No album art folders found. Please download cover art first.")
        return

    selected_collage_folder = st.selectbox("Select Album Art Folder", spotify_folders, key="collage")
    collage_folder_path = os.path.join(COVER_ART_FOLDER, selected_collage_folder)

    if st.button("Generate Album Collage"):
        collage_output_path = os.path.join(collage_folder_path, f"{selected_collage_folder}_collage.jpg")
        try:
            generate_album_collage(collage_folder_path, collage_output_path)
            st.success(f"Album Collage created successfully: {collage_output_path}")
            st.image(collage_output_path, caption="Generated Album Collage", use_column_width=True)
            with open(collage_output_path, "rb") as file:
                st.download_button("Download Collage", data=file, file_name=os.path.basename(collage_output_path), mime="image/jpeg")
        except Exception as e:
            st.error(f"Error creating album collage: {e}")

if __name__ == "__main__":
    main()