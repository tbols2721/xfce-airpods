# Machine validation, 9 November 2026

The target is Debian 13 with XFCE 4.20, X11, BlueZ 5.82, and PulseAudio 17.0.
The connected hardware identifies itself as AirPods Pro 3. Metadata reported
A3063 during initial testing and A3064 after the onboard connection was restored.

## Completed checks

The daemon built from the pinned omarchy-pods revision. All 19 registered CTest
tests passed. All six tests for the XFCE status reader passed. Desktop entries
passed `desktop-file-validate`, and both service units passed
`systemd-analyze --user verify`.

The installed daemon and GTK tray both ran successfully. The tray reported that
it was embedded in the XFCE notification area. A screenshot of the actual mapped
menu confirmed readable battery rows, listening modes, capability-gated toggles,
and ear-detection controls. The local screenshot is excluded from Git.

The live control connection reported both AirPods in ear with independent
battery readings. Transparency, Adaptive, and Noise Cancellation commands each
produced the expected mode readback from the AirPods. The noise setter does not
change its own state optimistically, so these readbacks required incoming device
state. The original Noise Cancellation setting was restored.

The microphone was tested through the hands-free profile at 16 kHz, mono.
Ten seconds of samples from the actual Bluetooth microphone source showed
changing input levels while the user spoke. One-second RMS levels ranged from
-48.0 to -31.1 dBFS. The maximum observed sample magnitude was 4547 out of
32768, with no clipping. No audio recording was retained. This verifies the
Linux input path; a browser or conferencing application has not been tested.

Configuration files were checked for owner-only access. The pairing settings
directory is mode 0700, its settings file is 0600, the status file is 0600, and
the control socket is 0700. None of these files is included in Git.

## Playback investigation

The user reported intermittent or silent YouTube playback despite Chrome being
routed to an active, unmuted AirPods output. An output monitor contained nonzero
audio samples. Resetting the Bluetooth playback profile briefly restored audible
sound, but the user subsequently reported poor or missing playback.

PulseAudio exposes SBC and three SBC XQ variants through its Bluetooth message
API. SBC XQ at 453 kbps was selected and read back successfully, but the user
reported that playback still failed. Codec selection alone is therefore not a
verified fix.

The daemon and tray were temporarily stopped to test ordinary Bluetooth audio
with standard SBC. The same silence and one-ear playback occurred in that
state. PulseAudio debug logs showed repeated audio skips and underruns, with
SBC bitpool dropping from 29 to 2. Debug logging was then restored to its normal
level. Both channels contained nonzero music at equal output volume. The user
confirmed that the same AirPods work normally on a phone.

The onboard MediaTek MT7927/MT6639 was down with a zero address. Its required
Bluetooth firmware was missing and was not present in the inspected Debian
stable or backports firmware packages. The matching payload was extracted from
an official ASUS archive, checked against ASUS's published archive hash, and
installed by the user. The installed file's SHA-256 and root ownership were
independently verified. A separate missing btusb device-ID entry was identified;
the correction builds for both installed kernel ABIs. The user installed it
through DKMS and reloaded the driver. Live inspection confirmed that the loaded
module matches the tested srcversion and resolves to the DKMS path. The onboard
MediaTek controller initialized and became powered and UP RUNNING with zero
controller errors at the time of inspection. Pairing and audio tests on that
adapter were the next acceptance checks.

At that stage, audible playback remained an open acceptance condition. A
RUNNING sink or an active Bluetooth transport alone was not proof that the
user could hear sound. The next section records the successful listening test.

## Accepted onboard playback and microphone

Pairing on the onboard adapter succeeded after the user put the AirPods into
white-flashing pairing mode. BlueZ reported the device paired and trusted,
with services resolved on the controller identified by USB `0489:e13a`.
Chrome was routed to that controller's A2DP output using standard SBC at
40 percent volume. The user confirmed clear audio in both ears.

A 40-second baseline PulseAudio debug capture contained no matching bitpool,
skipping, underrun, error, or failure lines. The onboard controller showed
zero receive and transmit errors. LibrePods and the GTK tray were then
restored. The control connection reported both AirPods in ear with separate
battery readings, the tray reported itself embedded in XFCE, and a second
30-second transport capture also contained no matching degradation lines.

The microphone was then retested through the onboard adapter. Its hands-free
profile exposed a real Bluetooth source at 16 kHz, mono. Five seconds of speech
produced one-second RMS levels from -33.0 to -18.7 dBFS, with maximum sample
magnitude 14883 out of 32768 and no clipping. Only numeric level results were
retained. The helper restored the onboard A2DP/SBC stereo profile afterward;
the final state was paired and connected on the onboard controller.

The separate public XFCE checkout was then built from its pinned submodules.
It also passed all 19 daemon CTest tests and all six tray-status tests.

These results establish working stereo and microphone input on the new radio
and working daemon/tray integration. They are bounded live tests, not proof
of reliability over a full workday.

## Remaining checks

Verify a fresh graphical login, suspend/resume, longer-duration playback,
conferencing-application input selection, and case battery refresh on real hardware.
Conversation awareness, one-AirPod noise cancellation, and physical removal
behavior have UI controls but have not received separate physical acceptance
tests. Stereo playback and the microphone use different Bluetooth profiles on
this installation.
