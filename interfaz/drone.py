import interfaz.ejecucion_red  as er
import numpy as np
import traceback
import tellopy
import time
import cv2
import sys
import av

drone = tellopy.Tello()

def start_drone():
    try:
        drone.connect()
        drone.wait_for_connection(30.0)

        container = None
        try:
            container = av.open(drone.get_video_stream())
            return drone, container
        except av.AVError as ave:
            print(ave)
            return None, None
        
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
        return None, None