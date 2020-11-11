from applications.model_wrapper import ModelWrapper
import configs.draw_config as draw_config
from drone.control import ControlDrone
import visualizations as vis
import numpy as np
import tellopy
import time
import cv2
import av


model_path = "trained_models/model11_test-15Sun1219-2101"


class CamApp:
    def __init__(self):
        self.model_wrapper = ModelWrapper(model_path)

        self.cam = cv2.VideoCapture(0)  # 0 -> index of camera
        state, cam_img = self.cam.read()
        if not state:
            raise IOError("Cannot access camera")

    def process_frame(self, img):

        skeletons = self.model_wrapper.process_image(img)

        skeleton_drawer = vis.SkeletonDrawer(img, draw_config)
        for skeleton in skeletons:
            skeleton.draw_skeleton(skeleton_drawer.joint_draw, skeleton_drawer.kpt_draw)
        return img

    def run(self):
        print("Press ESC to exit")
        drone = tellopy.Tello()
        drone.connect()
        drone.wait_for_connection(20.0)
        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        # skip first 300 frames
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                cv2.imshow('Original', image)
                cv2.imshow('Canny', cv2.Canny(image, 100, 200))
                cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
        # cv2.namedWindow("cam-test", cv2.WINDOW_AUTOSIZE)
        # while True:
        #     s, cam_img_bgr = self.cam.read()
        #     img_rgb = cv2.cvtColor(cam_img_bgr, cv2.COLOR_BGR2RGB)

        #     processed_img_rgb = self.process_frame(img_rgb)

        #     processed_img_bgr = cv2.cvtColor(processed_img_rgb, cv2.COLOR_RGB2BGR)
        #     cv2.imshow("cam-test", processed_img_bgr)

        #     key = cv2.waitKey(1)
        #     if key == 27:  # Esc key to stop
        #         break
        # cv2.destroyWindow("cam-test")


if __name__ == "__main__":
    app = CamApp()
    app.run()
