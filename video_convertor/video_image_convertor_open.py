# encoding: UTF-8

import os
import cv2
from PIL import Image
from image_processor import image_similarity_fundimental
from tools.file_util import FilePath
import time

class Video2Image:
    """
    将视频转换成图片，视频的1s为25帧，大部分的帧是相同的；
    所以需要对相同的图片分组，只取一张即可。
    """
    # 当前的文件目录
    curPath = os.path.abspath(os.path.dirname(__file__))

    def video2jpg(self, sp):
        """ 将视频转换成图片
            sp: 视频路径 """
        cap = cv2.VideoCapture(sp)
        suc = cap.isOpened()  # 是否成功打开
        frame_count = 0
        while suc:
            frame_count += 1
            suc, frame = cap.read()
            #print(frame.shape)
            yield frame, frame_count
            #params = []
            #params.append(2)  # params.append(1)
            #cv2.imwrite('mv\\%d.jpg' % frame_count, frame, params)

        cap.release()
        print('unlock image: ', frame_count)

    def frameToImage(self, frame):
        img = None
        if frame is not None:
            img = Image.fromarray(frame)  # 完成np.array向PIL.Image格式的转换
            # img = img.resize((80, 80)).convert('1')

        return img

    def saveFrame(self, frame, frame_count, video_to_image_file_path):
        params = []
        params.append(2)  # params.append(1)
        cv2.imwrite(video_to_image_file_path+'/%d.jpg' % frame_count, frame, params)

    def loadImage(self, count, video_to_image_file_path):
        path = video_to_image_file_path+'/%d.jpg' % count
        img = Image.open(path).resize((80, 80)).convert('1')
        return img

    def similary_calculate(self, img1 , img2):
        hist1 = list(img1.getdata())
        hist2 = list(img2.getdata())
        return image_similarity_fundimental.difference(hist1, hist2)

    def similarity_mode_3(self, image1, image2):
        """
        感知哈希算法
        :param image1: 
        :param image2: 
        :return: 
        """
        # 如果是frame的话，可以直接使用
        # img = cv2.resize(frame, (8, 8))
        img1 = image1.resize((128, 128)).convert('1')
        img2 = image2.resize((128, 128)).convert('1')
        hist1 = list(img1.getdata())
        hist2 = list(img2.getdata())
        sim = image_similarity_fundimental.difference(hist1, hist2)
        return sim

    def similarity_mode_2(self, image1, image2):
        """
        直方图的距离计算
        :param image1: 
        :param image2: 
        :return: 
        """
        # 预处理
        img1 = image1.resize((256, 256)).convert('RGB')
        img2 = image2.resize((256, 256)).convert('RGB')
        sim = image_similarity_fundimental.difference(img1.histogram(), img2.histogram())
        return sim

    def similarity_mode_1(self, image1, image2):
        """
        分块直方图的距离计算
        :param image1: 
        :param image2: 
        :return: 
        """
        sum = 0;
        img1 = image1.resize((256, 256)).convert('RGB')
        img2 = image2.resize((256, 256)).convert('RGB')
        for i in range(4):
            for j in range(4):
                hist1 = img1.crop((i * 64, j * 64, i * 64 + 63, j * 64 + 63)).copy().histogram()
                hist2 = img2.crop((i * 64, j * 64, i * 64 + 63, j * 64 + 63)).copy().histogram()
                sum += image_similarity_fundimental.difference(hist1, hist2)
                # print difference(hist1, hist2)
        return sum / 16

    def similary_calculate_multiple(self, image1 , image2):
        sim = 0
        sim1 = self.similarity_mode_1(image1, image2)
        if sim1 > sim:
            sim = sim1
        sim2 = self.similarity_mode_2(image1, image2)
        if sim2 > sim:
            sim = sim2
        sim3 = self.similarity_mode_3(image1, image2)
        if sim3 > sim:
            sim = sim3

        return sim

    def run(self, need_processed_video):
        #course_base_code = need_processed_video[0]
        video_file = need_processed_video[1]
        video_file_path = '{}/../data/course_video/{}'.format(self.curPath, video_file)

        # 检查文件夹是否存在，若不存在，创建
        video_to_image_file_path = '{}/img_folder/{}'.format(self.curPath, need_processed_video[2])
        FilePath.mkdir(video_to_image_file_path)
        # 清理图片文件夹
        print('正在清理文件夹')
        FilePath.del_file(video_to_image_file_path)
        print('清理完毕，开始进行转换...')
        pre_img = None
        for frame, frame_count in self.video2jpg(video_file_path):
            if frame_count % 100 == 0:
                print('已处理{}帧'.format(frame_count))
            # 对frame进行resize
            if pre_img is None:
                pre_img = self.frameToImage(frame)
                if pre_img is None:
                    break
                self.saveFrame(frame, frame_count, video_to_image_file_path)
            else:
                # 当前frame和前一个frame比较，如果相似度大于90的，就认为是一个
                cur_img = self.frameToImage(frame)
                if cur_img is None:
                    break
                sim = self.similary_calculate_multiple(pre_img,cur_img)
                if sim > 0.95:
                    continue
                else:
                    pre_img = cur_img
                    self.saveFrame(frame, frame_count, video_to_image_file_path)



if __name__ == '__main__':
    video_file = "./../data/glx.mp4"
    start_time = time.time()
    vv = Video2Image()
    vv.run(video_file)
    #time.sleep(1)
    end_time = time.time()

    print('花费时间:{}秒'.format(end_time - start_time))
