from RLUtilities.Simulation import Car, Ball
from RLUtilities.LinearAlgebra import vec3, dot

from RLUtilities.Maneuvers import AerialTurn, Aerial

c = Car()

b = Ball()
b.pos = vec3(0, 0, 1000)
b.vel = vec3(0, 0, 0)
b.omega = vec3(0, 0, 0)
b.t = 0

action = Aerial(c, b.pos, b.t)

b.step(0.0166)
print(action.t_arrival)
print(action.target)
