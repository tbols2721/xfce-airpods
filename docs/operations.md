# Operations and diagnostic scripts

The GTK tray controls the existing LibrePods daemon. The additional repository
tool, `scripts/airpods-tools`, records the terminal operations used during this
setup. It identifies the onboard adapter by USB ID `0489:e13a`, rather than
assuming that a controller number will remain fixed. Its audio operations
require one paired AirPods device on that adapter. These helpers target the
tested ASUS motherboard; the tray itself uses the daemon's normal interface.

## Normal use and pairing

Start the controls and inspect their state with:

```bash
~/.local/bin/airpods-xfce start
~/.local/bin/airpods-xfce menu
~/.local/bin/airpods-xfce status
./scripts/airpods-tools status
```

The adapter-aware status command reports controller identity, connection,
profile, and codec without printing the personal device name or Bluetooth
address. The complete daemon status is available through
`~/.local/bin/librepods-ctl status`; it includes the personal device name.

For a new pairing, put both AirPods in the open case and double-tap its front
until the status light flashes white. Keep the lid open. Run:

```bash
./scripts/airpods-tools pair-shell
```

This helper prints the exact controller-selection command, then opens a BlueZ
shell with a `NoInputNoOutput` agent. Follow the printed commands. Use the
AirPods address shown by discovery for `pair`, `trust`, and `connect`, then
stop discovery and quit. The helper deliberately leaves the pairing action
interactive so the user can identify the intended headphones.

## Stereo playback and microphone use

The accepted playback test used standard SBC stereo at 40 percent output
volume. Select that profile and codec with:

```bash
./scripts/airpods-tools stereo --codec sbc
```

This selects the onboard AirPods output, clears output mute, and routes current
playback streams to it. It preserves the stored output volume. Use the normal
XFCE audio controls or `pavucontrol` to adjust volume.

PulseAudio also exposes SBC XQ variants. The helper accepts `sbc_xq_453`,
`sbc_xq_512`, and `sbc_xq_552` to reproduce codec comparisons, but validates
availability and reads the selected codec back before reporting success.
Changing codecs did not fix the old adapter's playback failure. Standard SBC
on the newly activated onboard radio was the accepted baseline.

The AirPods microphone uses the hands-free profile on this installation.
Selecting it changes stereo playback to call-quality audio. Switch to it and
measure actual input samples with:

```bash
./scripts/airpods-tools calls
./scripts/airpods-tools meter --seconds 5
```

Speak normally during the meter check. It selects the actual Bluetooth input,
excluding monitor sources, and prints one-second RMS and peak levels. It does
not save a recording. A bounded wait reports a missing stream rather than
waiting indefinitely. Changing speech levels and unclipped samples support a
working input-path result; they do not verify a conferencing application's
device selection or permissions.

Restore stereo after the check:

```bash
./scripts/airpods-tools stereo --codec sbc
```

## Isolating a playback failure

Stop the app layer while retaining ordinary Bluetooth audio:

```bash
~/.local/bin/airpods-xfce stop
./scripts/airpods-tools stereo --codec sbc
./scripts/airpods-tools transport-log --seconds 40
```

Keep music playing during the diagnostic capture. The helper temporarily sets
PulseAudio logging to debug, stores a local log under ignored `local/`, then
returns logging to normal level 2. It summarizes bitpool changes, skipped
audio, underruns, and error lines. A clean bounded capture is useful evidence,
but the listener must still confirm audible output in both ears.

Restart the app layer and compare the result:

```bash
~/.local/bin/airpods-xfce start
./scripts/airpods-tools transport-log --seconds 30
```

Logs and recordings are different evidence. The transport helper logs audio
server messages, not microphone audio. Neither raw logs nor pairing settings
belong in public issue reports without inspection. For a report about onboard
initialization, use the redacted `scripts/check-system` output from the
[motherboard repository](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).

## Installed changes and maintenance

| Location or component | Change |
| --- | --- |
| `~/.local/bin` and `~/.local/share` | Built daemon, control CLI, GTK tray, launcher, and user units |
| `~/.config/autostart/airpods-xfce.desktop` | XFCE session startup |
| `~/.local/share/systemd/user/librepods.service` | Headless daemon started through `default.target` |
| `~/.config/AirPodsTrayApp` | Owner-only runtime settings and pairing keys, outside Git |
| `~/.local/state/librepods/status.json` | Owner-only daemon status watched by the tray |
| `/usr/lib/firmware/mediatek/mt7927` | Verified vendor Bluetooth payload |
| `/usr/src/airpods-btusb-1.0` and `/var/lib/dkms/airpods-btusb` | Reviewed source and DKMS state |
| Kernel `updates/dkms` directories | Corrected btusb module for the two verified ABIs |
| Debian packages | Qt/build dependencies, DKMS, and matching kernel headers from stable |

Debian package sources, XFCE, and PulseAudio were retained. No unstable suite
was enabled. The external Realtek radio was powered off for isolation; the
user can unplug it. The motherboard's external antenna serves the native radio.

DKMS archives the original stock modules while the override is installed.
`sudo ./scripts/remove-mt6639-driver` removes the override and restores the
stock module through DKMS. `./scripts/uninstall` separately removes the user
integration and restores its original files where safe. Both retain pairing
data and the verified firmware. Keep the ignored installation manifest and
backups if the user integration may need removal.

The kernel correction is restricted to the two recorded ABIs, with automatic
installation disabled. A future kernel requires checking whether its stock
driver already recognizes this device. The current driver source must not be
silently installed over a newer kernel's Bluetooth fixes.
