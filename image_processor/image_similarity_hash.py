# encoding: UTF-8
# 计算2张图片的相似度
# "感知哈希算法"（Perceptual hash algorithm），
# 它的作用是对每张图片生成一个"指纹"（fingerprint）字符串，
# 然后比较不同图片的指纹。结果越接近，就说明图片越相似。
"""
4.1  算法步骤
4.1.1 缩小尺寸
　　将图片缩小到8x8的尺寸，总共64个像素。这一步的作用是去除图片的细节，
只保留结构、明暗等基本信息，摒弃不同尺寸、比例带来的图片差异。
4.1.2  简化色彩
　　将缩小后的图片，转为64级灰度。也就是说，所有像素点总共只有64种颜色。
4.1.3  计算平均值
　　计算所有64个像素的灰度平均值
4.1.4  比较像素的灰度平均值
　　将每个像素的灰度，与平均值进行比较。大于或等于平均值，记为1；小于平均值，记为0。
4.1.5 计算哈希值
　　将上一步的比较结果，组合在一起，就构成了一个64位的整数，这就是这张图片的指纹。组合的次序并不重要，
只要保证所有图片都采用同样次序就行了。
　　得到指纹以后，就可以对比不同的图片，看看64位中有多少位是不一样的。在理论上，这等同于计算"汉明距离"（Hamming distance）。
如果不相同的数据位不超过5，就说明两张图片很相似；如果大于10，就说明这是两张不同的图片。
"""
import glob
import os
import sys
from functools import reduce
from PIL import Image

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'


def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((80, 80), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 6400.
    print('avg:{}'.format(avg))
    return reduce(lambda x,y,z: x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

def one_to_many():
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        print("Usage: %s image.jpg [dir]" % sys.argv[0])
    else:
        im, wd = sys.argv[1], '.' if len(sys.argv) < 3 else sys.argv[2]
        h = avhash(im)

        os.chdir(wd)
        images = []
        for ext in EXTS:
            images.extend(glob.glob('*.%s' % ext))

        seq = []
        # isatty方法检测文件是否连接到一个终端设备
        prog = int(len(images) > 50 and sys.stdout.isatty())
        for f in images:
            seq.append((f, hamming(avhash(f), h)))
            if prog:
                perc = 100. * prog / len(images)
                x = int(2 * perc / 5)
                print('\rCalculating... [' + '#' * x + ' ' * (40 - x) + ']')
                print('%.2f%%' % perc, '(%d/%d)' % (prog, len(images)))
                sys.stdout.flush()
                prog += 1

        if prog: print('prog')
        for f, ham in sorted(seq, key=lambda i: i[1]):
            print("%d\t%s" % (ham, f))

def one_to_one():
    im = './../mv/1.jpg'
    h = avhash(im)
    target = './../mv/2.jpg'
    t = avhash(target)
    sim = hamming(t, h)
    print('sim:{}'.format(sim))

if __name__ == '__main__':
    one_to_one()
