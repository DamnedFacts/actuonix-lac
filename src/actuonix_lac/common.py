"""Common enums etc"""
from typing import Iterable
import enum


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
    SET_Kp = 0x0C
    SET_Kd = 0x0D
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
