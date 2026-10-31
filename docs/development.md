# Developing our fork

Read [the integration plan](plans/jellyfin-development.md) first.
Run Git commands from this independent project directory.

Verified 2026-10-31: `origin` points to coreyb42/script.cablebox42 and `upstream`
to SeadogMcGrog/script.cablebox42. For changes, create focused feature branches.
Fetch upstream, inspect its log/diff, then integrate on a separate branch and
validate before merging. Never reset custom work to upstream or force-push shared
branches. No automatic commit, release or deployment workflow is configured.

Code map:

- `resources/lib/library.py`: Kodi library/VFS and media metadata.
- `resources/lib/scheduler.py`: rolling schedules.
- `resources/lib/channels.py`, `assign.py`: channel definitions/assignment.
- `resources/lib/tv.py`: Kodi interface, playback and channel controls.
- `resources/lib/progress.py`: watched/resume protection.
- `resources/lib/kodiutil.py`: settings, JSON-RPC and persistent profile.
- `resources/settings.xml`, `resources/skins/`: settings and interface layouts.

Run `python3 -m unittest discover -s tests -v` for the fixture unit tests and
mocked end-to-end TV lifecycle tests. Before changing integration code, add
meaningful regression coverage and pass both layers before human testing.
Compilation/mocks cannot establish real playback compatibility. Preserve
upstream attribution and MPL-2.0 license. Keep credentials, profiles, exports,
media and logs outside Git. Agree any new CLI requirements before implementation.

The first working Mac proof uses Kodi21.3 and Jellyfin for Kodi2.2.0+py3 in
Add-on mode. The playback adapter preserves scheduled offsets and recognizes
resolved streams. See [the decision record](decisions/2026-10-31-jellyfin-playback.md).
Jellyfin currently records channel viewing in watch history; progress protection
across both applications remains future work.

Weather now supports city/state, US five-digit ZIP or coordinates; full qualified
queries go to Open-Meteo, and US ZIP coordinates come from no-key Zippopotam.us.
Old ambiguous geocode entries are invalidated. See
[the weather decision](decisions/2026-10-31-weather-location.md).

To package runtime files, zip `addon.xml`, `default.py`, `service.py`,
`LICENSE.txt`, `README.md` and `resources/` under a single `script.cablebox42/`
directory, excluding bytecode/cache files. Keep profiles and credentials outside
that directory. Install into Kodi's add-ons directory only while Kodi is closed,
retain the previous code, reopen and validate actual playback. Do not copy a
user profile into Git or an installation ZIP.
