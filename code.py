from math import *
import numpy as np
import random
import matplotlib.pyplot as plt 

world_size = 100

rfids_xs = [5,25,75,93]
rfids_ys = [20,56,10,85]

class Robot():
      def __init__(self):
            self.x = random.random() * world_size
            self.y = random.random() * world_size
            self.orientation = random.random() * 2 * pi 
            self.forward_noise = 0
            self.sense_noise = 0
            self.rotation_noise = 0

      def set_noise(self, fn, rn, sn):
            self.forward_noise = fn
            self.sense_noise = sn 
            self.rotation_noise = rn
      
      def sense(self):
            measurements = []
            for i in range(len(rfids_xs)):
                  dist = sqrt((self.x - rfids_xs[i])**2 + (self.y - rfids_ys[i])**2)
                  dist += random.gauss(0.0, self.sense_noise)
                  measurements.append(dist)

            return measurements

      def set_state(self, x, y, orientation):
            self.x = x * 1.0
            self.y = y * 1.0
            self.orientation = orientation * 1.0

      def move(self, rotation, forward):
            orientation = self.orientation + rotation + random.gauss(0,sigma = self.rotation_noise)
            orientation %= 2 * pi
            dist = forward + random.gauss(0.0, self.forward_noise)
            x = self.x + dist * cos(orientation)
            y = self.y + dist * sin(orientation)

            rob = Robot()
            rob.set_state(x,y,orientation)
            rob.set_noise(self.forward_noise, self.rotation_noise, self.sense_noise)

            return rob

      def Gaussian(self, mu, sigma, x):
            return  exp(-(x - mu)**2 / (sigma**2 / 2.0)) / sqrt(2.0 * pi * sigma **2)

      def measurement_prob(self,measurements):
            prob = 1
            for i in range(len(rfids_xs)):
                  dist = sqrt((self.x - rfids_xs[i])**2 + (self.y - rfids_ys[i])**2)
                  prob *= self.Gaussian(dist,self.sense_noise,measurements[i])
            return prob

      def __repr__(self):
            return '[x = %.6s, y = %.6s, orient = %.6s]' % (str(self.x), str(self.y), str(self.orientation))
                  

def eval(r, p):
      sum = 0.0
      for i in range(len(p)): 
            dx = (p[i].x - r.x )
            dy = (p[i].y - r.y )
            err = sqrt(dx * dx + dy * dy)
            sum += err
      return sum / float(len(p))


N = 10000
T = 50
plt.ion()

myrobot = Robot()
myrobot.set_state(50,5,0)
dead_robot = Robot()
dead_robot.set_state(50,5,0)
dead_robot.set_noise(0.05,0.05,5)

hxs_true = []
hys_true = []
hxs_p = []
hys_p = []
hxs_dead = []
hys_dead = []

for t in range(T):
      myrobot = myrobot.move(0.15, 5.0)
      dead_robot = dead_robot.move(0.15, 5)

      hxs_true.append(myrobot.x)
      hys_true.append(myrobot.y)

      hxs_dead.append(dead_robot.x)
      hys_dead.append(dead_robot.y)

      Z = myrobot.sense()

      p = []
      w = []
      for i in range(N):
            r = Robot()
            r.set_noise(0.05,0.05,5)
            w.append(r.measurement_prob(Z))
            p.append(r.move(0.15,5.0))

      p3 = []
      index = int(random.random() * N)
      beta = 0.0
      mw = max(w)
      for i in range(N):
            beta += random.random() * 2.0 * mw
            while beta > w[index]: 
                  beta -= w[index]
                  index = (index + 1) % N
            p3.append(p[index])

      p = p3
      print(eval(myrobot, p))

      sumx = 0.0
      sumy = 0.0
      for i in range(N):
            sumx += p[i].x
            sumy += p[i].y
      
      hxs_p.append(sumx/N)
      hys_p.append(sumy/N)


      plt.cla()

      plt.plot([myrobot.x], [myrobot.y], 'bo')
      plt.plot([sumx/N],[sumy/N], 'ro')
      plt.plot(hxs_true,hys_true,'b-', label = 'Actual Path')
      plt.plot(hxs_p,hys_p,'r-', label = 'Partical Filter Path')
      plt.plot(hxs_dead,hys_dead, 'k-', label = 'Dead Reckoning Path')
      plt.plot(rfids_xs,rfids_ys,'ko', label = 'Landmarks')
      plt.legend()
      plt.xlim(0,100)
      plt.ylim(0,100)
      plt.show()
      plt.pause(0.01)