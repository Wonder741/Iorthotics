import urx
import math
robot=urx.robot("192.168.0.10")
print("hi")
pose=math.radians(45), math.radians(-20), math.radians(90), 0, 0, 0

robot.movex("pose", pose, acc=0.5, vel=0.2)

robot.close()