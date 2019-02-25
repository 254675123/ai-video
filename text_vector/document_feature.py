# -*- coding:utf-8 -*-

import os
import sys

import gensim
from gensim.models import Doc2Vec

from tools.file_util import FilePath

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

class TextVector:
    """
    文本向量，计算2个文本句子之间的相似度
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.model = None

        self.index_catalog = {}


    def train(self, sentences_words, course_base_code):
        # 如果模型已经生成，仅需要加载
        model_file = u'{}/model_folder/{}.model'.format(curPath, course_base_code)
        if FilePath.fileExist(model_file):
            # you can continue training with the loaded model!
            print('model has exist, loading')
            self.model = Doc2Vec.load(model_file)
            print('has been loaded.')

            # 序号和名称对应
            count = 0
            for words_tuple in sentences_words:
                self.index_catalog[count] = words_tuple
                count += 1
            return

        # 加载数据
        documents = []
        # 使用count当做每个句子的“标签”，标签和每个句子是一一对应的
        count = 0
        for words_tuple in sentences_words:
            words = words_tuple[2]
            self.index_catalog[count] = words_tuple
            # 这里documents里的每个元素是二元组，具体可以查看函数文档
            documents.append(gensim.models.doc2vec.TaggedDocument(words, [str(count)]))
            count += 1
            if count % 100 == 0:
                print('{} has loaded...'.format(count))

        # 模型训练
        print('start instance doc2vec')
        self.model = Doc2Vec(dm=1, vector_size=200, window=8, min_count=1, workers=4, epochs=2000)
        print('start build vocab')
        self.model.build_vocab(documents)
        print('start training')
        self.model.train(documents, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        # 保存模型
        print('save model')
        self.model.save(model_file)

    def test_doc2vec(self, sentence_words):
        # 加载模型
        #model = Doc2Vec.load('models/ko_d2v.model')
        model = self.model
        # 与标签‘0’最相似的
        #print(model.docvecs.most_similar('0'))
        # 进行相关性比较
        #print(model.docvecs.similarity('0', '1'))
        # 输出标签为‘10’句子的向量
        #print(model.docvecs['10'])
        # 也可以推断一个句向量(未出现在语料中)
        #words = u"여기 나오는 팀 다 가슴"
        #course_name = u'比较教育学'
        #words = jieba.cut(course_name)
        print('开始获取测试向量')
        vector = model.infer_vector(sentence_words)
        print('开始预测')
        #sims = model.docvecs.most_similar([vector], topn=len(model.docvecs))
        sims = model.docvecs.most_similar([vector], topn=1)
        # print('得到前10相似结果')
        # for sim in sims:
        #     name = self.index_catalog.get(int(sim[0]))
        #     print('{}, {}'.format(name, sim[1]))

        # 也可以输出词向量
        #print(model[u'가슴'])
        return sims



if __name__ == "__main__":
    tv = TextVector()
    tv.train()
    tv.test_doc2vec()
