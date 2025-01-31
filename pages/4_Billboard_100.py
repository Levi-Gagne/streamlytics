# streamlytics/pages/4_Billboard_100.py

import os
import json
import random
import shutil
import uuid
import pandas as pd
import streamlit as st

from coverArt import fetch_cover_art_for_week
from spotify_cover_art import (
    update_billboard_json_with_spotify_data,
    download_cover_art_from_billboard_json
)
from image_processing import (
    create_poster_with_title_subtitle,
    list_available_fonts,
    generate_billboard_poster
)

main_title_color = "rgb(68, 156, 255)"
header_colors = [
    "rgb(68, 156, 255)",
    "rgb(102, 178, 255)",
    "rgb(135, 199, 255)",
    "rgb(169, 219, 255)",
    "rgb(96, 146, 222)",
    "rgb(82, 187, 233)",
]
sidebar_colors = [
    "rgb(206, 83, 200)",
    "rgb(182, 93, 205)",
    "rgb(148, 111, 202)",
    "rgb(119, 125, 213)",
    "rgb(96, 146, 222)",
    "rgb(82, 187, 233)",
]

def get_file_path(relative_path):
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def count_appearances_by_performer(parquet_path):
    df = pd.read_parquet(parquet_path, engine="pyarrow")
    performer_counts = df.groupby("performer").size().reset_index(name="times_in_top_100")
    performer_counts.sort_values("times_in_top_100", ascending=False, inplace=True)
    return performer_counts

def count_unique_songs_by_performer(parquet_path):
    df = pd.read_parquet(parquet_path, engine="pyarrow")
    performer_counts = (
        df.groupby("performer")["song"]
          .nunique()
          .reset_index(name="unique_song_count")
    )
    performer_counts.sort_values("unique_song_count", ascending=False, inplace=True)
    return performer_counts

def display_top_performers_by_appearances(df, top_n=25):
    st.sidebar.markdown(
        f"<h2 style='color:{header_colors[1]};'>Top Performers by Appearances</h2>",
        unsafe_allow_html=True
    )
    for idx, row in df.head(top_n).iterrows():
        shade = sidebar_colors[idx % len(sidebar_colors)]
        st.sidebar.markdown(
            f"""
            <div style="background-color:{shade}; padding:10px; border-radius:5px; margin-bottom:10px;">
                <b>{row['performer']}</b><br>
                <span style="font-size:16px; font-weight:bold;">
                    🕒 Total Appearances: {row['times_in_top_100']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_top_performers_by_unique_songs(df, top_n=25):
    st.sidebar.markdown(
        f"<h2 style='color:{header_colors[1]};'>Leaders by Unique Songs</h2>",
        unsafe_allow_html=True
    )
    for idx, row in df.head(top_n).iterrows():
        shade = sidebar_colors[idx % len(sidebar_colors)]
        st.sidebar.markdown(
            f"""
            <div style="background-color:{shade}; padding:10px; border-radius:5px; margin-bottom:10px;">
                <b>{row['performer']}</b><br>
                <span style="font-size:16px; font-weight:bold;">
                    🎵 Unique Songs: {row['unique_song_count']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_top_100_by_date(parquet_path):
    st.markdown(
        f"""
        <div style="text-align:center; background-color:rgb(32,32,32); padding:20px; border-radius:10px;">
            <h1 style="color:{main_title_color};">Billboard 100</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = pd.read_parquet(parquet_path, engine="pyarrow")
    unique_dates = sorted(df["chart_date"].unique(), reverse=True)

    st.markdown(
        f"<h3 style='color:{header_colors[1]};'>Filter Billboard Top 100 by week</h3>",
        unsafe_allow_html=True
    )
    selected_date = st.selectbox(
        "Select a Chart Date:",
        unique_dates,
        help="Choose a chart date to see the Top 100 songs for that week."
    )

    filtered_df = df[df["chart_date"] == selected_date].sort_values("chart_position")
    st.markdown(
        f"<h4 style='color:{header_colors[2]};'>Week of {selected_date}</h4>",
        unsafe_allow_html=True
    )
    st.dataframe(
        filtered_df[["chart_position", "song", "performer"]].reset_index(drop=True),
        use_container_width=True
    )
    return df, selected_date

def random_subset_of_images(original_folder, subset_option, num_images=None):
    """
    Returns a random subset of images based on the subset_option.
    subset_option can be: "All", "Large", "Medium", "Small".
    num_images is determined based on subset_option.
    """
    valid_extensions = (".jpg", ".jpeg", ".png")
    all_files = [
        f for f in os.listdir(original_folder)
        if f.lower().endswith(valid_extensions)
    ]
    total = len(all_files)
    if total == 0:
        return []

    if subset_option == "All":
        subset_size = total
    elif subset_option == "Large":
        subset_size = 77
    elif subset_option == "Medium":
        subset_size = 50
    elif subset_option == "Small":
        subset_size = 35
    else:
        subset_size = total  # fallback

    subset_size = min(subset_size, total)

    if subset_size >= total:
        return [os.path.join(original_folder, f) for f in all_files]

    chosen = random.sample(all_files, subset_size)
    return [os.path.join(original_folder, c) for c in chosen]


def main():
    parquet_path = get_file_path("../data/hot_100.parquet")
    df, selected_date = display_top_100_by_date(parquet_path)

    # Ensure JSON folder is defined for all steps
    json_folder = get_file_path("../json")
    os.makedirs(json_folder, exist_ok=True)

    # Step 1: Fetch & Enrich
    st.markdown("---")
    st.markdown(f"<h3 style='color:{header_colors[2]};'>1. Fetch & Enrich Billboard Playlist for {selected_date}</h3>", unsafe_allow_html=True)

    if st.button("Fetch & Enrich Playlist"):
        weekly_df = df[df["chart_date"] == selected_date].sort_values("chart_position")
        billboard_data = []
        for _, row in weekly_df.iterrows():
            billboard_data.append({
                "chart_position": int(row["chart_position"]),
                "song": row["song"],
                "artist": row["performer"]
            })

        # Save JSON file in new location
        json_filename = os.path.join(json_folder, f"billboard_{selected_date}.json")
        with open(json_filename, "w") as f:
            json.dump(billboard_data, f, indent=4)

        st.success(f"Created {json_filename} with {len(billboard_data)} items.")

        if "spotify_client" not in st.session_state:
            st.error("Please authenticate with Spotify first to enrich data.")
            return
        sp = st.session_state.spotify_client

        update_billboard_json_with_spotify_data(json_path=json_filename, sp=sp)
        st.success(f"Enriched {json_filename} with Spotify data.")

    # Step 2: Download covers
    st.markdown("---")
    st.markdown(f"<h3 style='color:{header_colors[2]};'>2. Download Cover Art from JSON</h3>", unsafe_allow_html=True)

    if st.button("Download Cover Art from JSON"):
        json_file = os.path.join(json_folder, f"billboard_{selected_date}.json")
        
        if not os.path.exists(json_file):
            st.error(f"{json_file} not found. Please do step 1 first.")
        else:
            try:
                folder_path = download_cover_art_from_billboard_json(json_file)
                st.success(f"Cover art saved to: {folder_path}")
            except FileNotFoundError as e:
                st.error(str(e))

    # Step 3: Create Poster
    st.markdown("---")
    st.markdown(f"<h3 style='color:{header_colors[2]};'>3. Create Poster from Cover Art</h3>", unsafe_allow_html=True)


    cover_art_base = "data/cover_art"
    billboard_folders = [
        f for f in os.listdir(cover_art_base)
        if f.startswith("billboard_") and os.path.isdir(os.path.join(cover_art_base, f))
    ]

    if not billboard_folders:
        st.warning("No billboard_ folders in data/cover_art. Please do step 2 first.")
        return

    selected_folder = st.selectbox("Select a Folder to Make a Poster", billboard_folders)

    # Font Selection
    try:
        available_fonts = list_available_fonts("fonts")
        font_names = [os.path.basename(fp) for fp in available_fonts]
        selected_font = st.selectbox("Select a Font", font_names)
        font_path = available_fonts[font_names.index(selected_font)]
    except ValueError:
        st.warning("No fonts found in streamlytics/fonts.")
        return

    # Title & Subtitle Inputs
    main_title = st.text_input("Poster Main Title", value="Billboard 100")
    subtitle = st.text_input("Poster Subtitle", value=f"Week of {selected_date}")

    # Background Color Selection
    background_color = st.color_picker("Background Color", value="#C8B4FF")

    if st.button("Create Billboard Poster"):
        covers_folder = os.path.join(cover_art_base, selected_folder)
        output_poster_path = f"poster_{selected_folder}.jpg"

        try:
            generate_billboard_poster(
                folder_path=covers_folder,
                output_path=output_poster_path,
                font_path=font_path,
                title=main_title,
                subtitle=subtitle,
                background_color=background_color
            )

            st.success(f"Poster created successfully: {output_poster_path}")
            st.image(output_poster_path, caption="Generated Billboard Poster", use_column_width=True)

        except Exception as e:
            st.error(f"Error creating poster: {e}")

    # Old "Fetch Cover Art for Top 10"
    st.markdown("---")
    if st.button("Fetch Cover Art for Top 10"):
        fetch_cover_art_for_week(df, selected_date, limit=10, save_folder="data/cover_art/")
        st.success("Cover art fetched for the top 10 tracks!")

    # Sidebar
    appearances_df = count_appearances_by_performer(parquet_path)
    unique_songs_df = count_unique_songs_by_performer(parquet_path)
    if "toggle_view" not in st.session_state:
        st.session_state.toggle_view = True

    if st.sidebar.button("Switch View"):
        st.session_state.toggle_view = not st.session_state.toggle_view

    if st.session_state.toggle_view:
        display_top_performers_by_appearances(appearances_df)
    else:
        display_top_performers_by_unique_songs(unique_songs_df)

    st.markdown(
        """
        <div style="background-color: rgb(32,32,32); padding:15px; border-radius:10px;">
            <p style="color:white;">
                1) Fetch & Enrich → <code>billboard_YYYY-MM-DD.json</code><br>
                2) Download Covers → <code>data/cover_art/billboard_YYYY-MM-DD</code><br>
                3) Create Poster 
                    → pick the subfolder, 
                    → choose background color, 
                    → choose a font, 
                    → generate collage.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
