#!/usr/bin/python3
"""XFCE tray controls for the status interface in omarchy-pods."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import sys

MODES = ((1, "Noise cancellation", "anc"), (2, "Transparency", "transparency"),
         (3, "Adaptive", "adaptive"), (0, "Off", "off"))


def read_status(path):
    """Read a complete schema-1 snapshot, including the initial empty state."""
    # Sample input: {"schema_version":1,"connected":false,"noise_mode":-1}
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        return {}, "AirPods daemon is not running"
    except (OSError, ValueError) as error:
        return {}, f"Cannot read AirPods status: {error}"
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int:
        return {}, "Invalid AirPods status schema"
    if value["schema_version"] != 1:
        return {}, f"Unsupported AirPods status schema: {value['schema_version']}"
    return value, ""


def available_modes(status):
    if not status.get("supports_noise_control", False):
        return []
    return [(number, label, verb) for number, label, verb in MODES
            if (number != 0 or status.get("supports_noise_off", True))
            and (number != 3 or status.get("supports_adaptive", False))]


def battery_text(status, key):
    pod = status.get(key)
    if not isinstance(pod, dict) or not pod.get("available", False):
        return "Unknown"
    level = pod.get("level")
    if type(level) not in (int, float) or not 0 <= level <= 100:
        return "Unknown"
    suffix = " (charging)" if pod.get("charging") else ""
    if pod.get("in_ear"):
        suffix += " (in ear)"
    return f"{level:g}%{suffix}"


def tooltip(status, error=""):
    if error:
        return error
    name = status.get("model_name") or "AirPods"
    connection = "Connected" if status.get("connected") else "Disconnected"
    rows = [f"{name}: {connection}"]
    for key, label in (("left", "Left"), ("right", "Right"), ("case", "Case")):
        rows.append(f"{label}: {battery_text(status, key)}")
    return "\n".join(rows)


def run_tray(status_path, control):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gio, GLib, Gtk

    class Tray:
        def __init__(self):
            self.status = {}
            self.error = ""
            self.pending = []
            self.icon = Gtk.StatusIcon.new_from_icon_name("audio-headphones-symbolic")
            self.icon.set_title("AirPods Pro controls")
            self.icon.connect("activate", self.popup)
            self.icon.connect("popup-menu", self.popup)
            self.icon.set_visible(True)
            status_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.monitor = Gio.File.new_for_path(str(status_path.parent)).monitor_directory(
                Gio.FileMonitorFlags.NONE, None)
            self.monitor.connect("changed", self.changed)
            self.reload()
            GLib.timeout_add_seconds(2, self.report_embedding)

        def report_embedding(self):
            print(f"XFCE tray embedded: {self.icon.is_embedded()}", flush=True)
            return False

        def reload(self):
            self.status, self.error = read_status(status_path)
            self.icon.set_tooltip_text(tooltip(self.status, self.error))

        def changed(self, monitor, file, other_file, event):
            paths = [item.get_basename() for item in (file, other_file) if item]
            if status_path.name in paths:
                self.reload()

        def command(self, verb):
            try:
                process = Gio.Subprocess.new(
                    [str(control), verb],
                    Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
            except GLib.Error as error:
                print(f"Cannot start AirPods control: {error}", file=sys.stderr, flush=True)
                return
            self.pending.append(process)
            process.communicate_utf8_async(None, None, self.completed)

        def completed(self, process, result):
            try:
                _, output, error = process.communicate_utf8_finish(result)
                if not process.get_successful():
                    print(f"AirPods command failed: {error.strip()}", file=sys.stderr, flush=True)
                    self.icon.set_tooltip_text(f"AirPods command failed: {error.strip()}")
            except GLib.Error as error:
                print(f"AirPods control error: {error}", file=sys.stderr, flush=True)
            finally:
                self.pending.remove(process)

        def label(self, menu, text):
            item = Gtk.MenuItem.new_with_label(text)
            item.set_sensitive(False)
            menu.append(item)

        def radio(self, menu, rows, selected):
            group = None
            for value, label, command in rows:
                item = Gtk.RadioMenuItem.new_with_label_from_widget(group, label)
                if group is None:
                    group = item
                item.set_active(value == selected)
                item.connect("toggled", lambda widget, verb=command:
                             self.command(verb) if widget.get_active() else None)
                menu.append(item)

        def toggle(self, menu, label, key, capability, command):
            if not self.status.get(capability):
                return
            item = Gtk.CheckMenuItem.new_with_label(label)
            item.set_active(bool(self.status.get(key)))
            item.connect("toggled", lambda widget:
                         self.command(command + (":on" if widget.get_active() else ":off")))
            menu.append(item)

        def popup(self, *args):
            self.reload()
            menu = Gtk.Menu()
            self.label(menu, self.status.get("model_name") or "AirPods Pro")
            if self.error:
                self.label(menu, self.error)
            else:
                self.label(menu, "Connected" if self.status.get("connected") else "Disconnected")
                for key, label in (("left", "Left"), ("right", "Right"), ("case", "Case")):
                    self.label(menu, f"{label}: {battery_text(self.status, key)}")
            if self.status.get("connected"):
                menu.append(Gtk.SeparatorMenuItem())
                self.radio(menu, [(n, label, f"noise:{verb}")
                                  for n, label, verb in available_modes(self.status)],
                           self.status.get("noise_mode", -1))
                if self.status.get("supports_adaptive") and self.status.get("noise_mode") == 3:
                    parent = Gtk.MenuItem.new_with_label("Adaptive noise level")
                    submenu = Gtk.Menu()
                    self.radio(submenu, [(n, f"{n}%", f"adaptive:{n}")
                                         for n in (0, 25, 50, 75, 100)],
                               self.status.get("adaptive_noise_level", -1))
                    parent.set_submenu(submenu)
                    menu.append(parent)
                menu.append(Gtk.SeparatorMenuItem())
                self.toggle(menu, "Conversation awareness", "conversational_awareness",
                            "supports_conversational_awareness", "ca")
                self.toggle(menu, "Noise cancellation with one AirPod", "one_bud_anc_mode",
                            "supports_one_bud_anc", "onebud")
                parent = Gtk.MenuItem.new_with_label("Ear detection")
                submenu = Gtk.Menu()
                self.radio(submenu, [(0, "Pause when either AirPod is removed", "ear:one"),
                                     (1, "Pause when both AirPods are removed", "ear:both"),
                                     (2, "Do not pause automatically", "ear:off")],
                           self.status.get("ear_detection_behavior", 0))
                parent.set_submenu(submenu)
                menu.append(parent)
            menu.append(Gtk.SeparatorMenuItem())
            for label, executable in (("Bluetooth settings", "blueman-manager"),
                                      ("Audio settings", "pavucontrol")):
                item = Gtk.MenuItem.new_with_label(label)
                item.connect("activate", lambda widget, program=executable:
                             Gio.Subprocess.new([program], Gio.SubprocessFlags.NONE))
                menu.append(item)
            menu.show_all()
            self.menu = menu
            button = args[1] if len(args) > 1 else 0
            timestamp = args[2] if len(args) > 2 else Gtk.get_current_event_time()
            menu.popup(None, None, Gtk.StatusIcon.position_menu, self.icon, button, timestamp)

    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime:
        raise SystemExit("XDG_RUNTIME_DIR is required; run this in the desktop session")
    lock = open(Path(runtime) / "airpods-xfce.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("AirPods XFCE tray is already running")
    tray = Tray()
    def show_menu():
        tray.popup()
        return True
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, show_menu)
    notification_socket = os.environ.get("NOTIFY_SOCKET")
    if notification_socket:
        if notification_socket.startswith("@"):
            notification_socket = "\0" + notification_socket[1:]
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as notification:
            notification.connect(notification_socket)
            notification.sendall(b"READY=1")
    Gtk.main()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, default=Path(
        os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
        / "librepods/status.json")
    parser.add_argument("--control", type=Path, default=Path.home() / ".local/bin/librepods-ctl")
    parser.add_argument("--print-status", action="store_true")
    args = parser.parse_args()
    if args.print_status:
        status, error = read_status(args.status)
        print(tooltip(status, error))
        return 1 if error else 0
    run_tray(args.status, args.control)
    return 0


if __name__ == "__main__":
    sys.exit(main())
