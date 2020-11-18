from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import interfaz.drone as dr
import numpy as np
import traceback
import tellopy
import time
import cv2
import sys
import av

# CNN
from applications.model_wrapper import ModelWrapper
import configs.draw_config as draw_config
import visualizations as vis

from drone.control import ControlDrone

container = None
drone = None
model_path = "trained_models/model11_test-15Sun1219-2101"
model_wrapper = ModelWrapper(model_path)


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    
    def process_frame(self, img):
        global model_wrapper
        position, human = model_wrapper.process_image(img)
        if position is not None:
            drone.get_movement(position)
            drone.get_movement(position, 0)
        if human != True:
            if human == "up_low":
                drone.up(10)
                drone.up(0)
            elif human == "up_high":
                drone.up(0) 

    def run(self):
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                rgbImage = np.array(frame.to_image())
                self.process_frame(rgbImage)
                
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
               
                


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('interfaz/interfaz.ui', self)
        self.conexion_establecida = False
        self.StartButton.clicked.connect(self.start_drone)
        self.PictureButton.clicked.connect(self.take_picture)
        self.close_button.clicked.connect(self.close_conection)
        self.StopButton.clicked.connect(self.land)
        self.PalmButton.clicked.connect(self.palm_land)
        self.FlightButton.clicked.connect(self.flight)
        self.UpButton.clicked.connect(self.up)
        self.DownButton.clicked.connect(self.down)
        self.CameraLabel.hide()
        self.show()
        self.drone = None

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.CameraLabel.setPixmap(QPixmap.fromImage(image))

    def start_drone(self):
        global container, drone
        self.drone, container = dr.start_drone()
        drone = ControlDrone(self.drone)
        print(self.drone)
        self.CameraLabel.show()
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.StartButton.hide()

    def up(self):
        if self.drone is not None:
            self.drone.up(10)

    def down(self):
        if self.drone is not None:
            self.drone.down(10)

    def take_picture(self):
        if self.drone is not None:
            self.drone.take_picture()

    def palm_land(self):
        if self.drone is not None:
            self.drone.palm_land()

    def close_conection(self):
        if self.drone is not None:
            self.CameraLabel.hide()
            self.StartButton.show()
            self.drone.quit()

    def land(self):
        if self.drone is not None:
            self.drone.land()
    
    def flight(self):
        if self.drone is not None:
            self.drone.takeoff()

app = QApplication(sys.argv)
ex2 = MainWindow()
ex2.setWindowTitle("Control de Drone")
ex2.show()
sys.exit(app.exec_())
