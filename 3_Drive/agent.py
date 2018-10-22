import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from RLUtilities.Maneuvers import Drive
from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Car, Ball
from RLUtilities.LinearAlgebra import vec3, dot, clip, norm

from RLUtilities.controller_input import controller

class Agent(BaseAgent):

    def __init__(self, name, team, index):
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()
        self.action = None
        self.counter = 0

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        if self.action == None or self.action.finished or self.counter == 400:
            target_pos = vec3(
                random.uniform(-3000, 3000),
                random.uniform(-2000, 2000),
                25
            )

            target_speed = random.uniform(500, 2000)

            self.action = Drive(self.info.my_car, target_pos, target_speed)

            self.counter = 0

        r = 200
        self.renderer.begin_rendering()
        purple = self.renderer.create_color(255, 230, 30, 230)

        self.renderer.draw_line_3d(self.action.target_pos - r * vec3(1, 0, 0),
                                   self.action.target_pos + r * vec3(1, 0, 0),
                                   purple)

        self.renderer.draw_line_3d(self.action.target_pos - r * vec3(0, 1, 0),
                                   self.action.target_pos + r * vec3(0, 1, 0),
                                   purple)

        self.renderer.draw_line_3d(self.action.target_pos - r * vec3(0, 0, 1),
                                   self.action.target_pos + r * vec3(0, 0, 1),
                                   purple)
        self.renderer.end_rendering()



        if controller.L1:
            self.controls = controller.get_output()
        else:
            self.counter += 1
            if (self.counter % 10) == 0:
                print(f"current speed: {norm(self.info.my_car.vel):4.4f}, \
                        desired speed: {self.action.target_speed:4.4f}")

            self.action.step(0.01666)
            self.controls = self.action.controls



        return self.controls
