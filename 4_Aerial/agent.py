import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Car, Ball, Input
from RLUtilities.LinearAlgebra import vec3, dot

from RLUtilities.Maneuvers import Aerial

class Agent(BaseAgent):

    def __init__(self, name, team, index):
        self.index = index
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()

        self.skip = False
        self.timer = 0.0
        self.action = None
        self.car_predictions = []
        self.ball_predictions = []

        self.csign = 1;
        self.bsign = 1;

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        self.controls = SimpleControllerState()

        if self.timer == 0.0:

            self.csign = random.choice([-1, 1])

            # this just initializes the car and ball
            # to different starting points each time
            c_position = Vector3(random.uniform(-1000, 1000),
                                 random.uniform(-4500, -4000),
                                 25)

            car_state = CarState(physics=Physics(
                location=c_position,
                velocity=Vector3(0, 1000, 0),
                rotation=Rotator(0, 1.5 * self.csign, 0),
                angular_velocity=Vector3(0, 0, 0)
            ))

            self.bsign = random.choice([-1, 1])

            b_position = Vector3(random.uniform(-3500, -3000) * self.bsign,
                                 random.uniform(-1500,  1500),
                                 random.uniform(  150,   500))

            b_velocity = Vector3(random.uniform( 1000, 1500) * self.bsign,
                                 random.uniform(- 500,  500),
                                 random.uniform( 1000, 1500))

            ball_state = BallState(physics=Physics(
                location=b_position,
                velocity=b_velocity,
                rotation=Rotator(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0)
            ))

            self.set_game_state(GameState(
                ball=ball_state,
                cars={self.index: car_state})
            )

            self.increment_timer = True

        if self.timer < 0.3:
            self.controls.throttle = 1 * self.csign
        else:
            if self.action == None:

                # set empty values for target and t_arrival initially
                self.action = Aerial(self.info.my_car, vec3(0,0,0), 0)

                # predict where the ball will be
                prediction = Ball(self.info.ball)
                self.ball_predictions = [vec3(prediction.pos)]

                for i in range(150):
                    prediction.step(0.016666)
                    prediction.step(0.016666)
                    self.ball_predictions.append(vec3(prediction.pos))

                    # if the ball is in the air
                    if prediction.pos[2] > 100:

                        self.action.target = prediction.pos
                        self.action.t_arrival = prediction.t

                        # check if we can reach it by an aerial
                        if self.action.is_viable():
                            break

            nsteps = 30
            delta_t = self.action.t_arrival - self.info.my_car.time
            prediction = Car(self.info.my_car)
            self.car_predictions = [vec3(prediction.pos)]
            for i in range(nsteps):
                prediction.step(Input(), delta_t / nsteps)
                self.car_predictions.append(vec3(prediction.pos))

            r = 200
            self.renderer.begin_rendering()
            purple = self.renderer.create_color(255, 230, 30, 230)
            white  = self.renderer.create_color(255, 230, 230, 230)

            x = vec3(r,0,0)
            y = vec3(0,r,0)
            z = vec3(0,0,r)
            target = self.action.target
            future = self.action.target - self.action.A

            self.renderer.draw_polyline_3d(self.ball_predictions, purple)
            self.renderer.draw_line_3d(target - x, target + x, purple)
            self.renderer.draw_line_3d(target - y, target + y, purple)
            self.renderer.draw_line_3d(target - z, target + z, purple)

            self.renderer.draw_polyline_3d(self.car_predictions, white)
            self.renderer.draw_line_3d(future - x, future + x, white)
            self.renderer.draw_line_3d(future - y, future + y, white)
            self.renderer.draw_line_3d(future - z, future + z, white)
            self.renderer.end_rendering()

            self.action.step(1.0 / 60.0)
            self.controls = self.action.controls

            if self.action.finished or self.timer > 10.0:
                self.timer = 0.0
                self.action = None
                self.increment_timer = False
                self.predictions = []

        if self.increment_timer:
            self.timer += 1.0 / 60.0

        self.info.my_car.last_input.roll  = self.controls.roll
        self.info.my_car.last_input.pitch = self.controls.pitch
        self.info.my_car.last_input.yaw   = self.controls.yaw
        self.info.my_car.last_input.boost = self.controls.boost

        return self.controls
