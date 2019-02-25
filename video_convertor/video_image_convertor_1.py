# encoding: UTF-8

# 不建议使用，生成的视频大，压缩率不够，推荐ffmpeg
import glob as gb
import cv2

def images_video():
    img_path = gb.glob("G:\\temp_picture\\*.jpg")
    videoWriter = cv2.VideoWriter('test.mp4', cv2.VideoWriter_fourcc(*'MJPG'), 25, (640,480))

    for path in img_path:
        img  = cv2.imread(path)
        img = cv2.resize(img,(640,480))
        videoWriter.write(img)




def camera_video_img():
    cap = cv2.VideoCapture(0)

    while cv2.waitKey(30)!=ord('q'):
        retval, image = cap.read()
        cv2.imshow("video",image)
    cap.release()