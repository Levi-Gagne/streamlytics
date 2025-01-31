# streamlytics/spotify_cover_art.py

import os
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def save_image(url, folder, filename):
    """
    Downloads an image from a URL and saves it to the specified folder with the given filename.
    """
    try:
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


def download_spotify_album_images(sp, limit=50, folder="data/cover_art/"):
    """
    Legacy function: Fetches recently played tracks from Spotify,
    extracts the album image URL, and saves them to 'folder'.
    """
    recent_tracks = sp.current_user_recently_played(limit=limit)
    for item in recent_tracks['items']:
        track = item['track']
        played_at = item['played_at']
        artist_names = ', '.join(artist['name'] for artist in track['artists'])
        album_name = track['album']['name']
        album_images = track['album']['images']
        
        if album_images:
            image_url = album_images[0]['url']  # largest
            filename = f"{artist_names} - {album_name}.jpg".replace("/", "-")
            print(f"Downloading album cover for '{track['name']}' by {artist_names} (Played at: {played_at})")
            save_image(image_url, folder, filename)
            print("—"*40)
        else:
            print(f"No album images found for '{track['name']}' by {artist_names}")


def find_your_top_songs_playlists(sp):
    """
    Searches the user's playlists for any named 'Your Top Songs {Year}'.
    Returns a list of dicts with 'id' and 'name' for matching playlists.
    """
    matching_playlists = []
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        name = playlist['name']
        playlist_id = playlist['id']
        if name.startswith("Your Top Songs "):
            matching_playlists.append({'id': playlist_id, 'name': name})
    return matching_playlists


def fetch_playlist_tracks(sp, playlist_id):
    """
    Legacy function: Given a playlist ID, fetches tracks and returns metadata.
    """
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    items = results['items']
    tracks_info = []
    for item in items:
        track = item['track']
        if not track:
            continue
        track_name = track['name']
        artist_names = ', '.join(artist['name'] for artist in track['artists'])
        album_name = track['album']['name'] if track['album'] else "Unknown Album"
        album_images = track['album']['images'] if track['album'] else []
        tracks_info.append({
            'track_name': track_name,
            'artist_names': artist_names,
            'album_name': album_name,
            'album_images': album_images
        })
    return tracks_info


# -----------------------------------------------------------
# NEW HELPER: pick_best_spotify_match
# -----------------------------------------------------------
def pick_best_spotify_match(results, billboard_year):
    """
    From a list of Spotify search results (track items),
    pick the track whose album release_date is closest to the 'billboard_year'.
    If we can't parse a year or get no good match, fallback to the first.
    """
    # If no results, return None
    if not results:
        return None
    
    # If billboard_year is something like 1998, we'll try to pick an album near that
    best_item = None
    best_diff = 999999  # some large number
    for item in results:
        album_data = item.get('album', {})
        rel_date = album_data.get('release_date', '')
        # parse year if possible
        try:
            parsed_year = int(rel_date.split('-')[0])  # e.g. "2015-06-30"
        except ValueError:
            parsed_year = 999999  # can't parse, treat as outlier

        diff = abs(parsed_year - billboard_year)
        if diff < best_diff:
            best_diff = diff
            best_item = item

    # fallback is the first if best_item is still None
    return best_item or results[0]


# -----------------------------------------------------------
# Updated: fetch_billboard_cover_art_for_week
# -----------------------------------------------------------
def fetch_billboard_cover_art_for_week(
    df,
    selected_date,
    sp,
    limit=10,
    save_folder="data/cover_art/"
):
    """
    Improved version: we do track:"..." artist:"..." with limit=5,
    then pick the best match by album release year if possible.
    """
    import os
    import re

    weekly_df = df[df["chart_date"] == selected_date].sort_values("chart_position")
    weekly_df = weekly_df.head(limit)

    subfolder_name = f"billboard_{selected_date}"
    subfolder_path = os.path.join(save_folder, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Attempt to parse year from selected_date, e.g. "1998-01-24" => 1998
    try:
        billboard_year = int(str(selected_date).split('-')[0])  # "1998" => 1998
    except:
        billboard_year = 9999

    for idx, row in weekly_df.iterrows():
        song_name = row.get("song")
        performer = row.get("performer")
        chart_pos = row.get("chart_position", idx + 1)

        if not song_name or not performer:
            print(f"Skipping row {idx}: missing song or performer.")
            continue

        # Build advanced Spotify query
        # e.g. track:"Burn" artist:"Militia"
        # fallback is normal "song_name performer" if the advanced approach yields nothing
        adv_query = f'track:"{song_name}" artist:"{performer}"'
        search_results = sp.search(q=adv_query, type='track', limit=5)
        items = search_results["tracks"]["items"]

        if not items:
            # fallback
            naive_query = f"{song_name} {performer}"
            fallback_res = sp.search(q=naive_query, type='track', limit=5)
            items = fallback_res["tracks"]["items"]

        if not items:
            print(f"No Spotify match found for '{song_name}' by {performer}")
            continue

        # pick best match
        best_item = pick_best_spotify_match(items, billboard_year)
        if not best_item:
            print(f"No suitable match for '{song_name}' by {performer}")
            continue

        album_data = best_item.get("album", {})
        album_images = album_data.get("images", [])
        if not album_images:
            print(f"No album images for '{song_name}' by {performer}")
            continue

        image_url = album_images[0]["url"]
        safe_song = song_name.replace("/", "-")
        safe_perf = performer.replace("/", "-")
        filename = f"{chart_pos:02d} - {safe_perf} - {safe_song}.jpg"

        save_image(image_url, subfolder_path, filename)

    print(f"Cover art for '{selected_date}' saved to: {subfolder_path}")


# -----------------------------------------------------------
# Updated: update_billboard_json_with_spotify_data
# -----------------------------------------------------------
def update_billboard_json_with_spotify_data(json_path, sp, output_json_path=None):
    """
    Enriches the Billboard JSON file with Spotify metadata.
    """
    import json
    import re

    # Fix: Do NOT overwrite `json_path`, just check it exists
    if not os.path.exists(json_path):
        print(f"JSON file not found at {json_path}")
        return

    filename = os.path.basename(json_path)

    try:
        date_part = re.sub(r"^billboard_|\.json$", "", filename)  # Extract "YYYY-MM-DD"
        billboard_year = int(date_part.split('-')[0])  # Extract "YYYY"
    except:
        billboard_year = 9999

    with open(json_path, "r") as f:
        billboard_data = json.load(f)

    for entry in billboard_data:
        song_name = entry.get("song")
        artist_name = entry.get("artist")

        if not song_name or not artist_name:
            continue

        adv_query = f'track:"{song_name}" artist:"{artist_name}"'
        search_results = sp.search(q=adv_query, type="track", limit=5)
        items = search_results["tracks"]["items"]

        if not items:
            naive_query = f"{song_name} {artist_name}"
            fallback_res = sp.search(q=naive_query, type='track', limit=5)
            items = fallback_res["tracks"]["items"]

        if not items:
            print(f"No match for '{song_name}' by '{artist_name}'")
            continue

        best_item = pick_best_spotify_match(items, billboard_year)
        if not best_item:
            continue

        entry.update({
            "name": best_item["name"],
            "artists": [artist["name"] for artist in best_item["artists"]],
            "album": {"name": best_item.get("album", {}).get("name"),
                      "release_date": best_item.get("album", {}).get("release_date")},
            "image_url": best_item.get("album", {}).get("images", [{}])[0].get("url"),
            "duration_ms": best_item["duration_ms"],
            "explicit": best_item["explicit"],
            "popularity": best_item["popularity"],
            "track_url": best_item["external_urls"].get("spotify")
        })

    # Save the enriched JSON
    with open(json_path, "w") as out_f:
        json.dump(billboard_data, out_f, indent=4)

    print(f"Billboard JSON updated: {json_path}")




def download_cover_art_from_billboard_json(json_path, base_folder="data/cover_art/"):
    """
    Reads an enriched Billboard JSON file and downloads cover art images.
    """
    import json
    import re

    json_folder = os.path.join(os.path.dirname(__file__), "json")
    json_path = os.path.join(json_folder, os.path.basename(json_path))

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No such file: {json_path}")

    with open(json_path, "r") as f:
        billboard_data = json.load(f)

    filename = os.path.basename(json_path)
    date_part = re.sub(r"^billboard_|\.json$", "", filename)
    subfolder = os.path.join(base_folder, f"billboard_{date_part}")
    os.makedirs(subfolder, exist_ok=True)

    downloaded_count = 0
    for track in billboard_data:
        image_url = track.get("image_url")
        if not image_url:
            print(f"No image_url for track: {track}")
            continue

        chart_pos = track.get("chart_position", 0)
        track_name = track.get("name", "UnknownTrack")

        safe_track_name = re.sub(r'[\\/:*?"<>|]', '-', track_name)
        filename = f"{chart_pos:02d}_{safe_track_name}.jpg"

        save_image(image_url, subfolder, filename)
        downloaded_count += 1

    print(f"Downloaded {downloaded_count} images to {subfolder}")
    return subfolder

def download_spotify_cover_art(json_path, base_folder="data/cover_art/"):
    """
    Reads a Spotify Top Tracks JSON file and downloads album cover images.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No such file: {json_path}")

    with open(json_path, "r") as f:
        track_data = json.load(f)

    filename = os.path.basename(json_path)
    time_range = filename.replace("_top_tracks.json", "")
    subfolder = os.path.join(base_folder, f"{time_range}_top_tracks")
    os.makedirs(subfolder, exist_ok=True)

    downloaded_count = 0
    for track in track_data:
        image_url = track.get("album_image")
        if not image_url:
            print(f"No image_url for track: {track}")
            continue

        track_name = track.get("name", "UnknownTrack")
        artist_name = track.get("artist", "UnknownArtist")

        safe_track_name = track_name.replace("/", "-")
        safe_artist_name = artist_name.replace("/", "-")
        filename = f"{safe_artist_name} - {safe_track_name}.jpg"

        save_image(image_url, subfolder, filename)
        downloaded_count += 1

    print(f"Downloaded {downloaded_count} images to {subfolder}")
    return subfolder