import struct
import usb

class LAC:
    SET_ACCURACY                = 0x01
    SET_RETRACT_LIMIT           = 0x02
    SET_EXTEND_LIMIT            = 0x03
    SET_MOVEMENT_THRESHOLD      = 0x04
    SET_STALL_TIME              = 0x05
    SET_PWM_THRESHOLD           = 0x06
    SET_DERIVATIVE_THRESHOLD    = 0x07
    SET_DERIVATIVE_MAXIMUM      = 0x08
    SET_DERIVATIVE_MINIMUM      = 0x09
    SET_PWM_MAXIMUM             = 0x0A
    SET_PWM_MINIMUM             = 0x0B
    SET_PROPORTIONAL_GAIN       = 0x0C
    SET_DERIVATIVE_GAIN         = 0x0D
    SET_AVERAGE_RC              = 0x0E
    SET_AVERAGE_ADC             = 0x0F

    GET_FEEDBACK                = 0x10

    SET_POSITION                = 0x20
    SET_SPEED                   = 0x21

    DISABLE_MANUAL              = 0x30

    RESET                       = 0xFF

    def __init__(self, vendorID, productID):
        device = usb.core.find(vendorID, productID)  # 0x4D8 and 0xFC5F maybe?
        if device is None:
            raise Exception("No board found, ensure board is connected and powered and matching the IDs provided")

        device.set_configuration()

    # Take data and send it to LAC
    def send_data(self, function, value):
        if value < 0 || or value > 1023:
            raise Exception("Value is OOB. Must be 2-byte integer in rage [0, 1023]")

        data = struct.pack("BBB", function, value >> 8, value & 0xFF)
        # TODO: send data itself

    # How close to target distance is accepted
    # value/1024 * stroke gives distance (assuming all mm?)
    def set_accuracy(self, value):
        send_data(self.SET_ACCURACY, value)

    # How far back the actuator can go. A value
    # of 0 hits the mechanical stop, but this
    # is not recommended
    def set_retract_limit(self, value):
        send_data(self.SET_RETRACT_LIMIT, value)

    # How far forward the actuator can go. A value
    # of 1023 hits the mechanical stop, but this
    # is not recommended
    def set_extend_limit(self, value):
        send_data(self.SET_EXTEND_LIMIT, value)

    # Minimum speed before actuator is considered stalling
    def set_movement_threshold(self, value):
        send_data(self.SET_MOVEMENT_THRESHOLD, value)
