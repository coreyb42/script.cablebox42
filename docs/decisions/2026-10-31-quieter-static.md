# 2026-10-31: Quieter channel-change static

## Purpose and affected systems

Operator requested slightly quieter channel-change static in the Mac preview.
Affected asset: `resources/media/static.wav` in this fork and its installed Mac
Kodi add-on copy. No player volume, lineup or server setting changed.

## Pre-change state

Static is a0.55-second mono16-bit PCM WAV at22,050Hz,12,127 samples. TV tuning
uses `xbmc.playSFX(..., False)`, requesting uncached playback. There is only an
on/off sound setting, so reducing the asset is a small compatible change.

## Implementation

Attenuated PCM samples by10^(-6/20), approximately0.5012 gain. Retained original
asset privately outside the repository and installed the validated source asset
in the existing Mac add-on. No Kodi restart required for the next uncached SFX.

## Validation

Measured RMS reduction is6.0000dB. Sample count, rate, channel count, bit depth,
duration and PCM compression type are identical. Peak amplitude decreased;
installed/source hashes match. This is an asset-only edit; no new code, network
call, credential or automated infrastructure tool was added. Existing unit/e2e
code tests are unchanged; direct waveform checks validate this change.

## Rollback and follow-up

Restore the retained original asset to source and the installed add-on if the
operator requests the previous level; do not attenuate the quieter asset again
when deploying it. Private rollback path is in the sysadmin runbook. Subjective
gain can be refined after listening. Channel planning was read-only; personal
library inventories stay outside the public fork and no lineup was changed.
