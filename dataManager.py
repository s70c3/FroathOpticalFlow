import os
import cv2
import numpy as np


class DataManager(object):
    """Class for generating batches of frames from video"""

    def __init__(self, videoPath):
        """
        Constructor
        Parameters:
            :videoPath(str) - path for the input video
        Returns:
        """
        if os.path.exists(videoPath):
            self.video = cv2.VideoCapture(videoPath)
            self.fps = int(self.video.get(cv2.CAP_PROP_FPS))
        else:
            raise FileNotFoundError('No video file: '+videoPath)

    def preprocessing(self, frame):
        """
         Produce input for neural network.
         Parameters:
            :frame (np.ndarray): source image,
         Returns:
            :np.ndarray - contrast gray image
         """
        import cv2
        source = frame.copy()
        frame = cv2.GaussianBlur(frame, (11, 11), 0)
        frame = cv2.resize(frame, (256, 256))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v)
        hsv = cv2.merge([h, s, v])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(gray)
        img = img/255.
        img = np.reshape(img, img.shape + (1,))
        return img, frame, source

    def get_frames_gen(self, batch_size=32, num=np.inf):
        """
          Batches generator for neural network input.
          Parameters:
              :batch_size(int) - size of the images batch for Unet.
              :num(int) - maximum number of frames.
          """
        counter = 0
        while self.video.isOpened() and counter < num:
            imgs = []
            imgs_color = []
            sources = []
            for i in range(batch_size):
                ret, img = self.video.read()
                if not ret:
                    break
                img, img_color, source = self.preprocessing(img)
                imgs_color.append(img_color)
                imgs.append(img)
                sources.append(source)
                counter += 1
            yield np.asarray(imgs), np.asarray(imgs_color), np.asarray(sources)
        self.video.release()

