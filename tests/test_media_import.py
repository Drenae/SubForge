from app.state.media_state import MediaState


def test_import_validates_deduplicates_and_removes(tmp_path):
    valid = tmp_path / "episode.MKV"
    valid.write_bytes(b"video")
    invalid = tmp_path / "notes.txt"
    invalid.write_text("notes")
    state = MediaState()
    added, errors = state.add([str(valid), str(valid), str(invalid), str(tmp_path / "missing.mkv")])
    assert added == 1
    assert len(errors) == 2
    assert list(state.files.values())[0].name == "episode.MKV"
    state.remove(str(valid.resolve()))
    assert not state.files
