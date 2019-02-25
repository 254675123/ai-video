# -*- coding: utf-8 -*-
"""
将图像中的文本识别出来
"""
import os

from image_ocr import tencent_ocr_api
from tools.file_util import FilePath


class Image2Text:
    """
    将图片中的文字识别出来
    """
    # 当前的文件目录
    curPath = os.path.abspath(os.path.dirname(__file__))

    def loadImageList(self, directory_path):
        image_file_list = []
        if not os.path.exists(directory_path):
            return image_file_list

        for item in os.listdir(directory_path):
            basename = os.path.basename(item)
            # windows下文件编码为GBK，linux下为utf-8
            # try:
            #     decode_str = basename.decode("GBK")
            # except UnicodeDecodeError:
            #     decode_str = basename.decode("utf-8")

            image_file_list.append(basename)
        return image_file_list

    def saveText(self, text_filepath, text_lines):
        f_out = open(text_filepath, 'w', encoding='utf-8')
        f_out.write(' '.join(text_lines))
        f_out.close()
        pass

    def loadHasProcessedImageIndex(self, file_name):
        index_list = []
        processed_filepath = self.curPath+'./processed/{}.txt'.format(file_name)
        if not FilePath.fileExist(processed_filepath):
            return index_list
        f = open(processed_filepath,'r' , encoding='utf-8')
        for line in f:
            line = line.strip('\n')
            index_list.append(line)
        return index_list

    def saveProcessedImageIndex(self, filename, index):
        processed_filepath = self.curPath+'/processed/{}.txt'.format(filename)
        f = open(processed_filepath, 'a', encoding='utf-8')
        f.write(index)
        f.write('\n')
        f.close()
        pass

    def run(self, need_processed_video):
        file_directory = need_processed_video[2]

        processed_file = self.loadHasProcessedImageIndex(file_directory)
        image_filepath = self.curPath+'/../video_convertor/img_folder/'+file_directory
        image_file_list = self.loadImageList(image_filepath)
        text_filepath_dir = self.curPath+'/text_folder/{}'.format(file_directory)
        FilePath.mkdir(text_filepath_dir)

        length_file = len(image_file_list)
        index = 0
        for image_file in image_file_list:
            image_index = image_file.split('.')[0]
            if processed_file.__contains__(image_index):
                index += 1
                continue

            text_lines = tencent_ocr_api.invoke_api_file('{}/{}'.format(image_filepath,image_file))
            if len(text_lines) == 0:
                index+=1
                continue
            # 保存文件的名称

            text_filepath =  '{}/{}.txt'.format(text_filepath_dir, image_index)
            self.saveText(text_filepath, text_lines)
            index += 1
            print('已处理{}/{}'.format(index, length_file))
            self.saveProcessedImageIndex(file_directory, image_index)

if __name__ == '__main__':
    #run(need_processed_video)
    pass