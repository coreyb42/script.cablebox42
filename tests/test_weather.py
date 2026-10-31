"""No network: postal/geocoding/weather responses are synthetic fixtures."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

import resources.lib


class WeatherTests(unittest.TestCase):
    def setUp(self):
        k = ModuleType("resources.lib.kodiutil")
        k._ = lambda text: text
        k.PROFILE = "/fixture/profile"
        self.location = "27527"
        k.setting = lambda name, default="": self.location if name == "weather_location" else default
        k.setting_int = lambda name, default=0: 1 if name == "weather_units" else default
        k.log_err = MagicMock()
        self.k = k
        with patch.dict(sys.modules, {"resources.lib.kodiutil": k, "xbmc": MagicMock(), "xbmcgui": MagicMock()}), patch.object(resources.lib, "kodiutil", k, create=True):
            spec = importlib.util.spec_from_file_location("resources.lib.weather_under_test", Path(__file__).parents[1] / "resources/lib/weather.py")
            self.wx = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.wx)
        self.cache = {}
        self.wx._cache = lambda: self.cache
        self.wx._save_cache = MagicMock()
        self.wx._get_json = MagicMock()

    def postal(self):
        return {"post code": "27527", "country abbreviation": "US", "places": [{
            "place name": "Clayton", "state abbreviation": "NC",
            "latitude": "35.6577", "longitude": "-78.3837"}]}

    def test_zip_resolves_postal_area_with_clear_label(self):
        self.wx._get_json.return_value = self.postal()
        hit = self.wx._geocode("27527")
        self.assertEqual(hit, {"lat": 35.6577, "lon": -78.3837, "name": "Clayton, NC 27527"})
        self.wx._get_json.assert_called_once_with("https://api.zippopotam.us/us/27527")
        self.assertEqual(self.wx._geocode("27527"), hit)
        self.assertEqual(self.wx._get_json.call_count, 1)

    def test_city_state_sent_intact_and_legacy_cache_ignored(self):
        self.cache["geocode"] = {"Clayton, NC": {"lat": 31.8, "lon": -85.4, "name": "wrong fixture"}}
        self.wx._get_json.return_value = {"results": [{"name": "Clayton", "admin1": "North Carolina", "latitude": 35.65, "longitude": -78.45}]}
        hit = self.wx._geocode("Clayton, NC")
        self.assertEqual(hit["lat"], 35.65)
        url = self.wx._get_json.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(url).query)["name"], ["Clayton, NC"])

    def test_no_fallback_when_qualified_city_is_missing(self):
        self.wx._get_json.return_value = {"results": []}
        self.assertIsNone(self.wx._geocode("Clayton, NotAState"))
        self.wx._save_cache.assert_not_called()

    def test_invalid_postal_response_is_not_cached(self):
        for response in ({}, {"post code": "27527", "country abbreviation": "US", "places": []},
                         {"post code": "99999", "country abbreviation": "US"}):
            self.wx._get_json.return_value = response
            self.assertIsNone(self.wx._geocode("27527"))
        self.wx._save_cache.assert_not_called()

    def test_coordinates_skip_network_and_validate_bounds(self):
        self.assertEqual(self.wx._geocode("35.6,-78.3")["lat"], 35.6)
        self.assertIsNone(self.wx._geocode("95,-78.3"))
        self.wx._get_json.assert_not_called()

    def test_cache_does_not_show_weather_for_previous_place(self):
        self.wx.remember({"location": "Clayton, NC 27527"})
        self.assertIsNotNone(self.wx.last_good())
        self.location = "Another place"
        self.assertIsNone(self.wx.last_good())
        self.cache["last"].pop("lookup")
        self.assertIsNone(self.wx.last_good())

    def test_zip_to_forecast_and_screen_end_to_end_with_fixtures(self):
        raw = {"current": {"temperature_2m": 63, "weather_code": 0},
               "daily": {"time": [1800000000, 1800086400], "weather_code": [1, 1],
                         "temperature_2m_max": [65, 59], "temperature_2m_min": [40, 41]}}
        self.wx._get_json.side_effect = [self.postal(), raw]
        self.wx.from_kodi = lambda: None
        win = MagicMock()
        screen = self.wx.WeatherScreen(win)
        screen._fetch()
        url = self.wx._get_json.call_args.args[0]
        q = parse_qs(urlsplit(url).query)
        self.assertEqual(q["latitude"], ["35.6577"])
        self.assertEqual(q["longitude"], ["-78.3837"])
        self.assertEqual(q["temperature_unit"], ["fahrenheit"])
        self.assertEqual(screen.data["location"], "Clayton, NC 27527")
        self.assertEqual(screen.data["now"]["temp"], "63°F")
        self.assertEqual(screen.data["days"][0]["hi"], "59°")
        self.assertFalse(screen.fetching)
        self.assertEqual(self.wx.last_good(), screen.data)
        win.setProperty.assert_any_call("wx_location", "Clayton, NC 27527")
        win.setProperty.assert_any_call("wx_temp", "63°F")
        win.setProperty.assert_any_call("wx_d1_hi", "59°")


if __name__ == "__main__":
    unittest.main()
