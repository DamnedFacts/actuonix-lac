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

    def set_accuracy(self, value):
        if value < 0:
            value = 0
        elif value > 1023:
            value = 1023

        SET_ACCURACY

    def set_retract_limit(self, value):
        # data

    def set_extend_limit(self, value):
        # data
