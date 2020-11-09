"""Common enums etc"""
from typing import Iterable, Any
import enum
import time
import struct


class Commands(enum.IntEnum):
    """The commands"""

    SET_ACCURACY = 0x01
    SET_RETRACT_LIMIT = 0x02
    SET_EXTEND_LIMIT = 0x03
    SET_MOVEMENT_THRESHOLD = 0x04
    SET_STALL_TIME = 0x05
    SET_PWM_THRESHOLD = 0x06
    SET_DERIVATIVE_THRESHOLD = 0x07
    SET_MAX_DERIVATIVE = 0x08
    SET_MIN_DERIVATIVE = 0x09
    SET_MAX_PWM_VALUE = 0x0A
    SET_MIN_PWM_VALUE = 0x0B
    SET_PROPORTIONAL_GAIN = 0x0C
    SET_DERIVATIVE_GAIN = 0x0D
    SET_AVERAGE_RC = 0x0E
    SET_AVERAGE_ADC = 0x0F
    GET_FEEDBACK = 0x10
    SET_POSITION = 0x20
    SET_SPEED = 0x21
    DISABLE_MANUAL = 0x30
    RESET = 0xFF

    @classmethod
    def names(cls) -> Iterable[str]:
        """List all command names"""
        return (reg.name for reg in cls)

    @classmethod
    def values(cls) -> Iterable[int]:
        """List all command int values"""
        return (reg.value for reg in cls)


def pyusb_blocking(command: int, value: int, device: Any) -> int:
    """Handle the blocking pyusb send and read"""
    data = struct.pack(
        b"BBB", int(command), value & 0xFF, (value & 0xFF00) >> 8
    )  # Low byte masked in, high byte masked and moved down
    device.write(1, data, 100)  # Magic numbers from the PyUSB tutorial
    time.sleep(0.05)  # Just to be sure it's all well and sent
    response = device.read(0x81, 3, 100)  # 3 because there's three bytes to a packet
    return int((response[2] << 8) + response[1])  # High byte moved left, then tack on the low byte
