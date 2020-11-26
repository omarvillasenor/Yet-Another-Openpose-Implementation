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
    detected_class = pyqtSignal(str)
    
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
            try:
                for frame in container.decode(video=0):
                    if 0 < frame_skip:
                        frame_skip = frame_skip - 1
                        continue
                    start_time = time.time()
                    rgbImage = np.array(frame.to_image())
                    position = self.process_frame(rgbImage)
                    clase = "Nada" if position == None else position
                    if position is not None:
                        last = position
                        drone.get_movement(position)
                        flag = True
                    elif last != "" and position is None:
                        if flag == True:
                            drone.get_movement(last, 0)
                            flag = False
                    else:
                        drone.move_up(0)

                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    self.detected_class.emit(clase)
                    if frame.time_base < 1.0/60:
                        time_base = 1.0/60
                    else:
                        time_base = frame.time_base
                    frame_skip = int((time.time() - start_time)/time_base)
            except:
                self.exit()
               
                


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
        self.LeftButton.clicked.connect(self.move_left)
        self.RightButton.clicked.connect(self.move_right)
        self.UpButton.clicked.connect(self.up)
        self.DownButton.clicked.connect(self.down)
        self.TakeOffButton.clicked.connect(self.flight)
        self.hide_buttons()
        self.drone = None
        self.setFixedSize(self.width(),self.height())
        self.speed = 10
        self.th = Thread(self)
        self.is_flying = False

    def hide_buttons(self):
        self.StartButton.show()
        self.PictureButton.hide()
        self.close_button.hide()
        self.StopButton.hide()
        self.PalmButton.hide()
        self.LeftButton.hide()
        self.RightButton.hide()
        self.UpButton.hide()
        self.DownButton.hide()
        self.CameraLabel.hide()
        self.TakeOffButton.hide()
        self.ClassLabel.hide()
        self.ActualClass.hide()

    def show_buttons(self):
        self.StartButton.hide()
        self.PictureButton.show()
        self.close_button.show()
        self.StopButton.show()
        self.PalmButton.show()
        self.LeftButton.show()
        self.RightButton.show()
        self.UpButton.show()
        self.DownButton.show()
        self.CameraLabel.show()
        self.TakeOffButton.show()
        self.ClassLabel.show()
        self.ActualClass.show()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.CameraLabel.setPixmap(QPixmap.fromImage(image))
    
    @pyqtSlot(str)
    def setClass(self, clase):
        self.ActualClass.setText(clase)

    #Esta función arranca el drone e inicializa los botones de la interfaz
    def start_drone(self):
        global container, drone
        self.drone, container = dr.start_drone()
        if self.drone is not None and self.is_flying == False:
            self.show_buttons()
            drone = ControlDrone(self.drone)
            self.CameraLabel.show()
            self.th.changePixmap.connect(self.setImage)
            self.th.detected_class.connect(self.setClass)
            self.th.start()
            self.StartButton.hide()
        else:
            self.errorMessage("No se encontró un drone para conectar, verifique la red WiFi y la batería")
            self.close()
            exit(0)

    def errorMessage(self, message):
        errorBox = QMessageBox()
        errorBox.setIcon(QMessageBox.Warning)
        errorBox.setText(message)
        errorBox.setWindowTitle("ERROR")
        errorBox.exec_()
        self.close()

    def up(self):
        if self.drone is not None and self.is_flying != False:
            self.th.sleep(1)
            self.drone.up(self.speed*3)

    def down(self):
        if self.drone is not None:
            # self.th.sleep(2)
            self.drone.down(10)

    def take_picture(self):
        if self.drone is not None and self.is_flying != False:
            # self.th.sleep(2)
            global drone
            drone.take_picture()

    def palm_land(self):
        if self.drone is not None and self.is_flying != False:
            # self.th.sleep(2)
            self.drone.palm_land()

    def close_conection(self):
        if self.drone is not None:
            self.th.sleep(1)
            self.land()
            self.CameraLabel.hide()
            self.StartButton.show()
            self.drone.quit()
            self.th.exit()
            exit(0)
        else:
            #self.th.exit()
            exit(0)

    def land(self):
        if self.drone is not None and self.is_flying != False:
            # self.th.sleep(2)
            self.drone.land()
            self.is_flying = False
    
    def flight(self):
        if self.drone is not None and self.is_flying == False:
            self.th.sleep(2)
            self.drone.takeoff()
            self.drone.up(self.speed*2)
            self.is_flying = True

    def move_right(self):
        if self.drone is not None and self.is_flying != False:
            # self.th.sleep(2)
            self.drone.counter_clockwise(5)
            self.drone.right(10)

    def move_left(self):
        if self.drone is not None and self.is_flying != False:
            # self.th.sleep(2)
            self.drone.clockwise(5)
            self.drone.left(10)

app = QApplication(sys.argv)
ex2 = MainWindow()
ex2.setWindowTitle("Control de Drone")
ex2.show()
sys.exit(app.exec_())
