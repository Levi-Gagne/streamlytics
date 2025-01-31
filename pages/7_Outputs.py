# streamlytics/pages/7_Outputs.py


import streamlit as st
from pathlib import Path

# Set up page configuration
st.set_page_config(page_title="Streamlytics Outputs", layout="wide")

# Define a function to load and display images from a directory
def display_images(section_title, image_paths, captions=None):
    """
    Display images with a title and optional captions.
    :param section_title: The title of the section.
    :param image_paths: List of image file paths to display.
    :param captions: Optional list of captions for the images.
    """
    st.markdown(
        f"<h3 style='color: rgb(98, 201, 106);'>{section_title}</h3>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    for i, img_path in enumerate(image_paths):
        with (col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3):
            caption = captions[i] if captions else None
            st.image(img_path, caption=caption, use_container_width=True)

# Title Section
st.markdown(
    """
    <div style="
        background-color: rgb(32, 32, 32); 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center;">
        <h1 style="color: rgb(98, 201, 106); font-size: 40px;">Streamlytics Outputs</h1>
        <p style="color: white; font-size: 18px;">
            Explore the stunning visuals and charts you can create with Streamlytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Spotify Most Recent Tracks Section
display_images(
    "Spotify Most Recent Tracks (Short, Medium, Long Term)",
    [
        "data/outputs/short_term_top_tracks_collage.jpg",
        "data/outputs/medium_term_top_tracks_collage.jpg",
        "data/outputs/long_term_top_tracks_collage.jpg",
    ],
    captions=[
        "Short-Term Top Tracks Collage",
        "Medium-Term Top Tracks Collage",
        "Long-Term Top Tracks Collage",
    ],
)

# Billboard Charts Section
display_images(
    "Billboard Hot 100 Charts",
    [
        "data/outputs/Billboard_100_1970-01-31.jpg",
        "data/outputs/Billboard_100_2000-01-29.jpg",
    ],
    captions=[
        "Billboard Chart for January 31, 1970",
        "Billboard Chart for January 29, 2000",
    ],
)

# Top Tracks Posters Section
display_images(
    "Top Tracks Posters",
    [
        "data/outputs/poster_Your_Top_Songs_2018.jpg",
        "data/outputs/poster_Your_Top_Songs_2019.jpg",
        "data/outputs/poster_Your_Top_Songs_2020.jpg",
    ],
    captions=[
        "Your Top Songs 2018 Poster",
        "Your Top Songs 2019 Poster",
        "Your Top Songs 2020 Poster",
    ],
)

# Year Collage Art Section
display_images(
    "Year Collage Art",
    [
        "data/outputs/2023.jpg",
        "data/outputs/2024.jpg",
    ],
    captions=[
        "2023 Collage Art",
        "2024 Collage Art",
    ],
)

# Add some vertical space
st.markdown("<br><br>", unsafe_allow_html=True)
