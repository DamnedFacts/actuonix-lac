import struct
import usb.core

class LAC:
    SET_ACCURACY                = 0x01
    SET_RETRACT_LIMIT           = 0x02
    SET_EXTEND_LIMIT            = 0x03
    SET_MOVEMENT_THRESHOLD      = 0x04
    SET_STALL_TIME              = 0x05
    SET_PWM_THRESHOLD           = 0x06
    SET_DERIVATIVE_THRESHOLD    = 0x07
    SET_MAX_DERIVATIVE          = 0x08
    SET_MIN_DERIVATIVE          = 0x09
    SET_MAX_PWM_VALUE           = 0x0A
    SET_MIN_PWM_VALUE           = 0x0B
    SET_Kp                      = 0x0C
    SET_Kd                      = 0x0D
    SET_AVERAGE_RC              = 0x0E
    SET_AVERAGE_ADC             = 0x0F

    GET_FEEDBACK                = 0x10

    SET_POSITION                = 0x20
    SET_SPEED                   = 0x21

    DISABLE_MANUAL              = 0x30

    RESET                       = 0xFF

    def __init__(self, vendorID=0x4D8, productID=0xFC5F):
        device = usb.core.find(idVendor=vendorID, idProduct=productID)  # Defaults for our LAC; give yours a test
        if device is None:
            raise Exception("No board found, ensure board is connected and powered and matching the IDs provided")

        device.set_configuration()

    # Take data and send it to LAC
    def send_data(self, function, value=0):
        if value < 0 or value > 1023:
            raise Exception("Value is OOB. Must be 2-byte integer in rage [0, 1023]")

        data = struct.pack("BBB", function, value >> 8, value & 0xFF)  # High byte moved down, low byte masked in
        self.dev.write(1, data, 100)  # Magic numbers from the PyUSB tutorial
        time.sleep(.05)  # Just to be sure it's all well and sent
        response = self.dev.read(0x81, 3, 100)  # 3 because there's three bytes to a packet
        return response[2] << 8 + response[1]  # High byte moved left, then tack on the low byte

    # How close to target distance is accepted
    # value/1024 * stroke gives distance, where stroke is max
    # extension length (all values in mm). Round to nearest
    # integer
    def set_accuracy(self, value):
        send_data(self.SET_ACCURACY, value)

    # How far back the actuator can go. A value
    # of 0 hits the mechanical stop, but this
    # is not recommended. The value you want to send
    # is calculated by (distance * 1023)/stroke where
    # distance is intended distance and stroke is max
    # extension length, all values in mm. Round to
    # nearest integer
    def set_retract_limit(self, value):
        send_data(self.SET_RETRACT_LIMIT, value)

    # How far forward the actuator can go. A value
    # of 1023 hits the mechanical stop, but this
    # is not recommended. See above for math
    def set_extend_limit(self, value):
        send_data(self.SET_EXTEND_LIMIT, value)

    # Minimum speed before actuator is considered stalling
    def set_movement_threshold(self, value):
        send_data(self.SET_MOVEMENT_THRESHOLD, value)

    # Timeout (ms) before actuator shuts off after stalling
    def set_stall_time(self, value):
        send_data(self.SET_STALL_TIME, value)

    # When feedback-set>this, set speed to maximum
    def set_pwm_threshold(self, value):
        send_data(self.SET_PWM_THRESHOLD, value)

    # Compared to measured speed to determine
    # PWM increase (prevents stalls). Normally
    # equl to movement threshold
    def set_derivative_threshold(self, value):
        send_data(self.SET_DERIVATIVE_THRESHOLD, value)

    # Maximum value the D term can contribute to control speed
    def set_max_derivative(self, value):
        send_data(self.SET_MAX_DERIVATIVE, value)

    # Minimum value the D term can contribute to control speed
    def set_min_derivative(self, value):
        send_data(self.SET_MIN_DERIVATIVE, value)

    # Speed the actuator runs at when outside the pwm threshold
    # 1023 enables top speed, though actuator may try to move
    # faster to avoid stalling
    def set_max_pwm_value(self, value):
        send_data(self.SET_MAX_PWM_VALUE, value)

    # Minimum PWM value applied by PD
    def set_min_pwm_value(self, value):
        send_data(self.SET_MIN_PWM_VALUE, value)

    # Higher value = faster approach to target, but also more
    # overshoot
    def set_proportional_gain(self, value):
        send_data(self.SET_PROPORTIONAL_GAIN, value)

    # Rate at which differential portion of controller increases
    # while stalling. Not a /real/ differential term, but
    # similar effect. When stalling, derivtive term is
    # incremented to attempt escape
    def set_derivative_gain(self, value):
        send_data(self.SET_DERIVATIVE_GAIN, value)

    # Number of samples used in filtering the RC input signal
    # before the actuator moves. High value = more stability,
    # but lower response time. value * 20ms = delay time.
    # This does NOT affect filter feedback delay; control
    # response to valid input signals is unaffected
    def set_average_rc(self, value=4):
        send_data(self.SET_AVERAGE_RC, value)

    # Number of samples used in filtering the feedback and analog
    # input signals, if active. Similar delay effect to
    # set_average_rc, but this DOES affect control response. PD
    # loop values may need to be retuned when adjusting this
    def set_average_adc(self, value):
        send_data(self.SET_AVERAGE_ADC, value)


    # Causes actuator to send a feedback packet containing its
    # current position. This is read directly from ADC and might
    # not be equal to the set point if yet unreached
    def get_feedback(self):
        send_data(self.GET_FEEDBACK)


    # Set the LAC's position. This shouldn't be shocking, given
    # like ya know the name of the function? Note that this will
    # disable RC, I, and V inputs until reboot. To know what
    # number to send, do (distance * 1023)/stroke where distance
    # is intended position as a distance from the back hardstop,
    # in mm, and stroke is the maximum length of extension, in mm.
    # Be sure to round your result to the nearest integer!
    def set_position(self, value):
        send_data(self.SET_POSITION, value)

    # This command is not documented, but it's probably
    # easy to infer and just guess via trial by fire
    def set_speed(self, value):
        send_data(self.SET_SPEED, value)


    # Saves current config to EEPROM and disables all four
    # potentiometers. On reboot, these values will continue being used
    # instead of the potentiometer values. Analog inputs function
    # as normal either way
    def disable_manual(self):
        send_data(self.DISABLE_MANUAL)


    # Enables manual control potentiometers and resets config
    # to factory default
    def reset(self):
        send_data(self.RESET)
