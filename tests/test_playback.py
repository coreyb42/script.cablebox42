import unittest
from urllib.parse import parse_qs, urlsplit

from resources.lib import playback

SOURCE = "plugin://plugin.video.jellyfin/?mode=play&id=abc123&server=fixture"


class PlaybackTests(unittest.TestCase):
    def test_offset_survives_jellyfin_resolving(self):
        result = playback.with_offset(SOURCE, 1260.25)
        self.assertEqual(parse_qs(urlsplit(result).query), {
            "mode": ["play"], "id": ["abc123"], "server": ["fixture"],
            "timestamp": ["1260.25"],
        })

    def test_replaces_old_offset_and_clamps_negative(self):
        q = parse_qs(urlsplit(playback.with_offset(SOURCE + "&timestamp=10", -3)).query)
        self.assertEqual(q["timestamp"], ["0.0"])

    def test_non_jellyfin_paths_unchanged(self):
        for path in ("/media/demo.mkv", "smb://nas/show.mkv",
                     "plugin://other/?mode=play&id=abc123",
                     "plugin://plugin.video.jellyfin/?mode=browse&id=abc123"):
            self.assertEqual(playback.with_offset(path, 50), path)
            self.assertIsNone(playback.source_for_stream(path, "https://fixture/Videos/abc123/stream"))

    def test_resolved_identity_uses_original_source(self):
        for route in ("/Videos/ABC123/stream", "/base/Videos/abc123/stream.mkv"):
            self.assertEqual(playback.source_for_stream(SOURCE, "https://fixture" + route + "?api_key=fake"), SOURCE)

    def test_rejects_unrelated_and_stale_resolutions(self):
        for path in ("https://fixture/Videos/other/stream", "https://fixture/Items/abc123/stream",
                     "https://fixture/Videos/abc123/subtitles", "file:///Videos/abc123/stream",
                     "https://fixture/Videos/abc123/streaming", "https://fixture/Videos/abc123/stream/extra"):
            self.assertIsNone(playback.source_for_stream(SOURCE, path))


if __name__ == "__main__":
    unittest.main()
