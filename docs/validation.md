# Validation and compatibility

The reference configuration below was tested on 9 November 2026. These results
describe a bounded hardware test, not a guarantee for every AirPods model,
Bluetooth adapter, or Linux distribution.

## Reference configuration

| Component | Tested configuration |
| --- | --- |
| Distribution and desktop | Debian 13 amd64, XFCE 4.20, X11 |
| Audio stack | BlueZ 5.82 and PulseAudio 17.0 |
| Headphones | AirPods Pro 3 |
| Motherboard adapter | MediaTek MT7927/MT6639, USB `0489:e13a`, ASUS ROG Crosshair X870E Hero |
| Kernel used for hardware tests | `6.12.115+deb13.1-amd64` |
| Additional driver build and DKMS installation | `6.12.116+deb13-amd64`; not boot-tested |
| Daemon source | omarchy-pods `fff7fec600a5b9a61cdb40e93eccbcceb4b8f824` |

## Completed checks

| Area | Result and evidence |
| --- | --- |
| Daemon build | All 19 registered CTest tests passed |
| Tray status handling | All six Python tests passed |
| Desktop and service files | Desktop entries and user service units passed their validators |
| Fresh public checkout | Built from the pinned submodules; both test suites passed |
| Tray integration | GTK tray embedded in the XFCE notification area; menu labels and controls inspected |
| Control connection | Separate left/right battery readings and in-ear state received |
| Listening modes | Transparency, Adaptive, and Noise Cancellation commands received matching device state; original mode restored |
| Local settings | Pairing directory mode 0700, settings and status files mode 0600, control socket mode 0700 |
| Onboard initialization | Firmware hash and ownership, DKMS module path, loaded srcversion, USB identity, and powered controller verified |
| Stereo playback | Standard SBC A2DP; clear output confirmed by listening in both ears |
| Transport baseline | 40-second debug capture with no matching bitpool, skipping, underrun, error, or failure lines; zero controller receive/transmit errors at inspection |
| Controls with playback | Additional 30-second capture with daemon and tray running; no matching transport-degradation lines |
| Microphone input | Five seconds of speech sampled from the real Bluetooth source at 16 kHz mono; changing input levels without clipping |
| Profile restoration | A2DP/SBC stereo restored and onboard connection verified after microphone testing |

The microphone check measured one-second RMS levels from -33.0 to -18.7 dBFS
and a maximum sample magnitude of 14883 out of 32768. Only numeric results were
retained; no recording is included in the repository. This establishes input
through the Linux audio stack. It does not establish that a particular browser
or conferencing application has selected the source or granted microphone
permission.

## Interpretation and limits

The successful reference configuration uses the onboard MediaTek adapter with
the optional firmware and driver correction. Testing on a separate external
Realtek adapter encountered skips, underruns, and degraded SBC bitpool, including
when the daemon was stopped. Its underlying failure was not established.
Those observations do not establish a defect in the adapter or an interference
problem, and do not establish general Realtek incompatibility.

A clean short capture and successful listening test establish a working
baseline. They do not establish full-day reliability. The second supported
kernel ABI was built and installed, but did not receive a booted hardware test.

Fresh-login startup, suspend/resume, longer playback, conferencing-application
input selection, and case-battery refresh still need hardware testing.
Conversation awareness, one-AirPod noise cancellation, and physical ear-removal
behavior have controls but have not received separate physical acceptance tests.
PipeWire, Wayland, other distributions, and other AirPods models are outside the
tested configuration.

## Reproducing the checks

Run `./scripts/build` to execute both software test suites. Use the
[operations guide](operations.md) for playback, microphone metering, and bounded
transport captures. Use the motherboard repository's redacted
[`check-system`](https://github.com/tbols2721/asus-x870e-hero-bluetooth-fix/blob/main/scripts/check-system)
for initialization checks. Test each layer separately and record the actual
result rather than inferring success from installation or connection state.

Follow [PRIVACY.md](../PRIVACY.md) when preparing a public compatibility report.
