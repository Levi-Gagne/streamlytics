# streamlytics/utils.py

import streamlit as st
from datetime import datetime

def format_datetime(played_at):
    """
    Formats Spotify's played_at timestamp to 'YYYY-MM-DD' and 'HH:MM'.
    """
    try:
        dt_object = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt_object.strftime("%Y-%m-%d"), dt_object.strftime("%H:%M")
    except Exception as e:
        st.error(f"Error formatting datetime: {e}")
        return "N/A", "N/A"

def fetch_recent_tracks(sp, limit=25):
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

def display_recent_tracks_sidebar(sp, limit=25):
    """
    Fetches and displays recently played tracks in the sidebar.
    """
    st.sidebar.markdown(f"<h2 style='color: rgb(120, 216, 130);'>Recently Played Tracks</h2>", unsafe_allow_html=True)
    
    recent_tracks = fetch_recent_tracks(sp, limit=limit)

    # Define shades of green for hierarchy
    green_shades = [
        "rgb(98, 201, 106)", 
        "rgb(120, 216, 130)", 
        "rgb(142, 231, 154)", 
        "rgb(165, 241, 178)"
    ]

    for idx, track in enumerate(recent_tracks, start=1):
        date, time = format_datetime(track["played_at"])
        shade = green_shades[(idx - 1) % len(green_shades)]  # Cycle through green shades
        st.sidebar.markdown(
            f"""
            <div style="background-color: {shade}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <b>#{idx}</b> 🎵 <b>{track['name']}</b> by {track['artist']}<br>
                <span style="font-size: 12px;">Played on: {date} at {time}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
