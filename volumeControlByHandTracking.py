import time

import cv2
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
######################################
wCam, hCam = 1200, 720
######################################

cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# volume.GetMute()
# volume.GetMasterVolumeLevel()

volRange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0.0, None)
minVol = volRange[0]
maxVol = volRange[1]

vol = 0

cTime = 0
pTime = 0

dectator = htm.handDetector(detectionCon=0.7)

minV=10
maxV=150

while True:
    success, img = cap.read()

    img = dectator.findHands(img, draw=True)
    lmList = dectator.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 12, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 12, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 12, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        # Hand Range was 30-200
        # Volume Range -65-0

        # minV = min(minV, length)
        # maxV = max(maxV, length)

        vol = np.interp(length, [minV, maxV], [minVol, maxVol])
        # print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)

    # else:
    #     minV = 1000
    #     maxV = 0

    # cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    # cv2.rectangle(img, (50, int(vol)), (85, 400), (0, 255, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)


    cv2.imshow("Image", img)
    cv2.waitKey(1)
