"""Exercise the real TV playback lifecycle with fixture Kodi/Jellyfin boundaries."""
import importlib
import sys
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

SOURCE = "plugin://plugin.video.jellyfin/?mode=play&id=abc123&server=fixture"


class TVPlaybackE2E(unittest.TestCase):
    def setUp(self):
        modules = {name: ModuleType(name) for name in (
            "xbmc", "xbmcgui", "xbmcvfs", "resources.lib.kodiutil", "resources.lib.library",
            "resources.lib.scheduler", "resources.lib.weather", "resources.lib.progress")}
        modules["xbmc"].Player = type("Player", (), {})
        modules["xbmcgui"].WindowXML = type("WindowXML", (), {})
        modules["xbmcgui"].ListItem = MagicMock()
        k = modules["resources.lib.kodiutil"]
        k._ = lambda text: text
        k.setting_bool = lambda *args: False
        k.load_json = MagicMock(return_value={})
        k.save_json = MagicMock()
        k.executebuiltin = MagicMock()
        modules["xbmc"].executebuiltin = MagicMock()
        modules["xbmcgui"].Window = MagicMock()
        modules["resources.lib.library"].durations = MagicMock()
        self.mods = modules
        self.patcher = patch.dict(sys.modules, modules)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        sys.modules.pop("resources.lib.tv", None)
        self.tv = importlib.import_module("resources.lib.tv")
        self.w = self.tv.TVWindow.__new__(self.tv.TVWindow)
        self.w.player = MagicMock()
        self.w.player.isPlaying.return_value = True
        self.w.player.getPlayingFile.return_value = "https://fixture/Videos/abc123/stream?api_key=fake"
        self.w.player.getTotalTime.return_value = 2700
        self.w.progress = MagicMock()
        self.w.progress.pending = {}
        self.w.play_token = 0
        self.w.our_files = set()
        self.w.requested_path = ""
        self.w.closing = False
        self.w.ch = None
        self.w.close = MagicMock()

    def test_tune_resolve_change_and_shutdown(self):
        w = self.w
        w.play({"k": "show", "p": SOURCE, "s": 1000, "o": 60, "t": "Fixture"}, 2200)
        played = w.player.play.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(played).query)["timestamp"], ["1260.0"])
        w.progress.remember.assert_called_once_with(SOURCE)
        w.on_av_started()
        self.assertEqual(w.av_started_token, w.play_token)
        w.progress.release.assert_called_once_with(keep=SOURCE)
        self.mods["resources.lib.library"].durations().learn.assert_called_once_with(SOURCE, 2700)
        self.assertTrue(w.playing_ours())

        next_source = SOURCE.replace("abc123", "next456")
        w.play({"k": "show", "p": next_source, "s": 2200, "o": 0, "t": "Next"}, 2200)
        self.assertFalse(w.playing_ours())  # old callback cannot own the new item
        w.player.getPlayingFile.return_value = "https://fixture/Videos/next456/stream?api_key=fake"
        w.on_av_started()
        w.progress.release.assert_called_with(keep=next_source)
        w.shutdown()
        w.player.stop.assert_called_once()
        w.close.assert_called_once()
        self.assertTrue(w.closing)

    def test_regular_files_keep_existing_behavior(self):
        w = self.w
        w.play({"k": "show", "p": "/fixture/local.mkv", "s": 1000, "o": 0, "t": "Local"}, 1100)
        self.assertEqual(w.player.play.call_args.args[0], "/fixture/local.mkv")
        w.player.getPlayingFile.return_value = "/fixture/local.mkv"
        w.on_av_started()
        self.assertTrue(w.playing_ours())
        w.player.isPlaying.return_value = False
        self.assertFalse(w.playing_ours())


if __name__ == "__main__":
    unittest.main()
