# Privacy and diagnostic reports

Keep diagnostic reports limited to the information needed to reproduce a
problem. Hardware model names, USB vendor/product IDs, kernel versions,
software revisions, and firmware checksums identify a configuration without
requiring a device's unique Bluetooth address.

## Information to keep local

Do not publish Bluetooth addresses, device serial numbers, personalized device
names, usernames, hostnames, absolute home-directory paths, credentials, pairing
keys, or microphone recordings. Replace identifying fields consistently with
labels such as `<CONTROLLER_ADDRESS>`, `<DEVICE_ADDRESS>`, `<USER>`, and `<HOST>`
when a small diagnostic excerpt is necessary.

BlueZ pairing state under `/var/lib/bluetooth` contains keys and unique device
identifiers. Do not upload or commit that directory. Inspect screenshots as
well as text: terminal prompts, Bluetooth menus, and desktop notifications can
reveal personal information.

Raw `bluetoothctl`, `btmon`, `journalctl`, PulseAudio, and installer output can
contain private fields. Git ignore rules do not filter terminal output, issue
comments, release assets, or files deliberately added with `git add -f`.

## Preparing a useful report

Include the hardware model, USB product identity, distribution, running kernel,
relevant software versions, exact command or control that failed, and observed
behavior. State whether initialization, pairing, playback, or microphone input
is affected. Prefer a short redacted excerpt to a complete log archive.

`./scripts/airpods-tools status` omits Bluetooth addresses and personalized
names, but requires the supported onboard MediaTek adapter and PulseAudio.
For motherboard initialization, use the redacted `check-system` script in the
[companion repository](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).

Full daemon status can include a personalized device name. `pair-shell` prints
addresses, and `transport-log` saves raw server logs and prints excerpts. The
microphone meter prints numeric levels and does not save a recording.

## Runtime data and contributions

LibrePods settings and pairing keys live under `~/.config/AirPodsTrayApp`;
status lives under `~/.local/state/librepods`. These paths are outside the
checkout and must not be copied into it for an issue report. Installation
manifests and backups under `local/` can also contain local paths or settings.

Before committing, inspect staged content and commit identity:

```bash
git diff --cached --check
git diff --cached
git status --short
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

Use a GitHub noreply address if you do not want a personal email in public
commit metadata. Keep ignored build files, backups, downloads, captures,
credentials, and runtime settings untracked. Public upstream submodules retain
their authors' existing attribution and license notices.
Deleting a file in a later commit does not remove it from earlier Git history.
