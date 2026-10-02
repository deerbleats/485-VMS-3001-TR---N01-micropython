"""Host characterization tests; these do not validate MicroPython hardware."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class SoilSensorTests(unittest.TestCase):
    # Literal wire commands deliberately independent of production constants.
    measurements = (
        ('the_soil_ph', '010300030004b409', 10),
        ('the_soil_water', '010300000001840a', 10),
        ('the_soil_temp', '01030001000295cb', 10),
        ('the_soil_conductivity', '010300020003a40b', 10),
        ('the_soil_nitrogen', '010300040005c408', 100),
        ('the_soil_phosphorus', '010300050006d5c9', 100),
        ('the_soil_potassium', '010300060007e409', 100),
        ('the_soil_sainity', '010300070008f5cd', 100),
    )

    def setUp(self):
        self.events = []
        self.response = b'\x01\x03\x02\x12\x34'
        self.failure = None
        owner = self

        class UART:
            def __init__(self, *args):
                owner.events.append(('UART', args))

            def init(self, *args, **kwargs):
                owner.events.append(('init', args, kwargs))
                return 'init-result'

            def write(self, cmd):
                owner.events.append(('write', cmd))
                if owner.failure == 'write':
                    raise OSError('write failed')

            def read(self):
                owner.events.append(('read',))
                if owner.failure == 'read':
                    raise TypeError('read failed')
                return owner.response

        spec = importlib.util.spec_from_file_location(
            'soil_under_test', Path(__file__).resolve().parents[1] / 'soil_sensor.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'machine': types.SimpleNamespace(UART=UART)}):
            spec.loader.exec_module(self.module)
        self.module.time = types.SimpleNamespace(
            sleep=lambda delay: self.events.append(('sleep', delay)))
        self.sensor = self.module.the_soil_sensor(2, 4800)

    def test_uart_configuration_and_public_attributes(self):
        self.assertEqual(self.events, [('UART', (2, 4800)),
                                     ('init', (4800,), dict(bits=8, parity=None, stop=1))])
        self.assertEqual((self.sensor.uart, self.sensor.freq, self.sensor.uartinit),
                         (2, 4800, 'init-result'))

    def test_commands_scaling_and_timing(self):
        for method, command, divisor in self.measurements:
            with self.subTest(method=method):
                self.events.clear()
                value = getattr(self.sensor, method)(test='ignored')
                self.assertEqual(value, 4660 / divisor)
                self.assertIsInstance(value, float)
                self.assertEqual(self.events, [('write', bytes.fromhex(command)),
                                              ('sleep', 0.2), ('read',)])

    def test_existing_unpadded_hex_interpretation(self):
        # Preserve existing 0x01,0x02 -> 0x12, not a protocol correction to 0x0102.
        self.response = b'\x01\x03\x02\x01\x02'
        for method, _, divisor in self.measurements:
            self.assertEqual(getattr(self.sensor, method)(), 18 / divisor)

    def test_no_response_returns_error(self):
        self.response = None
        for method, _, _ in self.measurements:
            self.assertEqual(getattr(self.sensor, method)(), 'error')

    def test_short_response_still_raises_index_error(self):
        for size in range(5):
            self.response = bytes(size)
            for method, _, _ in self.measurements:
                with self.subTest(size=size, method=method), self.assertRaises(IndexError):
                    getattr(self.sensor, method)()

    def test_zero_bytes_return_zero(self):
        self.response = bytes(5)
        for method, _, _ in self.measurements:
            self.assertEqual(getattr(self.sensor, method)(), 0.0)

    def test_transport_errors_propagate(self):
        for failure, error in [('write', OSError), ('read', TypeError)]:
            self.failure = failure
            for method, _, _ in self.measurements:
                with self.subTest(failure=failure, method=method), self.assertRaises(error):
                    getattr(self.sensor, method)()


if __name__ == '__main__':
    unittest.main()
