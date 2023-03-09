import websockets
import asyncio
import cv2
import numpy as np

import torch
from models.detector import *
import gc

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
detector = Detector(model_type='PS')
async def main():
    url = 'ws://127.0.0.1:8000/ws'
    # url = 'http://192.168.8.102:8080/video'
    
    async with websockets.connect(url) as ws:
         #count = 1
         while True:
            contents = await ws.recv()
            arr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
            resized_img  =  cv2.resize(frame, (400, 400), interpolation = cv2.INTER_NEAREST)
            output = detector.test(resized_img)
            cv2.imshow('frame', output)
            cv2.waitKey(1)
            
            #cv2.imwrite("frame%d.jpg" % count, frame)
            #count += 1
                    
asyncio.run(main())


