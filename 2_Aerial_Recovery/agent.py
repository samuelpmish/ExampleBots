import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Car, Ball
from RLUtilities.LinearAlgebra import vec3, dot, clamp

from RLUtilities.controller_input import controller

from RLUtilities.Maneuvers import AerialTurn


class Agent(BaseAgent):

    def __init__(self, name, team, index):
        self.index = index
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()

        self.timer = 0.0
        self.action = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        self.controls = SimpleControllerState()

        if self.timer < 0.05:

            position = Vector3(random.uniform(-4000, 4000),
                               random.uniform(-3000, 3000),
                               random.uniform(  500, 2000))

            velocity = Vector3(random.uniform(-1500, 1500),
                               random.uniform(-1500, 1500),
                               random.uniform(-1000, -500))

            rotation = Rotator(random.uniform(-1.5, 1.5),
                               random.uniform(-1.5, 1.5),
                               random.uniform(-1.5, 1.5))

            angular_velocity = Vector3(random.uniform(-3.0, 3.0),
                                       random.uniform(-3.0, 3.0),
                                       random.uniform(-3.0, 3.0))

            car_state = CarState(physics=Physics(
                location=position,
                velocity=velocity,
                rotation=rotation,
                angular_velocity=angular_velocity
            ))

            self.set_game_state(GameState(cars={self.index: car_state}))

        if self.timer > 0.10:

            if self.action == None:
                self.action = AerialTurn(self.info.my_car)

            self.renderer.begin_rendering()
            red = self.renderer.create_color(255, 255, 30, 30)
            self.renderer.draw_polyline_3d(self.action.trajectory, red)
            self.renderer.end_rendering()


            self.action.step(1.0 / 60.0)
            self.controls = self.action.controls

            self.timer += 1.0 / 60.0
            if self.action.finished or self.timer > 5.0:
                print("target:\n", self.action.target)
                print("theta:\n", self.action.car.theta)
                print()
                self.timer = 0.0
                self.action = None

        self.timer += 1.0 / 60.0
        return self.controls
