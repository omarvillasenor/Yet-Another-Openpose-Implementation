import ejecucion_red  as er
import numpy as np
import traceback
import tellopy
import time
import cv2
import sys
import av

model = er.get_model_trained()
drone = tellopy.Tello()

def start_drone():
    try:
        drone.connect()
        drone.wait_for_connection(30.0)

        retry = 3
        container = None
        try:
            container = av.open(drone.get_video_stream())
            print(container)
            return container
        except av.AVError as ave:
            print(ave)
        
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)

def proof(frame):
    er.proof(model, frame)

def stop_drone():
    drone.quit()
    cv2.destroyAllWindows()