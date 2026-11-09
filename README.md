# AirPods controls for XFCE

An XFCE tray menu for AirPods battery readings, listening modes, and device
controls. This project builds the modified LibrePods daemon from
[omarchy-pods](https://github.com/thisisgm/omarchy-pods) and adds a native GTK 3
interface for XFCE's notification area. It does not require the Omarchy desktop
shell or its QML panel.

The daemon maintains the AirPods control connection. The tray reads its status
file and sends commands when a setting changes. Ordinary playback and microphone
capture use the system's existing audio and Bluetooth stack.

## Requirements and scope

The tested configuration is Debian 13 amd64, XFCE 4.20 on X11, BlueZ 5.82,
PulseAudio 17.0, and AirPods Pro 3. Other configurations have not been validated.
The dependency installer uses Debian package names and requires sudo access.
The tray requires an XFCE notification area and a graphical user session.

Basic Bluetooth pairing and audio must work before installing the controls.
Pair and trust the AirPods in Blueman, then confirm playback through the intended
adapter. For an ASUS ROG Crosshair X870E Hero with an uninitialized MediaTek
MT7927/MT6639 adapter, see the separate
[motherboard fix](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).
Its privileged scripts apply only to that board and two exact Debian kernel
ABIs. The tray itself does not require that motherboard.

## Installation

Install Git if needed, then clone the project with its pinned source submodules:

```bash
git clone --recurse-submodules https://github.com/tbols2721/xfce-airpods.git
cd xfce-airpods
./scripts/install-dependencies
./scripts/build
./scripts/install
systemctl --user enable --now librepods.service
~/.local/bin/airpods-xfce start
```

Run these commands as your desktop user. The dependency script invokes sudo
for APT; do not run the build or user-level installer as root. Review the
scripts before running them. The dependency installer prevents package removals
and does not replace the audio server.

The build runs 19 daemon CTest tests and six tray-status tests before staging
the installation. Files are installed under `~/.local`, with an XFCE autostart
entry under `~/.config/autostart`. Original files and the restore manifest stay
under ignored `local/` in the checkout. Keep that directory for uninstallation.

The installer adapts the daemon unit to `default.target` because some XFCE
sessions do not activate `graphical-session.target`. XFCE autostart imports the
display environment and starts the tray unit. Wear both AirPods for the initial
control-link check, and avoid running another LibrePods instance concurrently.

## Controls and audio

Click the headphone icon in the notification area, or launch **AirPods Pro
controls** from the application menu. The menu displays left, right, and case
battery readings. Unknown readings remain labeled **Unknown**. Case battery
depends on the last case packet received and may remain unknown while the
AirPods are being worn.

The device's capability flags determine which controls appear: noise
cancellation, transparency, adaptive listening, adaptive noise level,
conversation awareness, noise cancellation with one AirPod, and ear detection.
For the tested Pro 3, the daemon excludes the Off listening mode. GTK supplies
keyboard navigation through the menu and submenus.

The daemon pauses BLE scanning while its control link is connected, following
omarchy-pods' audio-interference handling. On the tested PulseAudio stack, A2DP
provides stereo playback and the hands-free profile provides microphone input
with call-quality playback. Select the appropriate profile in your audio
settings. The [operations guide](docs/operations.md) covers profile selection
and microphone checks, including the optional MediaTek-specific terminal helper.

```bash
~/.local/bin/airpods-xfce menu
~/.local/bin/airpods-xfce status
systemctl --user status librepods.service airpods-xfce-tray.service
```

## Troubleshooting and removal

Check service logs locally when the tray or daemon does not start:

```bash
journalctl --user -u librepods.service -u airpods-xfce-tray.service
```

Logs and full daemon status can contain device names, addresses, and local
paths. Pairing keys live outside the checkout in `~/.config/AirPodsTrayApp`.
Read [PRIVACY.md](PRIVACY.md) before sharing diagnostics or committing files.

To remove the integration:

```bash
./scripts/uninstall
```

This stops the services and restores files saved before the initial installation.
It retains subsequently modified files and reports their paths. Pairing data
and Debian packages are retained. Optional motherboard firmware and driver
changes have [separate removal procedures](docs/mt6639-driver.md).

## Technical documentation and credits

- [Architecture](docs/architecture.md): control and audio paths, services, and hardware support.
- [Operations](docs/operations.md): pairing, audio profiles, microphone metering, and diagnostics.
- [Validation](docs/validation.md): tested configuration, evidence, and remaining checks.
- [Motherboard firmware](docs/mt6639-firmware.md) and [driver](docs/mt6639-driver.md): optional hardware procedures.
- [Credits and licenses](NOTICE.md): LibrePods, omarchy-pods, and Linux/MT7927 contributors.

Both source repositories are pinned Git submodules; exact revisions are in
[`sources.lock.json`](sources.lock.json). `vendor/omarchy-pods` supplies the
active daemon, while `vendor/librepods-upstream` is a reference copy. Their
sources and license notices are retained unchanged.
