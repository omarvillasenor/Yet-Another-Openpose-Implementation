"""
Este archivo contiene las funciones de la interfaz y a su vez controles básicos del drone
"""

from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import interfaz.drone as dr #Esta es la fución que se conecta al drone y obtiene el contenedor del video
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

#variables globales necesarias para controlar el drone
container = None
drone = None
model_path = "trained_models/model11_test-15Sun1219-2101"
model_wrapper = ModelWrapper(model_path)


class Thread(QThread):
    """
    Esta clase permite ejecutar de forma paralela a la interfaz la imagen que nos provee la cámara del dron
    """

    changePixmap = pyqtSignal(QImage)
    
    def process_frame(self, img):
        global model_wrapper
        return model_wrapper.process_image(img)

    #Esta función arranca el hilo, muestra la imagen, la analiza y obtiene la posición que contiene la persona (Basado en los puntos definidos)
    def run(self):
        flag = False
        frame_skip = 300
        last = ""
        while True:
            time.sleep(0.01)
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                rgbImage = np.array(frame.to_image())
                position = self.process_frame(rgbImage)

                if position is not None:
                    last = position
                    drone.get_movement(position)
                    flag = True
                elif last != "" and position is None:
                    if flag == True:
                        drone.get_movement(last, 0)
                        flag = False
                else:
                    drone.move_up(1)

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
        self.hide_buttons()
        self.drone = None
        self.setFixedSize(self.width(),self.height())
        self.speed = 10

    def hide_buttons(self):
        self.StartButton.show()
        self.PictureButton.hide()
        self.close_button.hide()
        self.StopButton.hide()
        self.PalmButton.hide()
        self.FlightButton.hide()
        self.UpButton.hide()
        self.DownButton.hide()
        self.CameraLabel.hide()

    def show_buttons(self):
        self.StartButton.hide()
        self.PictureButton.show()
        self.close_button.show()
        self.StopButton.show()
        self.PalmButton.show()
        self.FlightButton.show()
        self.UpButton.show()
        self.DownButton.show()
        self.CameraLabel.show()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.CameraLabel.setPixmap(QPixmap.fromImage(image))

    #Esta función arranca el drone e inicializa los botones de la interfaz
    def start_drone(self):
        global container, drone
        self.drone, container = dr.start_drone()
        if self.drone != None:
            self.show_buttons()
            drone = ControlDrone(self.drone)
            self.CameraLabel.show()
            th = Thread(self)
            th.changePixmap.connect(self.setImage)
            th.start()
            self.StartButton.hide()
            self.flight()
            self.up()
            self.up()
        else:
            self.errorMessage("No se encontró un drone para conectar, verifique la red WiFi y la batería")
            self.close()

    def errorMessage(self, message):
        errorBox = QMessageBox()
        errorBox.setIcon(QMessageBox.Warning)
        errorBox.setText(message)
        errorBox.setWindowTitle("ERROR")
        errorBox.exec_()

    def up(self):
        if self.drone is not None:
            self.drone.up(self.speed*1.5)

    def down(self):
        if self.drone is not None:
            self.drone.down(10)

    def take_picture(self):
        global drone
        drone.take_picture()

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
