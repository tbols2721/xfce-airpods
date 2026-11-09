# Credits and component licenses

The AirPods protocol implementation is the work of **Kavish Devar** and the
[LibrePods project](https://github.com/librepods-org/librepods). It is the
foundation of this integration.

The active daemon comes from **GM / thisisgm** and
[omarchy-pods](https://github.com/thisisgm/omarchy-pods). That project bundles a
modified LibrePods daemon with Pro 3 support, a published status file, and
control commands. Its [upstream record](https://github.com/thisisgm/omarchy-pods/blob/fff7fec600a5b9a61cdb40e93eccbcceb4b8f824/daemon/UPSTREAM.md)
describes the original author and the modifications.

| Component | Revision or source | License |
| --- | --- | --- |
| Original GTK tray, automation, and documentation in this repository | This repository | MIT |
| Modified LibrePods daemon in `vendor/omarchy-pods/daemon` | `fff7fec600a5b9a61cdb40e93eccbcceb4b8f824` | GPL-3.0; see that component's LICENSE |
| Omarchy widget and other root files in its submodule | Same omarchy-pods revision | MIT, with the project's stated exceptions for product outlines |
| Upstream LibrePods reference submodule | `89356c08cea3db0b6b54792d9329d09a87cc85fa` | GPL-3.0; see that submodule's LICENSE |
| Linux Bluetooth device-ID patch | Linux stable v6.12.115 source | GPL-2.0-only |
| Downloaded ASUS/MediaTek firmware | Official ASUS driver archive | Vendor terms; binary not distributed here |

The GTK tray is a separate client of the daemon's status file and command
interface. This repository retains the original license notices in both
submodules. AirPods and ASUS product names identify the hardware; this project
has no vendor endorsement.

The motherboard work also builds on the Linux Bluetooth maintainers' driver
code, [Javier Tia / jetm's MT7927 work](https://github.com/jetm/mediatek-mt7927-dkms),
[Jean-François Marlière's MT6639 analysis](https://lists.openwall.net/linux-kernel/2026/02/08/473),
and the board-specific investigation in
[shaunstanislauslau/x870e-hero-linux-bluetooth-fix](https://github.com/shaunstanislauslau/x870e-hero-linux-bluetooth-fix).
The firmware container layout was checked against jetm's extraction code.
The preparation scripts download data directly and do not run third-party installers.

The standalone motherboard fix is published at
[tbols2721/asus-x870e-hero-bluetooth-fix](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix).
