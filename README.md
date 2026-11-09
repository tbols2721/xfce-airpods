# AirPods Pro controls for XFCE

This repository configures LibrePods and the control interface from
[omarchy-pods](https://github.com/thisisgm/omarchy-pods) for Debian 13 with XFCE.
The modified LibrePods daemon owns the Bluetooth control connection. A small
GTK 3 application puts its battery readings and controls in the existing XFCE
notification area. The application watches the daemon's status file and starts
the control command only when a setting changes.

The Omarchy QML panel depends on Omarchy's desktop shell. This repository uses
the same daemon interface through a native XFCE tray menu. It runs one daemon
in headless mode, with a separate tray process.

Both source repositories are pinned Git submodules:

| Source | Role |
| --- | --- |
| `vendor/omarchy-pods` | Modified daemon with Pro 3 support, status JSON, and control commands |
| `vendor/librepods-upstream` | Upstream LibrePods source for comparison and future updates |

The pinned source revisions are recorded in `sources.lock.json`. The daemon
sources are unchanged. Their licenses remain in their respective submodules.

## Installation

From a fresh checkout, initialize the source repositories and install the Debian
build dependencies. The dependency installer requires sudo authentication.
It prevents package removals and retains the existing audio server.

```bash
git clone --recurse-submodules https://github.com/tbols2721/xfce-airpods.git
cd xfce-airpods
git submodule update --init --recursive
./scripts/install-dependencies
./scripts/build
./scripts/install
systemctl --user enable --now librepods.service
~/.local/bin/airpods-xfce start
```

The build runs the daemon's CTest suite and the XFCE status tests before staging
the installation. Files go into `~/.local`, with an XFCE autostart entry under
`~/.config/autostart`. Original files and the installation manifest stay under
the ignored `local/` directory in this repository. Keep that directory to retain
the uninstall information.

The onboard MT7927/MT6639 adapter needs additional support on this machine.
See [the firmware procedure](docs/mt6639-firmware.md) and
[the tested device-ID correction](docs/mt6639-driver.md). These procedures are
separate from the tray installation and use the two recorded Debian kernel ABIs.

The supplied daemon unit normally starts through `graphical-session.target`.
This machine does not activate that target, so the installer changes its
startup target to `default.target`. The original daemon hardening remains in
place. XFCE autostart imports the display environment and starts the tray unit.

Pair the AirPods through Blueman. Wear both AirPods for the first control-link
test. Initial pairing can require several connection attempts while Bluetooth
service discovery completes. Trust the paired device in Blueman to support
later reconnection.

## Controls

Click the headphone icon in the notification area, or launch **AirPods Pro
controls** from the application menu. The menu shows separate left, right, and
case battery readings. Unknown readings remain labeled **Unknown**.

The connected device's capability flags determine which controls appear:
noise cancellation, transparency, adaptive listening, adaptive noise level,
conversation awareness, noise cancellation with one AirPod, and ear detection.
For the tested Pro 3, the daemon excludes the Off listening mode. GTK supplies
keyboard navigation through the menu and its submenus.

Case battery can remain unknown while the AirPods are being worn. Its value
depends on the last case packet received. The daemon pauses BLE scanning while
the control link is connected to avoid the audio interference documented by
omarchy-pods.

The daemon selects the playback profile available from the current audio
server. This machine uses PulseAudio 17 and exposes SBC and SBC XQ stereo
codecs. The user confirmed clear stereo playback through the corrected onboard
adapter using standard SBC. Microphone input was separately verified at 16 kHz
in the hands-free profile. Stereo playback was restored after that test.

```bash
~/.local/bin/airpods-xfce menu
~/.local/bin/airpods-xfce status
~/.local/bin/librepods-ctl status
systemctl --user status librepods.service airpods-xfce-tray.service
journalctl --user -u librepods.service -u airpods-xfce-tray.service
```

Pairing keys stay in `~/.config/AirPodsTrayApp`, outside this repository. The
daemon creates that directory with mode 0700 and its settings file with mode
0600. Status files and the control socket also have owner-only access. Do not
commit machine settings or raw Bluetooth logs.

## Verification and removal

See `docs/validation.md` for the checks completed on this machine and the
remaining physical tests. Local hardware-test results are stored in the
ignored `local/` directory.

The [setup report](docs/setup-report.md) explains the architecture, investigation,
and fix. The [operations guide](docs/operations.md) documents pairing, profile
selection, microphone metering, and bounded transport captures. The complete
terminal helper is `scripts/airpods-tools`.

See [NOTICE.md](NOTICE.md) for credits to Kavish Devar and LibrePods, GM and
omarchy-pods, and the Linux and MT7927 contributors. Component licenses remain
with their sources. Public copies are available as
[xfce-airpods](https://github.com/tbols2721/xfce-airpods) and the standalone
[motherboard fix](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).

To remove the integration, run:

```bash
./scripts/uninstall
```

This stops the services and restores files from before the initial installation.
It keeps files that have changed since installation and reports their paths.
Pairing data and Debian packages are retained.
