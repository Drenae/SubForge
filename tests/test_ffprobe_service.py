import pytest

from app.services.ffprobe_service import FFprobeError, FFprobeService


def test_parse_tracks_keeps_stream_index_and_metadata():
    payload = '{"streams":[{"index":0,"codec_type":"video"},{"index":3,"codec_type":"subtitle","codec_name":"hdmv_pgs_subtitle","tags":{"language":"fra","title":"Signes","handler_name":"Sous-titres"},"disposition":{"forced":1,"default":0}},{"index":4,"codec_type":"subtitle","codec_name":"subrip"}]}'
    tracks = FFprobeService.parse_tracks(payload)
    assert [track.index for track in tracks] == [3, 4]
    assert tracks[0].forced and not tracks[0].default
    assert tracks[0].tags["handler_name"] == "Sous-titres"
    assert tracks[1].language is None


def test_invalid_output_reports_error():
    with pytest.raises(FFprobeError):
        FFprobeService.parse_tracks("not json")
