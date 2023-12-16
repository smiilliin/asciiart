import cv2
from PIL import Image
import numpy as np

videoInput = 'badApple.mp4'
videoOutput = 'output_video.mp4'

cap = cv2.VideoCapture(videoInput)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps =  cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter(videoOutput, fourcc, fps, (int(width), int(height)))

while cap.isOpened():
  success, frame = cap.read()

  if not success:
    break

  image = Image.fromarray(frame)
  out.write(np.array(frame))
  
cap.release()
out.release()
