from pathlib import Path

from app.models.media_file import MediaFile
from app.models.subtitle_track import SubtitleTrack
from app.models.track_filter import TrackFilter
from app.state.media_state import MediaState


def test_french_forced_filters_across_episodes_and_keeps_manual_changes():
    state = MediaState()
    for episode in ("a.mkv", "b.mkv"):
        state.files[episode] = MediaFile(Path(episode), 1)
        state.set_tracks(episode, [SubtitleTrack(2, "hdmv_pgs_subtitle", "fra", forced=True),
                                   SubtitleTrack(3, "subrip", "eng", default=True),
                                   SubtitleTrack(4, "subrip", "fr", forced=False)])
    state.track_filter = TrackFilter(language="français", mode="forced")
    assert state.select_filtered() == 2
    assert state.selected_tracks == {("a.mkv", 2), ("b.mkv", 2)}
    state.select_track("a.mkv", 2, False)
    assert state.selected_tracks == {("b.mkv", 2)}
    state.track_filter = TrackFilter(codec="subrip", mode="full", default_only=True)
    assert state.select_filtered() == 2
    assert state.selected_tracks == {("a.mkv", 3), ("b.mkv", 3)}
