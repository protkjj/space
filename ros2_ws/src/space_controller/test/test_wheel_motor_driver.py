import unittest

from space_controller.wheel_motor_driver import Mode, _clip


class TestWheelMotorDriver(unittest.TestCase):
    def test_clip_limits_symmetric_range(self):
        self.assertEqual(_clip(0.5, 0.3), 0.3)
        self.assertEqual(_clip(-0.5, 0.3), -0.3)
        self.assertEqual(_clip(0.2, 0.3), 0.2)

    def test_clip_disabled_for_non_positive_limit(self):
        self.assertEqual(_clip(0.5, 0.0), 0.5)
        self.assertEqual(_clip(-0.5, -1.0), -0.5)

    def test_mode_values_match_wire_protocol(self):
        self.assertEqual(Mode.ROVER, 0)
        self.assertEqual(Mode.HOLD, 1)
        self.assertEqual(Mode.EMERGENCY, 2)
