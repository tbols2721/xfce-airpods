# Optional MT6639 Bluetooth firmware

The ASUS ROG Crosshair X870E Hero exposes its onboard MT7927/MT6639 Bluetooth
function as USB device `0489:e13a`. A missing firmware payload can leave the
controller down with an all-zero address. Identify the adapter by USB identity;
its `hci` number can change after reload or reboot.

The exact payload below was absent from the Debian stable and backports
`firmware-mediatek` packages inspected on 9 November 2026. The tested `btmtk`
module requests `mediatek/mt7927/BT_RAM_CODE_MT6639_2_1_hdr.bin`. Check current
package contents and controller behavior before applying this scoped workaround.

## Firmware source and integrity

`scripts/prepare-mt6639-firmware` downloads the official ASUS MTK WiFi driver
archive V5.6.0.3998, dated 9 July 2025, and extracts the Bluetooth payload from
`mtkwlan.dat`. It treats the archive as data and does not run the Windows
installer. The archive is linked from the
[ASUS support page](https://www.asus.com/uk/supportonly/rog%20crosshair%20x870e%20hero/helpdesk_download/).

| Artifact | SHA-256 |
| --- | --- |
| ASUS archive | `b377fffa28208bb1671a0eb219c84c62fba4cd6f92161b74e4b0909476307cc8` |
| Extracted payload, 688341 bytes | `669c5c99a0c59c85c1285d3d1b8b31915c2d31341a2244f4eddcbfd60ffbbc76` |

The archive hash matches ASUS's published checksum. The payload header reports
build timestamp `20250606201235`. Downloaded and extracted binaries stay under
ignored `local/firmware`; this repository does not redistribute them.

## Installation

Review the scripts and ensure Python 3 and `initramfs-tools` are available.
Run from the checkout:

```bash
./scripts/prepare-mt6639-firmware
sudo ./scripts/install-mt6639-firmware
```

The installer rechecks the payload hash and installs it as root-owned mode
0644 at `/usr/lib/firmware/mediatek/mt7927/BT_RAM_CODE_MT6639_2_1_hdr.bin`. It
backs up a differing existing file under `/var/lib/airpods-xfce/firmware-backups`
and updates installed initramfs images. The backup directory name is shared
with the companion motherboard scripts.

This step does not replace or reload kernel modules. Firmware installation
alone does not establish that the controller works. The two affected Debian
ABIs also need the [device-ID correction](mt6639-driver.md). Verify controller
initialization before pairing.

Driver removal retains this firmware. Firmware removal or restoration is a
separate administrative operation; the installer does not provide an automated
firmware uninstaller.

The extraction layout was checked against
[jetm/mediatek-mt7927-dkms](https://github.com/jetm/mediatek-mt7927-dkms/blob/main/extract_firmware.py).
See [NOTICE.md](../NOTICE.md) for contributor credits and component licenses.
