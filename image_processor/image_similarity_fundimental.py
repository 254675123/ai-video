# -*- coding: utf-8 -*-

# Birdy 17/11/27
import os
import PIL.Image as Image

#current_path = os.path.abspath(__file__)
current_path = os.path.dirname(__file__)

def difference(hist1,hist2):
    sum1 = 0
    for i in range(len(hist1)):
       if (hist1[i] == hist2[i]):
          sum1 += 1
       else:
           sum1 += 1 - float(abs(hist1[i] - hist2[i]))/ max(hist1[i], hist2[i])
    return sum1/len(hist1)

def similary_calculate(path1 , path2 , mode):
    if(mode == 3):
        # 如果是frame的话，可以直接使用
        # img = cv2.resize(frame, (8, 8))
        img1 = Image.open(path1).resize((8,8)).convert('1')
        img2 = Image.open(path2).resize((8,8)).convert('1')
        hist1 = list(img1.getdata())
        hist2 = list(img2.getdata())
        return difference(hist1, hist2)

    # 预处理
    img1 = Image.open(path1).resize((256,256)).convert('RGB')
    img2 = Image.open(path2).resize((256,256)).convert('RGB')
    if(mode == 1):
        return difference(img1.histogram(), img2.histogram())
    if(mode == 2):
        sum = 0;
        for i in range(4):
            for j in range(4):
                hist1 = img1.crop((i*64, j*64, i*64+63, j*64+63)).copy().histogram()
                hist2 = img2.crop((i*64, j*64, i*64+63, j*64+63)).copy().histogram()
                sum += difference(hist1, hist2)
                #print difference(hist1, hist2)
        return sum/16
    return 0


def readfolder(folder,pic, mode):
# 不同的mode对应不同的类型
    file_list = []
    t = 0
    file_temp = ''
    for root,directors,files in os.walk(folder):
        for filename in files:
            filepath = os.path.join(root,filename)
            if (filepath.endswith(".png") or filepath.endswith(".jpg")):
               remember = similary_calculate(pic,filepath,mode)
               print(filename)
               print(remember)
               if (remember > t) and remember!= 1:
                   file_temp = filename
                   t = remember

    return file_temp

if __name__ == '__main__':
    print("###########直方图的距离计算#############")
    print("相似度最高的图是" + readfolder(current_path+'/../test','./../data/1073.jpg',1))
    print("###########分块直方图的距离计算#############")
    print("相似度最高的图是" + readfolder(current_path+'/../test','./../data/1073.jpg',2))
    print("##############感知哈希算法###############")
    print("相似度最高的图是" + readfolder(current_path+'/../test','./../data/1073.jpg',3))
