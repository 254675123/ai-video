# encoding: UTF-8
"""
1. 首先读取基础课程和视频资源的关系表
2. 对每一个视频资源，开始处理，处理的过程中，带上基础课程信息
"""
import os
from tools.file_util import FilePath
from tools.excel_xls import ExcelReader
from video_convertor import video_image_convertor_open
from image_ocr import image_text
from text_analysit import text_distribution
class AssociateKV:
    """
    对视频资源进行知识点定位关联
    """

    def __init__(self):
        """
        initialize local variables.
        """
        # 读取基础课程和视频资源的excel文件
        self.excel_reader = ExcelReader.ExcelReader()

        # 已经处理过的video文件
        self.processed_video_list = []
        # video 处理成图片
        self.video2image = video_image_convertor_open.Video2Image()
        # image 处理成文本
        self.image2text = image_text.Image2Text()
        # text 与知识点相似分布
        self.text2kwg = text_distribution.Text2KnowledgeDistribution()

    def loadNeedProcessedVideo(self, filepath):
        need_processed_video_list = []
        if not FilePath.fileExist(filepath):
            return need_processed_video_list

        # 如果是文本文件，按文本文件读取, 这里暂且用文本文件做测试
        f_input = open(filepath, 'r')
        for line in f_input:
            line = line.strip('\n')
            line_secs = line.split(' ')
            if len(line_secs) < 2:
                continue
            # 去掉后缀，只取名字，用作创建文件夹名字使用
            course_base_code = line_secs[0]
            video_file = os.path.splitext(line_secs[1])[0]
            directory_name = '{}-{}'.format(course_base_code, video_file)
            # directory_name = line_secs[1].split('.')[0]
            need_processed_video_list.append((line_secs[0], line_secs[1], directory_name))

        # 如果是excel文件，按excel文件读取


        return need_processed_video_list

    def associateFlow(self, scope_filepath):
        """
        关联的流程
        :param scope_filepath: 
        :return: 
        """
        # 获取需要处理的基础课程与视频资源表
        need_processed_video_list = self.loadNeedProcessedVideo(scope_filepath)
        length = len(need_processed_video_list)
        index = 0
        for need_processed_video in need_processed_video_list:
            # 转换为图片
            self.video2image.run(need_processed_video)
            # 图片识别成文本
            self.image2text.run(need_processed_video)
            # 文本与知识点相似度统计
            self.text2kwg.run(need_processed_video)

            index += 1
            print('已经处理了{}/{}'.format(index, length))

if __name__ == '__main__':
    scope_filepath = u'./scope_folder/scope_video_20181219_test.txt'
    akv = AssociateKV()
    akv.associateFlow(scope_filepath)
    print('task execute over.')

