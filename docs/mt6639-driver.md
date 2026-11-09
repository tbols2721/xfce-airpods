# Targeted MT6639 device-ID correction

The distribution's `btmtk` module already contains support for the MT6639 variant,
the zero-CHIPID workaround, the correct firmware filename, and firmware-section
filtering. The distribution's `btusb` module lacks the board's `0489:e13a` entry in
its quirks table. Generic USB Bluetooth matching therefore binds the interface
without selecting the MediaTek setup path.

The four-line patch adds that one device ID with `BTUSB_MEDIATEK` and
`BTUSB_WIDEBAND_SPEECH`. It changes no other USB device entries or driver logic.
Sources come from the upstream stable Linux v6.12.115 tag and are verified by
SHA-256 before the patch is applied.

The patched module was built successfully against both exact Debian header
sets on this machine:

| Kernel ABI | Patched module srcversion |
| --- | --- |
| `6.12.115+deb13.1-amd64` | `29AC947EAFB09F046C1A14A` |
| `6.12.116+deb13-amd64` | `29AC947EAFB09F046C1A14A` |

BTF debug metadata is omitted from this module build. Both builds completed
modpost and linked against their corresponding kernel symbol-version tables.
Successful compilation is a compatibility check, not proof of working radio
hardware or audio playback.

## Installation

The firmware must already be installed. Prepare the verified source tree and
run the installer from a desktop terminal:

```bash
./scripts/prepare-mt6639-driver
sudo ./scripts/install-mt6639-driver
```

The installer adds DKMS and the two exact kernel-header packages from Debian
stable. It builds both targets before installing either. It installs the
module through DKMS, which archives the distribution's original module,
and reloads Bluetooth. Connected Bluetooth devices disconnect during reload.
This machine has Secure Boot disabled; the installer refuses an enabled
Secure Boot configuration rather than changing its security settings.

The initial workaround is restricted to the two tested ABIs. DKMS automatic
installation is disabled so this older driver source cannot silently override
future kernel fixes. When using a later kernel, check its stock device-ID
support and prepare a matching fix only if it is still needed.

The installer verifies that the resolved module comes from DKMS and that its
srcversion matches the loaded module. It then identifies the onboard adapter
by USB vendor and product IDs, requires a nonzero Bluetooth address, and powers
it on. Adapter numbering can change during reload.

Build, installation, or module-load failures trigger an attempt to remove the
DKMS override and reload the stock driver. Failed DKMS cleanup preserves the
source tree for diagnosis. If the correct module loads but the controller does
not initialize, the installer keeps the installed fix and reports that a full
power-off may be required before retrying.

To remove the override:

```bash
sudo ./scripts/remove-mt6639-driver
```

Removal retains the verified firmware. It attempts to reload a driver and
restart Bluetooth even if DKMS removal fails.

## Review and acceptance

The device-ID patch and installation plan received independent read-only
reviews through Claude CLI and Astra. Their packaging findings were corrected,
including a reproduced repeat-preparation failure. Preparing the source twice
now produces a valid seven-file manifest.

The user ran the installer on 9 November 2026. DKMS installed both verified
targets. The running kernel resolves `btusb` to its DKMS copy, and the loaded
module's srcversion matches `29AC947EAFB09F046C1A14A`.

The onboard controller then initialized, obtained a nonzero Bluetooth address,
and became visible to BlueZ. Independent live checks confirmed the USB identity
`0489:e13a`, manufacturer MediaTek, Bluetooth 5.4, powered state, and UP RUNNING
status with zero receive and transmit errors at the time of inspection. This
confirms that the firmware and device-ID correction activated the adapter.

The external Realtek adapter was temporarily powered off for isolation after
checking it had no connected devices. The AirPods were subsequently paired
with the onboard adapter. The user confirmed audible stereo, the daemon and
tray were restored, and an onboard microphone input test passed. See
[validation.md](validation.md) for the bounded captures and remaining
longer-duration tests.
