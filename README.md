# Soil sensor MicroPython driver

`soil_sensor.py` uses `machine.UART`. Copy it to the MicroPython board and keep
the UART number and baud rate appropriate for your wiring and sensor.

```python
from soil_sensor import the_soil_sensor

sensor = the_soil_sensor(2, 4800)
value = sensor.the_soil_ph()
```

All eight existing methods and command bytes are retained, including the
historical spelling `the_soil_sainity`. Each measurement writes one command,
waits 0.2 seconds, then reads once. Missing responses return `"error"`; short
responses still raise `IndexError`, and transport exceptions still propagate.

The existing conversion concatenates **unpadded** hexadecimal bytes. For
example, bytes `01 02` are interpreted as `0x12`, not `0x0102`. This refactor
preserves that behavior and existing scale factors; it does not establish that
they agree with the device protocol. CRC validation, signed temperatures,
fragmented UART reads, and any protocol corrections require separate testing
against the device documentation and hardware.

Run host characterization tests from this directory:

```sh
python3 -B -m unittest discover -s tests -v
```

These tests substitute a fake UART and clock to check byte sequences, scaling,
call ordering, and error behavior. They do not validate MicroPython firmware,
physical UART timing, RS-485 direction control, or sensor accuracy.
