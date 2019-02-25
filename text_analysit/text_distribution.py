# -*- coding: utf-8 -*-
"""
分析文本在知识树上面的分布情况，确定一段时间内的内容是集中在一个段的知识点
"""
import os
import math
from word_spliter import jieba_splitor
from text_vector import document_feature

class Text2KnowledgeDistribution:
    splitor = jieba_splitor.JiebaSplitor()
    docvector = document_feature.TextVector()
    frame_index_kwg_dict = {}
    knowledge_code_dict = {}

    # 当前的文件目录
    curPath = os.path.abspath(os.path.dirname(__file__))

    def loadKnowledge(self, kwg_filepath):
        knowledge_list = []
        f = open(kwg_filepath, 'rb')
        ids_lines = f.read().decode('utf-8', 'ignore')
        ids_lines_list = ids_lines.split('\r\n')
        index = 0
        for line in ids_lines_list:
            index += 1
            if index == 1:
                continue
            line = line.strip('\n')
            line_k = line.split(' ')
            if len(line_k) < 2:
                continue

            line_k_code = line_k[0]
            line_k_word = line_k[1]
            line_k_word_array = self.splitor.split1list(line_k_word)

            if knowledge_list.__contains__(line):
                continue
            else:
                knowledge_list.append((line_k_code, line_k_word, line_k_word_array))
            self.knowledge_code_dict[line_k_code] = line_k_word
        return knowledge_list

    def loadTextList(self, directory_path):
        text_file_list = []
        if not os.path.exists(directory_path):
            return text_file_list

        for item in os.listdir(directory_path):
            basename = os.path.basename(item)
            # windows下文件编码为GBK，linux下为utf-8
            # try:
            #     decode_str = basename.decode("GBK")
            # except UnicodeDecodeError:
            #     decode_str = basename.decode("utf-8")

            text_file_list.append(basename)
        return text_file_list

    def readFileContent(self, filepath):
        f = open(filepath, 'r', encoding='utf-8')
        content = f.read()
        return content

    def compute_similarity(self, course_base_code, file_name):
        kwg_filepath = self.curPath+'./knowledge_folder/{}.txt'.format(course_base_code)
        print('开始加载知识点集')
        kwg_list = self.loadKnowledge(kwg_filepath)
        # 训练模型
        print('开始训练模型')
        self.docvector.train(kwg_list, course_base_code)
        print('开始预测')
        # 测试数据
        text_filepath = self.curPath+'/../image_ocr/text_folder/{}'.format(file_name)
        text_file_list = self.loadTextList(text_filepath)
        for text_file in text_file_list:
            content = self.readFileContent('{}/{}'.format(text_filepath, text_file))
            content_words = self.splitor.split1list(content)
            sims = self.docvector.test_doc2vec(content_words)

            index = os.path.splitext(text_file)[0]

            print('{}的对应的知识点如下：'.format(content))
            sim_kwg_list = []
            for sim in sims:
                kwg = self.docvector.index_catalog.get(int(sim[0]))
                kwg_tuple = (kwg[0],kwg[1],kwg[2],sim[1])
                sim_kwg_list.append(kwg_tuple)
                print('{} {}, {}'.format(kwg[0], kwg[1], sim[1]))

            self.frame_index_kwg_dict[index] = sim_kwg_list

    def statistics(self):
        img_index_kwg_list = []
        for key, value in self.frame_index_kwg_dict.items():
            img_index_kwg_list.append((int(key), value))

        # 按帧的顺序排序
        # 由tuple组成的List排序
        # students = [('john', 'A', 15), ('jane', 'B', 12), ('dave', 'B', 10),]
        # 用key函数排序：返回由tuple组成的list
        # sorted(students, key=lambda student : student[2])   # sort by age
        # [('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)]
        # 用cmp函数排序
        # sorted(students, cmp=lambda x,y : cmp(x[2], y[2])) # sort by age
        # [('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)]

        # 这里的kwg是(index, (code, name, words))
        sort_list = sorted(img_index_kwg_list, key=lambda x:x[0])
        # 对排序后的帧，分析段
        # 分组的原则是相似度大于80%的作为分组的开始，如果连续几个都大于80%，都作为一组
        # 如果80%后，开始小于80%，也同样归属于当前组；
        # 如果再次出现80%，前面的一定是小于80%的或者是刚开始，才作为分组的开始
        # 分组的信息，只需要记录开始的帧序号
        section_index_dict = {}
        pre_similarity = 0.0
        current_section_index = 1
        has_exist_kwg_point = False
        for frame_tuple in sort_list:
            frame_index = frame_tuple[0]
            k_code = frame_tuple[1][0][0]
            k_code_part = self.getPartCode(k_code)
            cur_similarity = frame_tuple[1][0][3]
            if cur_similarity >= 0.8 and pre_similarity < 0.8:
                current_section_index = frame_index
                self.setFrameIndexSectionDict(section_index_dict, current_section_index, k_code_part)
            else:
                if has_exist_kwg_point:
                    self.setFrameIndexSectionDict(section_index_dict, current_section_index, k_code_part)
                else:
                    continue
            pre_similarity = cur_similarity
        print('统计分段完成')
        return section_index_dict

    def getPartCode(self, code, sec=4):
        if code is None:
            return code
        section_list = code.split('.')
        n_code = '.'.join(section_list[:sec])

        return n_code

    def setFrameIndexSectionDict(self, section_index_dict, current_section_index, k_code_part):
        """
        设置相同内容的为一段
        :param section_index_dict: 
        :return: 
        """
        if section_index_dict.__contains__(current_section_index):
            frame_list = section_index_dict.get(current_section_index)
            frame_list.append(k_code_part)
        else:
            frame_list = []
            frame_list.append(k_code_part)
            section_index_dict[current_section_index] = frame_list

    def compute_distribute(self, section_index_dict, file_name):
        """
        对于每一段，选择大多数的知识点为最终知识点，也算是投票的结果
        :param section_index_dict: 
        :return: 
        """
        index_kwg_list = []
        print('计算知识点分布')

        for index, kwg_code_list in section_index_dict.items():
            kwg_code_tuple = self.getMoreKwgCode(kwg_code_list)

            index_kwg_list.append((index, kwg_code_tuple))

        # 合并code 相同的
        index_kwg_code_list = []
        pre_kwg_code_tuple = None
        pre_index = 0
        for index, kwg_code_tuple in index_kwg_list:
            if pre_kwg_code_tuple is not None and pre_kwg_code_tuple[0] == kwg_code_tuple[0]:
                pre_kwg_code_tuple = (kwg_code_tuple[0], kwg_code_tuple[1]+pre_kwg_code_tuple[1])
                continue
            elif pre_kwg_code_tuple is not None:
                index_kwg_code_list.append((pre_index, pre_kwg_code_tuple))
                pre_kwg_code_tuple = kwg_code_tuple
                pre_index = index
            else:
                pre_kwg_code_tuple = kwg_code_tuple
                pre_index = index
        if pre_kwg_code_tuple is not None:
            index_kwg_code_list.append((pre_index, pre_kwg_code_tuple))

        # 对应知识点的code到名称
        # 把帧换算成时分秒
        result_list = []
        for index, kwg_code_tuple in index_kwg_code_list:
            time_string = self.frame2Time(index)
            kwg_name = self.knowledge_code_dict.get(kwg_code_tuple[0])
            result_list.append((index, time_string, kwg_code_tuple[0], kwg_name, kwg_code_tuple[1]))
        # 将结果存储
        filepath = self.curPath+'/distribution_folder/{}.txt'.format(file_name)
        self.saveText(filepath, result_list)

    def frame2Time(self, frame_count):
        """
        将视频帧的序号，转换成时分秒的具体时间点
        :param frame_count: 
        :return: 
        """
        seconds = int(frame_count) / 25
        if seconds <= 1:
            seconds = 1
        else:
            seconds = math.ceil(seconds)
        minute = int(seconds / 60)
        hour = int(minute / 60)
        minute = minute % 60
        seconds = seconds % 60

        return '{:0>2d}:{:0>2d}:{:0>2d}'.format(hour,minute,seconds)

    def saveText(self, filepath, index_kwg_list):
        f_out = open(filepath, 'w', encoding='utf-8')
        for index_kwgcode in index_kwg_list:
            f_out.write('{} {} {} {} {}'.format(index_kwgcode[0], index_kwgcode[1],index_kwgcode[2],index_kwgcode[3],index_kwgcode[4]))
            f_out.write('\n')
        f_out.close()
        pass

    def getMoreKwgCode(self, kwg_code_list):
        kwg_distribute_dict = {}
        for kwg_code in kwg_code_list:
            if kwg_distribute_dict.__contains__(kwg_code):
                kwg_distribute_dict[kwg_code] += 1
            else:
                kwg_distribute_dict[kwg_code] = 1
        sorted_kwg_code_list = sorted(kwg_distribute_dict.items(), key=lambda d: d[1],reverse=True)

        return sorted_kwg_code_list[0]

    def run(self, need_processed_video):
        course_base_code = need_processed_video[0]
        video_file = os.path.splitext(need_processed_video[1])[0]
        file_name = '{}-{}'.format(course_base_code, video_file)

        self.compute_similarity(course_base_code, file_name)
        section_index_dict = self.statistics()
        self.compute_distribute(section_index_dict, file_name)

if __name__ == '__main__':
    #t2kd = Text2KnowledgeDistribution()
    #t2kd.run()
    pass