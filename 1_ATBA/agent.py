import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Car, Ball
from RLUtilities.LinearAlgebra import vec3, dot, clip

from RLUtilities.controller_input import controller

class Agent(BaseAgent):

    def __init__(self, name, team, index):
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        ball = self.info.ball
        car = self.info.my_car

        # the vector from the car to the ball in local coordinates:
        # delta_local[0]: how far in front of my car
        # delta_local[1]: how far to the left of my car
        # delta_local[2]: how far above my car
        delta_local = dot(ball.pos - car.pos, car.theta)

        # the angle between the direction the car is facing
        # and the in-plane local position of the ball
        phi = math.atan2(delta_local[1], delta_local[0])

        # a simple steering controller that is proportional to phi
        self.controls.steer = clip(2.5 * phi, -1.0, 1.0)

        # just set the throttle to 1 so the car is always moving forward
        self.controls.throttle = 1.0

        # draw some of the lines showing the angle phi (purple)
        # and the local coordinates:
        # delta_local[0]: red
        # delta_local[1]: green
        # delta_local[2]: blue
        self.renderer.begin_rendering()
        red = self.renderer.create_color(255, 255, 30, 30)
        green = self.renderer.create_color(255, 30, 255, 30)
        blue = self.renderer.create_color(255, 30, 30, 255)
        white = self.renderer.create_color(255, 230, 230, 230)
        gray = self.renderer.create_color(255, 130, 130, 130)
        purple = self.renderer.create_color(255, 230, 30, 230)

        f = car.forward()
        l = car.left()
        u = car.up()

        self.renderer.draw_line_3d(car.pos, car.pos + delta_local[0] * f, red)
        self.renderer.draw_line_3d(car.pos, car.pos + delta_local[1] * l, green)
        self.renderer.draw_line_3d(car.pos, car.pos + delta_local[2] * u, blue)
        self.renderer.draw_line_3d(car.pos, ball.pos, white)
        self.renderer.draw_line_3d(ball.pos, ball.pos - delta_local[2] * u, gray)
        self.renderer.draw_line_3d(car.pos, ball.pos - delta_local[2] * u, gray)

        radius = 200
        num_segments = 30
        angle = []
        for i in range(num_segments):
            c = math.cos(phi * float(i) / (num_segments - 1))
            s = math.sin(phi * float(i) / (num_segments - 1))
            angle.append(car.pos + radius * (c * f + s * l))

        self.renderer.draw_polyline_3d(angle, purple)
        self.renderer.end_rendering()

        if controller.L1:
            self.controls = controller.get_output()

        return self.controls
