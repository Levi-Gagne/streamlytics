# streamlytics/pages/6_Top_Tracks_Cover_Art.py

import streamlit as st
import json
import os
from datetime import datetime
from spotify_cover_art import (
    update_billboard_json_with_spotify_data, 
    download_spotify_cover_art
)
from image_processing import (
    list_available_fonts, 
    generate_billboard_poster, 
    custom_title_positions,
    generate_album_collage
)

# Define the cover art folder location
COVER_ART_FOLDER = "data/cover_art/"
FONTS_FOLDER = "fonts"

def fetch_user_top_data(sp, data_type='tracks', time_range='medium_term', limit=50):
    """
    Fetch the user's top tracks.
    """
    try:
        top_data = sp.current_user_top_tracks(time_range=time_range, limit=limit)
        return [
            {
                "name": track['name'],
                "artist": ', '.join(artist['name'] for artist in track['artists']),
                "album": track['album']['name'],
                "album_url": track['album']['external_urls']['spotify'],
                "album_image": track['album']['images'][0]['url'] if track['album']['images'] else None,
                "popularity": track['popularity']
            }
            for track in top_data['items']
        ]
    except Exception as e:
        st.error(f"Error fetching top tracks: {e}")
        return []

def process_top_tracks(json_data, time_range, sp):
    """
    Process the received JSON data for updating and downloading cover art.
    """
    st.session_state['selected_tracks'] = json_data
    
    save_path = os.path.join(os.path.dirname(__file__), "..", "json")
    os.makedirs(save_path, exist_ok=True)
    
    file_name = f"{time_range}_top_tracks.json"
    file_path = os.path.abspath(os.path.join(save_path, file_name))
    
    with open(file_path, "w") as f:
        json.dump(json_data, f, indent=4)
    
    st.success(f"Tracks data has been processed and saved to {file_path}!")
    
    update_billboard_json_with_spotify_data(file_path, sp)
    
    if os.path.exists(file_path):
        cover_art_folder = download_spotify_cover_art(file_path, base_folder=COVER_ART_FOLDER)
        st.success(f"All album covers downloaded to: {cover_art_folder}")
    else:
        st.error(f"Error: JSON file {file_path} not found!")

def main():
    st.set_page_config(page_title="Top Tracks", layout="wide", initial_sidebar_state="expanded")

    # **Top Tracks Title with Black Box Styling**
    st.markdown(
        """
        <div style="
            background-color: rgb(32, 32, 32); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 20px;">
            <h1 style="color: rgb(98, 201, 106);">Top Tracks</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "spotify_client" in st.session_state and st.session_state.spotify_client:
        sp = st.session_state.spotify_client

        # **Step 1: Download Spotify Top Tracks**
        st.markdown("<h2 style='color: rgb(98, 201, 106);'>1. Download Spotify Top Tracks</h2>", unsafe_allow_html=True)

        st.markdown("<label style='color: rgb(142, 231, 154);'>Select Time Range:</label>", unsafe_allow_html=True)
        time_range = st.selectbox(
            "", ["short_term", "medium_term", "long_term"],
            format_func=lambda x: x.replace("_", " ").capitalize(),
            key="time_range_selection"
        )
        
        top_tracks = fetch_user_top_data(sp, data_type='tracks', time_range=time_range, limit=50)
        
        if top_tracks:
            if st.button("Process Tracks for Download"):
                process_top_tracks(top_tracks, time_range, sp)

        else:
            st.warning("No tracks found for the selected time range.")
    
    else:
        st.warning("Please log in to Spotify from the Home Page to access this feature.")
    st.markdown("---")
    # **Step 2: Always Visible - Create Poster from Cover Art**
    st.markdown("<h2 style='color: rgb(98, 201, 106);'>2. Create Poster from Cover Art</h2>", unsafe_allow_html=True)

    # Select available folders
    folders = [folder for folder in os.listdir(COVER_ART_FOLDER) if os.path.isdir(os.path.join(COVER_ART_FOLDER, folder))]

    if not folders:
        st.warning("No album art folders found. Download images first.")
    else:
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

        # Generate Poster Button
        if st.button("Generate Ultra High-Res Poster"):
            output_poster_path = os.path.join(folder_path, f"{custom_text.replace(' ', '_')}_poster.jpg")
            
            grid_size = (8, 10)  # Example grid size, dynamically determine in actual use
            title_font_size = custom_title_positions.get(grid_size, {}).get('title_font_size', None)

            try:
                poster = generate_billboard_poster(
                    folder_path=folder_path,
                    output_path=output_poster_path,
                    font_path=font_path,
                    title=custom_text,
                    subtitle="Generated from Spotify",
                    background_color=background_color,
                    image_effect="None",
                    bevel_width=10,
                    corner_radius=30
                )
                
                st.success(f"Poster created successfully: {output_poster_path}")
                st.image(poster, caption="Generated Poster", use_container_width=True)

                if download_option == "Yes":
                    with open(output_poster_path, "rb") as file:
                        st.download_button("Download Poster", data=file, file_name=os.path.basename(output_poster_path), mime="image/jpeg")

            except Exception as e:
                st.error(f"Error creating poster: {e}")
        st.markdown("---")
        # Step 3: Generate Album Collage Only (New Section)
        st.markdown(
            """
            <h2 style='color: rgb(98, 201, 106);'>3. Download Album Collage Only</h2>
            """,
            unsafe_allow_html=True
        )

        spotify_folders = [folder for folder in os.listdir(COVER_ART_FOLDER) if os.path.isdir(os.path.join(COVER_ART_FOLDER, folder))]
        if not spotify_folders:
            st.warning("No album art folders found. Download images first.")
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
