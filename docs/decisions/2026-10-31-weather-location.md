# 2026-10-31: Qualified city and US ZIP weather lookup

## Purpose and affected systems

Correct weather in the Mac CableBox preview and make location selection reliable.
Operator specified ZIP27527 after noticing temperatures differed from Apple
Weather. No server configuration or authentication change.

## Pre-change state

The cached `Clayton, NC` lookup was31.87822,-85.44966:Clayton, Alabama.
The implementation removed the qualifier before calling Open-Meteo, then tried
substring matching NC against North Carolina and silently fell back to the
first result. The UI only said Clayton, hiding the mistake. Old weather could
also be reused after the location changed.

## Implementation

Send full city/state queries to Open-Meteo's supported qualifier filter.
For exactly five digits, resolve a US ZIP through public no-key Zippopotam.us,
validating country/postcode/coordinate ranges. ZIP27527 resolves to35.6577,
-78.3837, labelled Clayton, NC27527. Weather itself remains from Open-Meteo.
Use a new geocode cache namespace to invalidate old wrong matches and bind
cached forecasts to location/source/units. Update the English settings label.
Client configured explicitly to27527, Open-Meteo, Fahrenheit.

## Validation

14 offline unit/mocked-e2e tests pass, including ZIP resolution, intact city/state
queries, invalid responses, coordinate bounds, cache invalidation and actual
forecast parser/screen property rendering. Tests use only synthetic fixtures.
Afterward, separate live read-only checks verified postal area, forecast
coordinates and Eastern timezone. Mac cache/screen now show Clayton, NC27527,
current65°F and tomorrow high67°F, matching the operator's Apple Weather figures.
NWS independent forecast point identifies nearby Archer Lodge, NC. App restart
preserved the library/lineup; no video played after test-history restoration.

## Rollback and follow-up

Quit Kodi and restore only original weather module/settings/cache from the
private pre-weather-fix backup recorded in the sysadmin runbook. Reverting would
reintroduce the known location bug. Current source is on the operator-approved
development branch. New provider dependency is only the public postal lookup;
no API key. Provider outages produce no result rather than guessing another city.

## Sources

- https://open-meteo.com/en/docs/geocoding-api
- https://api.zippopotam.us/us/27527
