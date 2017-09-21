import cv2
from ev3control.rpc import Robot
from brain.controllers import euclidian_move_to_brick
from brain.core import State
from brain.core import main_loop

print("Creating robot...")

with Robot(cv2.VideoCapture(1)) as robot:
    robot.map = [(100, 100)]
    print("These are the robot motor positions before planning:", robot.left_track.position, robot.right_track.position)
    # Define the state graph, we can do this better, currently each method
    # returns the next state name
    states = [
        State(
            name="MOVE_BY_MAP",
            act=euclidian_move_to_brick,
            default_args={
                "ltrack_pos": robot.left_track.position,
                "rtrack_pos": robot.right_track.position
            }),
    ]
    print(states[0])
    state_dict = {}
    for state in states:
        state_dict[state.name] = state

    start_state = states[0]

    main_loop(robot, start_state, state_dict, delay=0.03)
