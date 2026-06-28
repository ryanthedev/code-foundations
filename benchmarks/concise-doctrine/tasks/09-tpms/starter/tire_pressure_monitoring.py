import random


class Sensor(object):
    # The pressure reading is simulated. Random by design — the point of the
    # exercise is that Alarm hardcodes this dependency and is therefore hard to
    # unit-test without triggering real (random) readings.
    _OFFSET = 16

    def pop_next_pressure_psi_value(self):
        pressure_telemetry_value = self.sample_pressure()
        return Sensor._OFFSET + pressure_telemetry_value

    @staticmethod
    def sample_pressure():
        return 6 * random.random() * random.random()


class Alarm(object):

    def __init__(self):
        self._low_pressure_threshold = 17
        self._high_pressure_threshold = 21
        self._sensor = Sensor()
        self._is_alarm_on = False

    def check(self):
        psi_pressure_value = self._sensor.pop_next_pressure_psi_value()
        if psi_pressure_value < self._low_pressure_threshold \
                or self._high_pressure_threshold < psi_pressure_value:
            self._is_alarm_on = True

    @property
    def is_alarm_on(self):
        return self._is_alarm_on
