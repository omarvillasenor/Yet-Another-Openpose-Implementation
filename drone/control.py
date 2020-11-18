import datetime
import tellopy
import time
import sys
import os
# import pygame
# import pygame.display
# import pygame.key
# import pygame.locals
# import pygame.font
# from subprocess import Popen, PIPE
# from tellopy import logger

# log = tellopy.logger.Logger('TelloUI')

# prev_flight_data = None
# video_player = None
# video_recorder = None
# font = None
# wid = None
# date_fmt = '%Y-%m-%d_%H%M%S'

class ControlDrone:

    def __init__(self, drone):
        self.drone = drone
        self.drone.subscribe(drone.EVENT_FILE_RECEIVED, self.handleFileReceived)
        self.controls = {
            'adelante': 'forward',
            'atras': 'backward',
            'izquierdo': lambda drone, speed: self.move_right(),
            'derecho': lambda drone, speed: self.move_left(),
            'foto': lambda drone, speed: drone.take_picture(),
        }
        self.speed = 10
        self.date_fmt = '%Y-%m-%d_%H%M%S'

    def start_fligt(self):
        self.drone.takeoff()
    
    def stop_drone(self):
        drone.land()
        drone.quit()

    def move_right(self):
        self.drone.counter_clockwise(self.speed)
        self.drone.right(self.speed)

    def move_left(self):
        self.drone.clockwise(self.speed)
        self.drone.left(self.speed)
    
    def move_up(self):
        self.drone.up(self.speed)

    def get_movement(self, position, speed=-1):
        speed = self.speed if speed == -1 else speed
        accion = self.controls[position]
        if type(accion) == str:
            getattr(self.drone, accion)(speed)
        else:
            accion(self.drone, speed)

    def handleFileReceived(self, event, sender, data):
        path = 'tello-%s.jpeg' % (
            datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
        with open(path, 'wb') as fd:
            fd.write(data)