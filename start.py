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
        position = model_wrapper.process_image(img)
        if position is not None:
            drone.get_movement(position)
        # skeleton_drawer = vis.SkeletonDrawer(img, draw_config)
        # for skeleton in skeletons:
        #     skeleton.draw_skeleton(skeleton_drawer.joint_draw, skeleton_drawer.kpt_draw)
        return img

    def run(self):
        while True:
            counter = 0
            for frame in container.decode(video=0):               
                if counter == 9:
                    rgbImage = np.array(frame.to_image())
                    #rgbImage = cv2.resize(rgbImage, (640, 480))
                    processed_img_rgb = self.process_frame(rgbImage)
                    
                    h, w, ch = processed_img_rgb.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    counter = 0
                counter+=1
                # if frame.time_base < 1.0/60:
                #     time_base = 1.0/60
                # else:
                #     time_base = frame.time_base
                


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

    def take_picture(self):
        self.drone.take_picture()

    def palm_land(self):
        self.drone.palm_land()

    def close_conection(self):
        self.CameraLabel.hide()
        self.StartButton.show()
        self.drone.quit()

    def land(self):
        self.drone.land()
    
    def flight(self):
        self.drone.takeoff()

app = QApplication(sys.argv)
ex2 = MainWindow()
ex2.setWindowTitle("Control de Drone")
ex2.show()
sys.exit(app.exec_())
