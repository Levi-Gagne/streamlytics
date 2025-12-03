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
        redirect_uri=cfg["redirect_uri"],  # must match Spotify dashboard
        scope=SPOTIFY_SCOPE,
        cache_path=None,                   # per-session, no shared file cache
    )


def _build_client_from_token(token_info: dict) -> spotipy.Spotify:
    return spotipy.Spotify(auth=token_info["access_token"])


def get_spotify_client():
    """
    Per-session Spotify auth:

    - If token in session_state: reuse (refresh if expired).
    - If coming back from Spotify with ?code=...: exchange for token.
    - Otherwise: show login link and stop.
    """
    auth_manager = _get_auth_manager()

    # 1) If this session already has a token, reuse/refresh it
    token_info = st.session_state.get("spotify_token_info")
    if token_info:
        # Refresh if expired
        if auth_manager.is_token_expired(token_info):
            try:
                token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
                st.session_state.spotify_token_info = token_info
            except Exception:
                # refresh failed (revoked, etc.) -> force re-login
                st.session_state.pop("spotify_token_info", None)
                token_info = None

        if token_info:
            return _build_client_from_token(token_info)

    # 2) If Spotify redirected back with ?code=..., finish the flow
    params = st.experimental_get_query_params()
    if "code" in params:
        code = params["code"][0]
        token_info = auth_manager.get_access_token(code)
        st.session_state.spotify_token_info = token_info
        # clean URL
        st.experimental_set_query_params()
        return _build_client_from_token(token_info)

    # 3) First-time login for this session: show auth URL and stop
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[Click here to log in with Spotify]({auth_url})")
    st.info("After granting access, you'll be redirected back here automatically.")
    st.stop()


def is_spotify_logged_in() -> bool:
    """Helper for UI: check if this session has a token."""
    return "spotify_token_info" in st.session_state