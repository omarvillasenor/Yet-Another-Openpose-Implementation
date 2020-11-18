"""
Este archivo contiene las funciones necesarias para mover el drone con los resultados de la red neuronal
"""
import datetime
import tellopy
import time
import sys
import os

class ControlDrone:

    def __init__(self, drone):
        self.drone = drone
        self.drone.subscribe(drone.EVENT_FILE_RECEIVED, self.handleFileReceived)
        self.controls = {
            'adelante': 'forward',
            'atras': 'backward',
            'izquierdo': lambda drone, speed: self.move_right(speed),
            'derecho': lambda drone, speed: self.move_left(speed),
            'foto': lambda drone, speed: drone.take_picture(),
        }
        self.speed = 10
        self.date_fmt = '%Y-%m-%d_%H%M%S'

    def start_fligt(self):
        self.drone.takeoff()
    
    def stop_drone(self):
        self.drone.land()
        self.drone.quit()

    def move_right(self, speed):
        self.drone.counter_clockwise(speed)
        self.drone.right(speed)

    def move_left(self, speed):
        self.drone.clockwise(speed)
        self.drone.left(speed)
    
    def move_up(self, speed=-1):
        if speed == -1:
            self.drone.up(self.speed)
        else:
            self.drone.up(speed)

    #Esta función obtiene el texto de la posición y lo convierte en acción, tomándola del diccionario self.controls
    def get_movement(self, position, speed=-1):
        time.sleep(0.01)
        if speed == -1:
            accion = self.controls[position]
            if type(accion) == str:
                getattr(self.drone, accion)(self.speed)
            else:
                accion(self.drone, self.speed)
        elif speed != -1:
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