#LD2410 test
import serial


class Target:
    def __init__(self, distance, energy):
        self._distance = distance
        self._energy = energy


class MovingTarget(Target):
    def __init__(self, distance, energy):
        Target.__init__(self, distance, energy)
    
    def __repr__(self) -> str:
        return f"Moving Target at {self._distance}cm with energy {self._energy}"

class StationnaryTarget(Target):
    def __init__(self, distance, energy):
        Target.__init__(self, distance, energy)
    
    def __repr__(self) -> str:
        return f"Stationnary Target at {self._distance}cm with energy {self._energy}"


class TargetFactory:


    def get(self, buffer):
        targets = []
        target_type_ = buffer[8]
        stationary_target_distance_ = buffer[9] + (buffer[10] << 8)
        stationary_target_energy_ = buffer[14]
        moving_target_energy_ = buffer[11]
        moving_target_distance_ = buffer[15] + (buffer[16] << 8)
        if target_type_ == 0x01:
            targets.append(StationnaryTarget(stationary_target_distance_, stationary_target_energy_))
        elif target_type_ == 0x02:
            targets.append(MovingTarget(moving_target_distance_, moving_target_energy_))
        elif target_type_ == 0x03:
            targets.append(StationnaryTarget(stationary_target_distance_, stationary_target_energy_))
            targets.append(MovingTarget(moving_target_distance_, moving_target_energy_))
        return targets


class LD2410:

    def __init__(self, port):
        self._port = serial.Serial(port=port,baudrate=256000)
        self._buffer = bytearray()
        self._factory = TargetFactory()

    def read(self):
        if self._port.in_waiting > 0:
            new_data = self._port.read(self._port.in_waiting)
            self._buffer += new_data
        while len(self._buffer) > 0 and self._buffer[0] != 0xF4:
            self._buffer = self._buffer[1:]
        if len(self._buffer) > 0 and self._buffer[0] == 0xF4:
            if len(self._buffer) >= 23:
                targets = []
                start_pattern = bytearray([0xF4, 0xF3, 0xF2, 0xF1, 13, 0x00, 0x02, 0xAA])
                end_pattern = bytearray([0x55, 0x00, 0xF8, 0xF7, 0xF6, 0xF5])
                if start_pattern == self._buffer[0:len(start_pattern)] and end_pattern == self._buffer[17:]:
                    targets = self._factory.get(self._buffer)
                self._buffer = self._buffer[23:]
                return targets
        return None

radar = LD2410('/dev/ttyUSB0')
while True:
    targets = radar.read()
    if targets:
        print(targets)