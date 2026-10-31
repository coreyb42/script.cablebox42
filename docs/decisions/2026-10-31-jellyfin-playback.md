# 2026-10-31: Preserve scheduled offsets through Jellyfin playback

## Purpose and affected systems

Make CableBox's existing Kodi interface usable with Jellyfin for Kodi on Mac.
Source branch `feature/jellyfin-playback`; Mac Kodi21.3 Omega ARM64 and official
Jellyfin for Kodi2.2.0+py3. No server configuration change.

## Pre-change behavior

Jellyfin replaces CableBox's ListItem while resolving plugin URLs. That loses
StartOffset, so tuning into a scheduled episode starts at zero. Kodi reports a
resolved HTTP stream instead of the plugin source; CableBox's ownership check
then fails, and exiting can leave video playing outside the CableBox window.

## Implementation

Pass the scheduled offset through Jellyfin's supported `timestamp` parameter.
Match the currently requested Jellyfin item with its resolved Videos/item/stream
route for ownership, retaining the original source for progress hooks and
duration caches. Do not store resolved authentication URLs in those caches.
Leave ordinary local/share playback unchanged. Keep changes in a small adapter
plus TV lifecycle hooks to simplify upstream merging.

## Validation

Seven offline unittest tests pass, including a mocked end-to-end TV lifecycle
covering play, resolve callback, stale-item rejection, channel change and stop.
Tests use fixtures only and make no production calls. Live smoke checks after
passing tests: guide, Clayton weather, Black Mirror and Buffy playback/channel
switching pass. Jellyfin reported position around42 minutes for the scheduled
Sci-Fi item, rather than zero (session report lags the wall clock by20 seconds).
Returning to guide leaves no Kodi session playing. Restart retains library and
lineup:853 movies,127 series,14,413 episodes;29 channels and210 prime-time pins.

## Limitation

Jellyfin records channel viewing in server watch history. CableBox's existing
Kodi progress protection does not fully protect Jellyfin user data. Do not claim
history preservation. Two live test episodes were restored with explicit
operator approval, with server readback confirming original watched/count/resume/
last-played fields. Private baselines are outside the repository. Future work
must design/test account and progress behavior before promising preservation.

## Rollback and follow-up

Quit Kodi, reinstall the original add-on code and reopen; original TV module and
activation database backups are retained outside source, per sysadmin runbook.
Do not delete client profiles or reset the server. Apple TV installation,
commercials/music assets, update channel and history protection remain future
work. The operator approved committing/pushing this development branch; this
does not authorize future automatic commits or deployment.
