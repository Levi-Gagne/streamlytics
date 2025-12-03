# streamlytics/spotify.py

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_SCOPE = (
    "user-read-email user-read-private user-library-read user-library-modify "
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-read-recently-played user-top-read user-follow-read user-follow-modify"
)


def _get_auth_manager() -> SpotifyOAuth:
    cfg = st.secrets["spotify"]
    return SpotifyOAuth(
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        redirect_uri=cfg["redirect_uri"],  # MUST match one of the URIs in Spotify dashboard
        scope=SPOTIFY_SCOPE,
        cache_path=".spotify_cache",       # token cache
    )


def get_spotify_client():
    """
    Streamlit-friendly Spotify auth flow:

    - If token cached: return a ready Spotipy client.
    - If Spotify redirected back with ?code=...: exchange for token and return client.
    - Otherwise: show login link and stop execution until user comes back.
    """
    auth_manager = _get_auth_manager()

    # 1) Reuse cached token if present
    token_info = auth_manager.get_cached_token()
    if token_info and "access_token" in token_info:
        return spotipy.Spotify(auth=token_info["access_token"])

    # 2) If Spotify redirected back with `code` in query params, finish the flow
    params = st.experimental_get_query_params()
    if "code" in params:
        code = params["code"][0]
        token_info = auth_manager.get_access_token(code)
        # Clean the URL so ?code=... doesn't stick around
        st.experimental_set_query_params()
        return spotipy.Spotify(auth=token_info["access_token"])

    # 3) First-time login: show auth URL and halt app run
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[Click here to log in with Spotify]({auth_url})")
    st.info("After granting access, you'll be redirected back here automatically.")
    st.stop()