# Optional MT6639 device-ID correction

This procedure targets the ASUS ROG Crosshair X870E Hero's onboard MediaTek
MT7927/MT6639 adapter, USB `0489:e13a`. It is separate from the XFCE tray
installation. The standalone
[motherboard repository](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix)
provides the full explanation and a redacted system-check script.

## Supported configuration

The affected stock Debian kernels contain MT6639 support in `btmtk`, including
the chip-ID workaround, firmware path, and firmware-section filtering. Their
`btusb` quirks table lacks the board's device-ID entry. Generic USB matching can
therefore bind the interface without selecting MediaTek initialization.

The four-line patch selects `BTUSB_MEDIATEK` and `BTUSB_WIDEBAND_SPEECH` for
this device. Source files come from Linux stable v6.12.115 and are checked
against recorded SHA-256 hashes before patching.

| Supported kernel ABI | Patched module srcversion | Validation |
| --- | --- | --- |
| `6.12.115+deb13.1-amd64` | `29AC947EAFB09F046C1A14A` | Built, installed, and hardware-tested |
| `6.12.116+deb13-amd64` | `29AC947EAFB09F046C1A14A` | Built and installed; not boot-tested |

The installer checks the board and running ABI. It refuses an enabled Secure
Boot configuration and does not configure module signing. BTF debug metadata
is omitted from the module build. Other kernels require a separate source and
compatibility review.

## Installation and verification

Install the [verified firmware](mt6639-firmware.md) first. Ensure Python 3,
`python3-dbus`, `patch`, and BlueZ are available. Review the scripts, keep a
non-Bluetooth input device available, and run from the checkout:

```bash
./scripts/prepare-mt6639-driver
sudo ./scripts/install-mt6639-driver
```

The installer obtains DKMS and both exact kernel-header packages through APT,
builds both targets before installing either, and reloads Bluetooth. Connected
Bluetooth devices disconnect during reload. If the configured repositories no
longer provide those headers, reassess the supported kernel scope rather than
substituting an unreviewed version.

The source-preparation manifest covers seven required build files. The
installer verifies staged and copied sources, the resolved module path, and
the loaded module's srcversion. It then identifies the adapter by USB identity,
requires a nonzero Bluetooth address, and powers it on. Controller numbering
can change after reload or reboot.

Verify the installed and loaded module separately:

```bash
/usr/sbin/modinfo -n btusb
/usr/sbin/modinfo -F srcversion btusb
cat /sys/module/btusb/srcversion
/usr/sbin/dkms status -m airpods-btusb
```

The module path should resolve under `updates/dkms`, and both srcversion
checks should match the table. Confirm controller initialization before
attempting pairing, then test audible playback and microphone input separately.
See [validation.md](validation.md) for the reference test results and limits.

Build, installation, or load failures trigger an attempted rollback. Failed
DKMS cleanup preserves sources for diagnosis. If the verified module loads but
the controller does not initialize, the installer retains the fix and reports
that a full power-off may be required. That message does not establish that
every initialization failure has a power-state cause.

## Removal and future kernels

```bash
sudo ./scripts/remove-mt6639-driver
```

DKMS archives the original modules while the override is installed. Removal
restores the stock module through DKMS, reloads Bluetooth, and retains firmware.
Recovery handlers attempt to reload a driver and restart Bluetooth even if
cleanup fails. Inspect the reported state before treating recovery as complete.
On the affected stock kernels, removal also removes the required device-ID fix.

`AUTOINSTALL="no"` prevents this older source from automatically overriding
future kernel drivers. Before changing kernels, check whether the stock driver
already supports the device. If another correction is needed, review source
for that kernel and test it explicitly; do not broaden the version filter only
because an untested build compiles.

The installer prints controller addresses and kernel log excerpts during local
verification. Follow [PRIVACY.md](../PRIVACY.md) before publishing that output.
