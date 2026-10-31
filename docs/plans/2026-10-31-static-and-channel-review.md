# Quieter static and channel options

## Purpose and scope

Operator requested quieter channel-change static and recommendations based on
the actual synced TV library/metadata. Do not change the lineup until channels
are selected. Inspect the existing Kodi database read-only; keep personal title
inventories and profile/credential data outside Git.

## Phases

1. Inspect static WAV format and playback call; retain original privately.
2. Attenuate only the sound asset by6dB (gain10^(-6/20)); install the validated
   asset into the existing Mac add-on. Existing playSFX uses useCached=False,
   so no Kodi restart should be necessary.
3. Validate identical PCM format/sample count/duration, measured RMS change
   -6dB, peak decrease and no clipping. This is an asset edit, not new automation.
4. Review all synced TV titles, episode counts, years, genres, networks/studios,
   tags, ratings and runtimes. Describe built-in source options and assignment
   effects, with concrete library-backed candidate channels. Counts are metadata
   entries, not proof of complete seasons or correct content classification.
5. Document results/rollback and remaining channel-selection work. Commit/push
   remains task-scoped and requires operator instruction for this change.

## Validation and open questions

No new infrastructure CLI, secret use or production API call is needed. Automated
tests remain fixture-only. Audio verification measures the actual output asset;
use guide/weather transitions for live smoke checks to avoid new video history.
Exact final static preference and channel selections remain operator preferences.
Proposed starting attenuation is6dB; operator can refine after listening.
