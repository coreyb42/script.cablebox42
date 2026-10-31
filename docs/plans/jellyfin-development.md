# Jellyfin integration and development plan

Verified 2026-10-31. Fork: https://github.com/coreyb42/script.cablebox42.
Upstream: https://github.com/SeadogMcGrog/script.cablebox42.
Baseline: d55595444a40c1a148cc0491cb7046ed3d0037e4, version 1.0.0, MPL-2.0.

## Purpose and current state

Use the home Jellyfin library with CableBox and maintain our own changes.
Operator targets Mac and Apple TV and has no preferred player app. Mac proof
is now working with Kodi21.3 and Jellyfin for Kodi2.2.0+py3:853 movies,127 shows,
14,413 episodes;29 channels and Clayton weather. Small playback adapter added;
seven offline unit/mocked-e2e tests pass, plus live guide/weather/video/channel
switch/stop checks. Server watch-history preservation remains unresolved.

## Phases

1. Fork under coreyb42; configure fork origin and original upstream. Complete.
2. Prove Kodi + Jellyfin for Kodi + CableBox on an isolated Mac Kodi profile.
   Jellyfin for Kodi syncs metadata into the database CableBox queries; JellyCon
   alone does not. Compatibility remains **TBD**, especially plugin playback
   URLs, duration metadata, mid-program seeking and watched/resume protection.
3. Before changing code, establish fixture-based unit and end-to-end tests for
   affected source/scheduler/player behavior. Implement incrementally and run
   both suites before human validation. Tests must mock Kodi/Jellyfin boundaries
   and use no live credentials or production API calls.
4. Validate isolated-client lineup building, channel switching, seeking, guide,
   weather, commercials, restart persistence and Jellyfin progress behavior.
5. Package a repeatable add-on ZIP/update workflow with rollback; decide fork
   add-on ID before any side-by-side install. Keep custom changes focused so
   upstream merges remain manageable.
6. Choose Apple TV path after Mac proof. Official Kodi instructions require
   sideloading; free developer signing requires reinstallation every seven days.
   A server-rendered version usable through conventional clients is a larger
   alternative requiring streaming and recreation of Kodi-dependent screens.

## Open questions

- Mac-first installation authorized 2026-10-31. Kodi21.3 and CableBox1.0.0
  installed in a fresh Mac profile; Jellyfin2.2.0+py3 Quick Connect completed.
- Apple TV model/tvOS and willingness to maintain sideloading: **TBD**.
- Independent lineups versus synchronized multi-screen schedules: **TBD**.
- Priority custom features and initial channels/commercial sources: **TBD**.
- Client account/interactive authentication and credential handling: **TBD**.
- Operator approved committing/pushing this development branch; future automatic
  commit policy and new tooling language/output/secret policy remain **TBD**.

## Validation and rollback

### First compatibility change

Live Mac proof found Jellyfin add-on playback replaces CableBox's ListItem,
discarding StartOffset. Its resolved HTTP stream also fails exact plugin-path
ownership checks, so exit can leave playback running. Implement a narrow adapter
in the existing Python code: pass the scheduled offset in Jellyfin's supported
timestamp parameter; associate resolved `/Videos/<same item>/stream` playback
with its original source for ownership, duration caching and progress restoration.
Preserve non-Jellyfin playback. Add unittest unit coverage and a mocked end-to-end
play/start callback/channel-change/stop flow; no production requests in tests.
Run both before deploying changed files and repeating live validation. No new
CLI, credentials or automatic commits/pushes are introduced.

GitHub fork parent and remote URLs verified. See the dated project decision for
offline/live validation. Mac apps/profile/add-ons changed; no server config,
Tunarr, network or storage change. Credentials are client-local and owner-only.
Original TV module and add-on activation DB backups retained outside source.
Quit Kodi before reverting code; preserve profiles and do not remove source/fork
without a request. Two test episodes were restored with explicit approval and
server readback verification. Future watching will update Jellyfin watch history.

## References

### Weather correction

Operator reported wrong temperatures and specified ZIP27527. Live cache showed
Clayton, Alabama (31.87822,-85.44966). Existing code drops the qualifier from
the API search and silently falls back when NC fails substring matching against
North Carolina. Pass the full city/state query to Open-Meteo, add US5-digit ZIP
lookup via public no-key Zippopotam.us postal data, version geocode cache and
scope stale forecast reuse to the current location/units/source. Validate fixture
unit and mocked full weather fetch/render tests before deploying and confirm
27527 coordinates/current/tomorrow forecast through separate live smoke checks.
No production calls in automated tests. Weather remains from Open-Meteo.

- https://jellyfin.org/docs/general/clients/kodi/
- https://kodi.wiki/view/HOW-TO:Install_Kodi_on_Apple_TV_4_and_5_(HD_and_4K)
