# Onboard MT6639 Bluetooth firmware

The ASUS ROG Crosshair X870E Hero exposes its onboard MT7927/MT6639 Bluetooth
adapter as USB device `0489:e13a`. On this machine it appears as hci0 but stays
down with an all-zero address. The external Realtek adapter is hci1.

The specific Bluetooth payload is absent from Debian's stable and backports
`firmware-mediatek` packages checked on 9 November 2026. The running btmtk
module declares the required path as
`mediatek/mt7927/BT_RAM_CODE_MT6639_2_1_hdr.bin`.

`scripts/prepare-mt6639-firmware` downloads a Windows driver archive from
[ASUS's official support site](https://www.asus.com/uk/supportonly/rog%20crosshair%20x870e%20hero/helpdesk_download/)
and extracts the Bluetooth payload as data. It does not run the Windows
installer. The archive is the MTK WiFi package V5.6.0.3998 dated 9 July 2025;
the Bluetooth payload is embedded in its `mtkwlan.dat` container.

| Artifact | SHA-256 |
| --- | --- |
| ASUS archive | `b377fffa28208bb1671a0eb219c84c62fba4cd6f92161b74e4b0909476307cc8` |
| Extracted Bluetooth payload, 688341 bytes | `669c5c99a0c59c85c1285d3d1b8b31915c2d31341a2244f4eddcbfd60ffbbc76` |

The archive hash matches ASUS's published checksum. The payload header reports
build timestamp `20250606201235`. Both the archive and extracted binary remain
in the ignored `local/firmware` directory. This repository does not redistribute
the firmware binaries.

Prepare and install the file with:

```bash
./scripts/prepare-mt6639-firmware
sudo ./scripts/install-mt6639-firmware
```

The installer verifies the payload hash before copying it to the path declared
by the installed driver. It saves a differing existing file under
`/var/lib/airpods-xfce/firmware-backups`, then updates installed initramfs images.
It installs no kernel modules, package repositories, or desktop components.

Firmware installation alone does not establish that the adapter works. The
distribution's btmtk module contains MT6639 support, but the stock btusb modules
for kernels 6.12.115 and 6.12.116 lack this adapter's specific device-ID entry.
That driver gap remains a separate activation requirement. Verify the actual
controller and kernel logs before attempting AirPods pairing on this adapter.
The prepared correction and rollback procedure are described in
[mt6639-driver.md](mt6639-driver.md).

The container format was checked against the extraction implementation in
[jetm/mediatek-mt7927-dkms](https://github.com/jetm/mediatek-mt7927-dkms/blob/main/extract_firmware.py).
No third-party installation script was executed.
