import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from airpods_xfce import available_modes, battery_text, read_status, tooltip


class StatusTest(unittest.TestCase):
    def test_new_daemon_has_no_battery_objects(self):
        status = {"schema_version": 1, "connected": False}
        self.assertEqual(battery_text(status, "left"), "Unknown")
        self.assertIn("Disconnected", tooltip(status))

    def test_pro3_capabilities_exclude_off(self):
        modes = available_modes({"supports_noise_control": True,
                                 "supports_noise_off": False,
                                 "supports_adaptive": True})
        self.assertEqual([mode[2] for mode in modes], ["anc", "transparency", "adaptive"])

    def test_plain_airpods_have_no_listening_controls(self):
        self.assertEqual(available_modes({"supports_noise_control": False}), [])

    def test_disconnected_case_can_still_report_battery(self):
        status = {"connected": False, "case": {"available": True, "level": 71,
                                              "charging": True}}
        self.assertEqual(battery_text(status, "case"), "71% (charging)")

    def test_unavailable_or_invalid_battery_is_unknown(self):
        for battery in ({"available": False, "level": 80},
                        {"available": True, "level": -1},
                        {"available": True, "level": "bad"}):
            self.assertEqual(battery_text({"left": battery}, "left"), "Unknown")

    def test_schema_errors_disable_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            self.assertIn("not running", read_status(path)[1])
            for value in ([], {}, {"schema_version": True}, {"schema_version": 2}):
                path.write_text(json.dumps(value))
                status, error = read_status(path)
                self.assertEqual(status, {})
                self.assertTrue(error)
            path.write_text('{"schema_version":1,"connected":false}')
            self.assertEqual(read_status(path)[1], "")


if __name__ == "__main__":
    unittest.main()
