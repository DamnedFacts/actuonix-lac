"""The old blocking implementation"""
from typing import Union
import struct
import time

import usb.core

from .common import Commands


class LAC:  # pylint: disable=R0904
    """Communicate with the LAC board (blocking version)"""

    def __init__(self, vendorID=0x4D8, productID=0xFC5F):
        self.device = usb.core.find(idVendor=vendorID, idProduct=productID)  # Defaults for our LAC; give yours a test
        if self.device is None:
            raise Exception("No board found, ensure board is connected and powered and matching the IDs provided")

        self.device.set_configuration()

    def send_data(self, command: Union[int, Commands], value: int = 0) -> int:
        """Take data and send it to LAC"""
        if value < 0 or value > 1023:
            raise ValueError("Value is OOB. Must be 2-byte integer in rage [0, 1023], was {}".format(value))
        if int(command) not in Commands.values():
            raise ValueError("command is OOB, see the Commands enum for valid values. was {}".format(command))

        data = struct.pack(
            b"BBB", int(command), value & 0xFF, (value & 0xFF00) >> 8
        )  # Low byte masked in, high byte masked and moved down
        self.device.write(1, data, 100)  # Magic numbers from the PyUSB tutorial
        time.sleep(0.05)  # Just to be sure it's all well and sent
        response = self.device.read(0x81, 3, 100)  # 3 because there's three bytes to a packet
        return (response[2] << 8) + response[1]  # High byte moved left, then tack on the low byte

    def set_accuracy(self, value: int = 4) -> None:
        """How close to target distance is accepted value/1024 * stroke gives distance, where stroke is max
        extension length (all values in mm). Round to nearest integer"""
        self.send_data(Commands.SET_ACCURACY, value)

    def set_retract_limit(self, value: int) -> None:
        """How far back the actuator can go. A value of 0 hits the mechanical stop, but this is not recommended.
        The value you want to send is calculated by (distance * 1023)/stroke where distance is intended distance
        and stroke is max extension length, all values in mm. Round to nearest integer"""
        self.send_data(Commands.SET_RETRACT_LIMIT, value)

    def set_extend_limit(self, value: int) -> None:
        """How far forward the actuator can go. A value of 1023 hits the mechanical stop,
        but this is not recommended. See above for math"""
        self.send_data(Commands.SET_EXTEND_LIMIT, value)

    def set_movement_threshold(self, value: int) -> None:
        """Minimum speed before actuator is considered stalling"""
        self.send_data(Commands.SET_MOVEMENT_THRESHOLD, value)

    def set_stall_time(self, value: int) -> None:
        """Timeout (ms) before actuator shuts off after stalling"""
        self.send_data(Commands.SET_STALL_TIME, value)

    def set_pwm_threshold(self, value: int) -> None:
        """When feedback-set>this, set speed to maximum"""
        self.send_data(Commands.SET_PWM_THRESHOLD, value)

    def set_derivative_threshold(self, value: int) -> None:
        """Compared to measured speed to determine PWM increase (prevents stalls).
        Normally equal to movement threshold"""
        self.send_data(Commands.SET_DERIVATIVE_THRESHOLD, value)

    def set_max_derivative(self, value: int) -> None:
        """Maximum value the D term can contribute to control speed"""
        self.send_data(Commands.SET_MAX_DERIVATIVE, value)

    def set_min_derivative(self, value: int) -> None:
        """Minimum value the D term can contribute to control speed"""
        self.send_data(Commands.SET_MIN_DERIVATIVE, value)

    def set_max_pwm_value(self, value: int) -> None:
        """Speed the actuator runs at when outside the pwm threshold 1023 enables top speed,
        though actuator may try to move faster to avoid stalling"""
        self.send_data(Commands.SET_MAX_PWM_VALUE, value)

    def set_min_pwm_value(self, value: int) -> None:
        """Minimum PWM value applied by PD"""
        self.send_data(Commands.SET_MIN_PWM_VALUE, value)

    def set_proportional_gain(self, value: int) -> None:
        """Higher value = faster approach to target, but also more overshoot"""
        self.send_data(Commands.SET_PROPORTIONAL_GAIN, value)

    def set_derivative_gain(self, value: int) -> None:
        """Rate at which differential portion of controller increases while stalling. Not a /real/ differential term,
        but similar effect. When stalling, derivtive term is incremented to attempt escape"""
        self.send_data(Commands.SET_DERIVATIVE_GAIN, value)

    def set_average_rc(self, value: int = 4) -> None:
        """Number of samples used in filtering the RC input signal before the actuator moves.
        High value = more stability, but lower response time. value * 20ms = delay time. This does NOT affect filter
        feedback delay; control response to valid input signals is unaffected"""
        self.send_data(Commands.SET_AVERAGE_RC, value)

    def set_average_adc(self, value: int) -> None:
        """Number of samples used in filtering the feedback and analog input signals, if active.
        Similar delay effect to set_average_rc, but this DOES affect control response.
        PD loop values may need to be retuned when adjusting this"""
        self.send_data(Commands.SET_AVERAGE_ADC, value)

    def get_feedback(self) -> int:
        """Causes actuator to send a feedback packet containing its current position.
        This is read directly from ADC and might not be equal to the set point if yet unreached"""
        return self.send_data(Commands.GET_FEEDBACK)

    def set_position(self, value: int) -> None:
        """Set the LAC's position. This shouldn't be shocking, given like ya know the name of the function?
        Note that this will disable RC, I, and V inputs until reboot.
        To know what number to send, do (distance * 1023)/stroke where distance is intended position as a distance
        from the back hardstop, in mm, and stroke is the maximum length of extension, in mm.
        Be sure to round your result to the nearest integer!"""
        self.send_data(Commands.SET_POSITION, value)

    def set_speed(self, value) -> None:
        """This command is not documented, but it's probably easy to infer and just guess via trial by fire"""
        self.send_data(Commands.SET_SPEED, value)

    def disable_manual(self) -> None:
        """Saves current config to EEPROM and disables all four potentiometers.
        On reboot, these values will continue being used instead of the potentiometer values.
        Analog inputs function as normal either way"""
        self.send_data(Commands.DISABLE_MANUAL)

    def reset(self) -> None:
        """Enables manual control potentiometers and resets config to factory default"""
        self.send_data(Commands.RESET)
