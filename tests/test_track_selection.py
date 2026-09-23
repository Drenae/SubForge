from pathlib import Path

from app.models.media_file import MediaFile
from app.models.subtitle_track import SubtitleTrack
from app.state.media_state import MediaState


def test_selection_survives_analysis_and_cleans_removed_tracks():
    state = MediaState()
    first = MediaFile(Path("episode1.mkv"), 10)
    second = MediaFile(Path("episode2.mkv"), 10)
    state.files = {str(m.path).casefold(): m for m in (first, second)}
    state.set_tracks(str(first.path), [SubtitleTrack(2, "subrip"), SubtitleTrack(3, "ass")])
    state.set_tracks(str(second.path), [SubtitleTrack(4, "hdmv_pgs_subtitle", forced=True)])
    state.select_all(True)
    assert len(state.selected_tracks) == 3
    state.set_tracks(str(first.path), [SubtitleTrack(3, "ass")])
    assert state.selected_tracks == {("episode1.mkv", 3), ("episode2.mkv", 4)}
    state.remove(str(second.path))
    assert state.selected_tracks == {("episode1.mkv", 3)}
    state.select_all(False)
    assert not state.selected_tracks
