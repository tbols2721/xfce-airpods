# Operations and diagnostics

The tray uses the daemon's normal interface and can operate with other supported
Bluetooth adapters. The optional `scripts/airpods-tools` helper specifically
requires the onboard MediaTek adapter with USB ID `0489:e13a`, one paired AirPods
device on that adapter, BlueZ's system D-Bus interface, and PulseAudio's command
utilities. It identifies the radio by USB identity rather than a fixed `hci`
number. It is not a generic helper for other adapters or audio servers.

## Start the controls

Run these commands from the XFCE user session:

```bash
~/.local/bin/airpods-xfce start
~/.local/bin/airpods-xfce menu
~/.local/bin/airpods-xfce status
```

The status command displays model, connection, and battery information. For
MediaTek-specific audio diagnostics, use:

```bash
./scripts/airpods-tools status
```

This reports controller index, USB product identity, connection, profile, and
codec without printing Bluetooth addresses or the personalized device name.
Full daemon status is available through `~/.local/bin/librepods-ctl status`;
that output can contain a personalized name and should be reviewed before sharing.

## Pair through the intended adapter

Use Blueman for ordinary pairing. Select the intended adapter, put the AirPods
in pairing mode, pair, and trust the device. Follow the pairing procedure for
your AirPods model. For Pro 3, place both AirPods in the open case and double-tap
the front until the status light flashes white. Keep the lid open during pairing.

With the supported onboard MediaTek adapter, the terminal helper can open a
BlueZ shell:

```bash
./scripts/airpods-tools pair-shell
```

It prints a controller-selection command and opens `bluetoothctl` with a
`NoInputNoOutput` agent. Follow its printed commands, using the AirPods address
shown by discovery for `pair`, `trust`, and `connect`. Stop discovery and quit
when pairing is complete. Pairing remains interactive so the intended device
can be selected. This local output contains Bluetooth addresses; do not paste
it unedited into an issue.

## Stereo playback and microphone input

Select A2DP in the audio settings for stereo playback. With the supported
MediaTek helper, select standard SBC with:

```bash
./scripts/airpods-tools stereo --codec sbc
```

This selects the onboard AirPods output, unmutes it, and moves all current
playback streams to it. It preserves the stored output volume. Adjust volume
through XFCE audio settings or `pavucontrol`.

The helper also accepts `sbc_xq_453`, `sbc_xq_512`, and `sbc_xq_552` when the
PulseAudio card exposes them. It checks availability and reads the selected
codec back before reporting success. Start with standard SBC when diagnosing
an unreliable connection; selecting a different codec alone does not establish
that a transport problem is resolved.

Microphone input uses the hands-free profile on the tested stack. Selecting
this profile changes playback to call-quality audio. Select the microphone
and measure its actual input samples with:

```bash
./scripts/airpods-tools calls
./scripts/airpods-tools meter --seconds 5
```

Speak normally during the check. The meter excludes monitor sources and prints
one-second RMS and peak levels without saving a recording. A bounded wait
reports a missing stream instead of waiting indefinitely. Changing speech
levels and unclipped samples support a working Linux input path; they do not
verify an application's device selection or microphone permission.

Restore stereo afterward:

```bash
./scripts/airpods-tools stereo --codec sbc
```

## Isolate a playback failure

First check volume, mute, the selected adapter, and the audio application's
output. Listen in both ears. A connected device or a running audio sink does
not by itself establish audible output.

For the supported MediaTek/PulseAudio configuration, compare playback without
and with the controls running:

```bash
~/.local/bin/airpods-xfce stop
./scripts/airpods-tools stereo --codec sbc
./scripts/airpods-tools transport-log --seconds 40
~/.local/bin/airpods-xfce start
./scripts/airpods-tools transport-log --seconds 30
```

Keep music playing during each capture. The helper temporarily sets PulseAudio
logging to debug, saves a local log under ignored `local/`, and returns logging
to normal level 2. It prints matching bitpool changes, skipped audio, underruns,
and errors. Both the saved log and printed excerpts can contain private data.
Review them locally and follow [PRIVACY.md](../PRIVACY.md) before sharing.

For controller initialization problems, use the redacted `scripts/check-system`
output from the [motherboard repository](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).
Do not remove or power off another adapter until you have checked whether it
serves connected input devices or other peripherals.

## Installed files and removal

| Location | Purpose |
| --- | --- |
| `~/.local/bin` and `~/.local/share` | Daemon, control CLI, tray, launcher, desktop entry, and user units |
| `~/.config/autostart/airpods-xfce.desktop` | XFCE session startup |
| `~/.config/AirPodsTrayApp` | Runtime settings and pairing keys; outside the checkout |
| `~/.local/state/librepods/status.json` | Daemon status watched by the tray |
| Checkout `local/` | Installation manifest, original-file backups, and local diagnostics |

`./scripts/uninstall` stops the services and restores original files where safe.
It retains pairing data and Debian packages. Keep the checkout's installation
manifest and backups until removal is complete.

The optional motherboard procedures separately install firmware under
`/usr/lib/firmware/mediatek/mt7927` and register `airpods-btusb` with DKMS.
`sudo ./scripts/remove-mt6639-driver` removes the driver override through DKMS
and reloads the stock module; firmware is retained. See the
[driver guide](mt6639-driver.md) before changing kernels or removing that fix.
