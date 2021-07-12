import usb.core
from typing import Tuple
from struct import pack
from time import sleep

class LAC:

	# All of these constants are used to command the LAC; all were copied directly from the configuration datasheet

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

	def __init__(self, stroke: float, vendorID: int = 0x4D8, productID: int = 0xFC5F):
		"""
		LAC class initializer. stroke is the maximum length of your specific actuator in millimeters, for example 30
		would be used as the stroke for a 30mm LAC.

		The default vendorID and productID came from our own actuator; be sure to test for your own values! Good
		operating systems have the `lsusb` command, which contains an ID field in the form VID:PID.

		Winblows users can (allegedly) go to "Device manager", find the LAC, right click, choose "Properties", then
		"Details", then "Hardware IDs", and find an entry in the form `HID\VID_XXXX&PID_YYYY` which correspond to the
		vendor (XXXX) and product (YYYY) IDs. That's according to this:
		https://superuser.com/a/1106248
		"""
		if stroke < 0 or vendorID < 0 or productID < 0:
			raise ValueError("No parameters can be negative values")

		self.device = usb.core.find(idVendor = vendorID, idProduct = productID)
		if self.device is None:
			raise Exception("No board found, ensure board is connected and powered with matching ID")

		self.device.set_configuration()
		self.stroke = stroke

	def send_data(self, function: int, value: int = 0) -> Tuple[int, int]:
		"""
		Send data to the LAC. The return value is an echo of the sent packet, unless otherwise stated.

		The first item in the response is (probably?) the current control mode (like `function`). The second item is the
		two-byte data as an integer (like `value`). On account of endianness, the bytes are manually swapped
		"""
		if not 0 <= value <= 1023:
			raise ValueError("Value is out of bounds. Must be 2-byte integer in range [0, 1023]")

		# Bytes are separated: low byte first, then high byte. Former is masked, latter is shifted into position
		data = pack(b"BBB", function, value & 0xFF, value >> 8)

		# These magic numbers were gleefully stolen from the PyUSB tutorial
		# TODO: is there a better way to ensure data is fully sent than sleeping for 50ms?
		self.device.write(1, data, 100)
		sleep(.05)

		# Three bytes per packet
		# I assume the 0x81 and 100 here also came from the PyUSB tutorial, but I never actually wrote that down...
		response = self.device.read(0x81, 3, 100)

		# Just as before, the bytes are separated, so here they're put back together as one integer
		return response[0], (response[2] << 8) + response[1]

	def set_accuracy(self, accuracy: float = .117) -> Tuple[int, int]:
		"""
		Describes how close the LAC needs to get to its target position before stopping, in millimeters. The default
		value gives the arm ±0.117mm of lenience to its requested destination. According to the datasheet, with too low
		a value, the arm could move back and forth around the desired position endlessly.

		Because of the natures of floats and the LAC's integer-based interface, there is ironically some inaccuracy
		between the parameter and the result
		"""
		return self.send_data(self.SET_ACCURACY, int(round(accuracy/self.stroke * 1024)))

	def set_retract_limit(self, length: float) -> Tuple[int, int]:
		"""
		Retract limit gives the actuator a minimum length, in millimeters.

		A value of zero would contact the mechanical stop, but according to the datasheet, "it is recommended to offset
		[this value] to ensure the actuator is never driven into the physical end stops. This increases cycle life
		considerably." In English, don't do that
		"""
		return self.send_data(self.SET_RETRACT_LIMIT, int(round(length/self.stroke * 1023)))

	def set_extend_limit(self, length: float) -> Tuple[int, int]:
		"""
		Extend limit gives the actuator a maximum length, in millimeters.

		A value equal to `stroke` from the constructor would contact the mechanical stop, but according to the
		datasheet, "it is recommended to offset [this value] to ensure the actuator is never driven to the physical end
		stops. This increases cycle life considerably." In English, don't do that
		"""
		return self.send_data(self.SET_EXTEND_LIMIT, int(round(length/self.stroke * 1023)))

	def set_movement_threshold(self, value: int) -> Tuple[int, int]:
		"""
		The datasheet describes this value as "the minimum actuator speed that is considered a stall", and warns that
		"the stall timer begins counting" when the movement speed of the actuator falls below the given value. See also
		`set_stall_time`.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_MOVEMENT_THRESHOLD, value)

	def set_stall_time(self, time: int) -> Tuple[int, int]:
		"""
		The amount of time, in milliseconds, the actuator will wait before stopping the motor after a stall is detected
		(see also `set_movement_threshold`). According to the datasheet, "the actuator will exit this state when the
		input signal tells the actuator to move in the opposite direction". If the stall is resolved in time, the stall
		timer will reset.

		Whether "this state" refers to the pre- or post-stop stall is unclear to me.

		The value is almost certainly a 2-byte integer, but that is my extrapolation from technical details -- it's not
		officially stated
		"""
		return self.send_data(self.SET_STALL_TIME, time)

	def set_pwm_threshold(self, value: int) -> Tuple[int, int]:
		"""
		Described as setting "the distance around the set point where the PWM PD controller is active", whatever that
		means (particularly the "set point". Perhaps that relates to `set_position`?).

		If the difference between the feedback (see `get_feedback`) and set point is greater than the given value, the
		actuator's speed is maxed.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_PWM_THRESHOLD, value)

	def set_derivative_threshold(self, value: int) -> Tuple[int, int]:
		"""
		The derivative threshold is used to determine when PWM should be increased to exit a stall, based on the current
		speed. The datasheet claims it's normally set equal to the movement threshold (see `set_movement_threshold`).

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_DERIVATIVE_THRESHOLD, value)

	def set_max_derivative(self, value: int) -> Tuple[int, int]:
		"""
		Maximum value that the derivative term contributes to controlling speed. Probably involced in PD control? See
		also `set_min_derivative`.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_MAX_DERIVATIVE, value)

	def set_min_derivative(self, value: int) -> Tuple[int, int]:
		"""
		Minimum value that the derivative term contributes to controlling speed. Probably involced in PD control? See
		also `set_max_derivative`.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_MIN_DERIVATIVE, value)

	def set_max_pwm_value(self, value: int) -> Tuple[int, int]:
		"""
		Sets the value "manually controlled by the speed potentiometer". When outside the PWM threshold (see
		`set_pwm_threshold`), this is the actuator's speed. 1023 represents maximum speed. Regardless of the value set,
		the actually may actually exceed it while attempting to exit a stall. Whether 1023 can be exceeded is unclear.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_MAX_PWM_VALUE, value)

	def set_min_pwm_value(self, value: int) -> Tuple[int, int]:
		"""
		Sets the value that the datasheet simply calls "the minimum PWM value that can be applied by the PD control".

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_MIN_PWM_VALUE, value)

	def set_proportional_gain(self, value: int) -> Tuple[int, int]:
		"""
		This sets the Kp value, the proportional control term. Higher values result in a faster approach to the target
		position, but that can also make overshoot more likely. If that happens, reducing Kp will reduce overshoot.

		No units, equations, range, or other helpful info are provided
		"""
		return self.send_data(self.SET_PROPORTIONAL_GAIN, value)

	def set_derivative_gain(self, value: int) -> Tuple[int, int]:
		"""
		Sets the rate at which the differential control term increases when stalling. This is not an actual differential
		term, but it has a similar effect. If a stall is detected, the derivative term increments.

		No units, equations, range, or other helpful info are provided. I presume the increment is equal to this value,
		but that is entirely unclear from the datasheet
		"""
		return self.send_data(self.SET_DERIVATIVE_GAIN, value)

	# TODO: does this value affect the `sleep(.05)` in the contructor?
	def set_average_rc(self, samples: int = 4) -> Tuple[int, int]:
		"""
		Sets the value which determines how many samples are used when filtering the RC input before the actuator is
		moved. Increasing this value can improve stability, but will affect response time. One sample costs 20ms of
		delay. Feedback filter delay and control response to a valid input signal are unaffected
		"""
		return self.send_data(self.SET_AVERAGE_RC, samples)

	def set_average_adc(self, samples: int) -> Tuple[int, int]:
		"""
		Sets the value which detemines the number of samples used in filtering the feedback and analog input signals, if
		active. Increasing this value increases the feedback filter delay, where one sample costs 20ms of delay. Unlike
		`set_average_rc`, this delay affects actuator control response. This delay allows the actuator to move before
		using PD to update the speed, so other values may need retuning after changing this
		"""
		return self.send_data(self.SET_AVERAGE_ADC, samples)

	def get_feedback(self) -> int:
		"""
		Per the datasheet, "This command causes the actuator to respond with a feedback packet containing the current
		actuator position. This is read directly from the ADC and may not be equal to the set point if the actuator has
		not yet reached it."

		Because the control mode seems irrelevant, it is left out of this function's return value. How the return value
		relates to the millimeter length of the arm isn't described, but I suspect it's the inverse equation of the
		`set_position` function
		"""
		return self.send_data(self.GET_FEEDBACK)[1]

	def set_position(self, distance: int) -> Tuple[int, int]:
		"""
		Tells the actuator what distance to extend to, in millimeters from the base.

		Using this command disables RC, I, and V inputs until reboot, but enables USB control.

		This is the only command with a response that isn't a simple echo. Instead, the second value of the tuple
		represents the arm's current position
		"""
		return self.send_data(self.SET_POSITION, int(round(distance/self.stroke * 1023)))

	def set_speed(self, value: int) -> Tuple[int, int]:
		"""
		This command is not documented in the datasheet at all.

		There are four potentiometers on the board, and only one does not have a matching documented USB control
		function. For that reason, I suspect this function mirrors the speed potentiometer in the same way that the
		`set_accuracy` function mirrors the accuracy potentiometer
		"""
		return self.send_data(self.SET_SPEED, value)

	def disable_manual(self, value: int = 0):
		"""
		Save the current configration to EEPROM and disable all four potentiometers.

		On reboot, these values will be used instead of the potentiometer values. Analog inputs are not affected. What
		"these values" refers to is unclear, though I suspect it is the accuracy, retract limit, extend limit, and speed
		functions' values.

		Whether the `value` parameter has any effect is also unclear. For that reason, I have it defaulting to zero
		"""
		self.send_data(self.DISABLE_MANUAL)

	def reset(self, value: int = 0):
		"""
		Enable the manual control potentiometers and reset the configuration settings.

		I doubt the `value` parameter has any effect, so I have defaulted it to zero
		"""
		self.send_data(self.RESET)
