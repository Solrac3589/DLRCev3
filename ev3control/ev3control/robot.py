"""
    Interaface to EV3 for higher level functions.
"""
from collections import deque

from .messages import *
from .master import *
from ev3control.objects import GearBox
from ev3control.utils import decode_mqtt


class Robot(object):

    naming_convention = ["gearBox", "gripper", "elevator", "colorSensor", "infraredSensor"]

    def __init__(self, device_constructors, cap):
        """
        Constructor for the class, adds the devices automatically
        :param ports: List of ports for the devices listed in the naming conventions
        """
        self.m = start_master()
        self.devices = []

        self.cap = cap
        self.map = []
        self.position = [0, 0, 0]

        for name in self.naming_convention:
            setattr(self, name, None)

        for device in device_constructors:
            if not device in self.naming_convention:
                raise Exception("Device " + device +
                                " not known, please follow the naming conventions")
            setattr(self, device, device)
            print("Adding ", device, " with constructor ", device_constructors[device])
            self.publish(AddObjectMessage(device, device_constructors[device]))

        # This stores the messages published via MQTT in an attribute of this class (a deque)
        self.m.on_message = self.update_sensor_state
        self._print_messages = deque()
        # This is non-blocking! It starts listening on any topics the client is subscribed to
        self.m.loop_start()

    def update_sensor_state(self, client, userdata, msg):
        """Bad name, this just adds a message to a deque/queue."""
        # TODO: add message type checking
        message = eval(decode_mqtt(msg))
        self._print_messages.append(message)

    def read_proximity_sensor(self):
        self.publish(ShowAttrMessage(self.infraredSensor, "proximity"))
        while True:
            if self._print_messages:
                print("Intensity message")
                proximity_msg = self._print_messages.pop()
                return proximity_msg.value

    def publish(self, msg):
        publish_cmd(self.m, msg)

    def rotate_left(self, vel, time=300):
        """
        Rotates the robot with given velocity
        :param vel: Velocity
        :return:
        """
        self.publish(RunMethodMessage(self.gearBox, "rotate_left", {"vel": vel, "time": time}))

    def rotate_right(self, vel, time=300):
        self.publish(RunMethodMessage(self.gearBox, "rotate_right", {"vel": vel, "time": time}))

    def stop_driving(self):
        self.publish(RunMethodMessage(self.gearBox, "stop", {}))

    def stop_motor(self, name, action="brake"):
        self.publish(RunMethodMessage(name, "stop", {"stop_action": action}))

    def stop_all_motors(self):
        self.stop_driving()
        self.stop_motor("gripper")

    def _move_grip(self, vel, time):
        self.publish(
            RunMethodMessage(self.gripper, "run_timed", {"time_sp": time,
                                                         "speed_sp": vel}))

    def close_grip(self, vel=100, time=3500):
        self._move_grip(-vel, time)

    def open_grip(self, vel=100, time=3500):
        self._move_grip(vel, time)

    def _move_elevator(self, vel, time):
        self.publish(
            RunMethodMessage(self.elevator, "run_timed", {"time_sp": time,
                                                          "speed_sp": -vel}))

    def elevator_up(self):
        self._move_elevator(100, 3000)

    def elevator_down(self):
        self._move_elevator(-100, 3000)

    def move_straight(self, vel=600, time=4000):
        """
        Move straight (forwards/backwards) with given speed, top speed is default
        :param vel: Velocity
        :param time: Time
        :return:
        """
        self.publish(RunMethodMessage(self.gearBox, "drive_straight", {"vel": vel, "time": time}))

    def move(self, vel_left=300, vel_right=300):

        self.publish(RunMethodMessage(self.leftMotor, "run_forever", {"speed_sp": vel_left}))
        self.publish(RunMethodMessage(self.rightMotor, "run_forever", {"speed_sp": vel_right}))

    def move_to_target(self, vec):
        """
        Method for moving to target over a trajectory
        :param vec: Direction vector
        :return:
        """
        pass
