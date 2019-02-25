# encoding: UTF-8

# 图片灰度化（白-灰-黑）+二值化（黑白2色）

from PIL import Image

#  load a color image
im = Image.open('durant.jpg')

#  convert to grey level image
Lim = im.convert('L')
Lim.save('grey.jpg')

#  setup a converting table with constant threshold
threshold = 185
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

# convert to binary image by the table
bim = Lim.point(table, '1')

bim.save('durant_grey.jpg')