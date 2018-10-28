from math import sin, cos
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Car, Ball, Input
from RLUtilities.LinearAlgebra import vec3, dot, norm

from RLUtilities.Maneuvers import Wavedash

class State:
    RESET = 0
    WAIT = 1
    INITIALIZE = 2
    RUNNING = 3

class Agent(BaseAgent):

    def __init__(self, name, team, index):
        self.index = index
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()

        self.timer = 0.0
        self.timeout = 4.0

        self.action = None
        self.state = State.RESET

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        self.controls = SimpleControllerState()

        next_state = self.state

        if self.state == State.RESET:

            self.timer = 0.0
            self.action = None

            # put the car in the middle of the field
            car_state = CarState(physics=Physics(
                location=Vector3(0, 0, 20),
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0)
            ))

            theta = random.uniform(0, 6.28)
            pos = Vector3(sin(theta) * 3000.0, cos(theta) * 3000.0, 100.0)

            # put the ball somewhere out of the way
            ball_state = BallState(physics=Physics(
                location=pos,
                velocity=Vector3(0, 0, 0),
                rotation=Rotator(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0)
            ))

            self.set_game_state(GameState(
                ball=ball_state,
                cars={self.index: car_state})
            )

            next_state = State.WAIT

        if self.state == State.WAIT:

            if self.timer > 0.2:
                next_state = State.INITIALIZE

        if self.state == State.INITIALIZE:

            # in this demonstration, we choose to dodge toward the ball
            c = self.info.my_car
            target = self.info.ball.pos
            self.action = Wavedash(c, target)

            self.controls.handbrake = 1

            next_state = State.RUNNING

        if self.state == State.RUNNING:

            self.action.step(0.01666)
            self.controls = self.action.controls

            if self.timer > self.timeout:
                next_state = State.RESET
            elif self.action.finished:
                next_state = State.INITIALIZE

        self.timer += 0.01666
        self.state = next_state

        self.info.my_car.last_input.roll  = self.controls.roll
        self.info.my_car.last_input.pitch = self.controls.pitch
        self.info.my_car.last_input.yaw   = self.controls.yaw

        return self.controls
