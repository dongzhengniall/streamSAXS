import numpy as np
from PIL import Image
import h5py

imgpath='D:\data\mouse1s-2\mouse1s-saxs_00002.tif'
img=Image.open(imgpath, mode='r')
image_all = np.array(img)

imgpathf = 'D:\data\mouse1s-2\mouse1s-saxs_'
min_num = 2
max_num = 100

data = np.full((max_num - min_num, 3, 5), float('nan'))

for i in range(2, 593):
    if i == min_num:
        imgpath = 'D:\data\mouse1s-2\mouse1s-saxs_00002.tif'
        img = Image.open(imgpath, mode='r')
        image_all = np.array(img)
    print(i)
    imgpath = imgpathf + (5 - len(str(i))) * '0' + str(i) + '.tif'
    img=Image.open(imgpath, mode='r')
    img_array = np.array(img)
    image_all = np.dstack((image_all, img_array))

image_all = image_all.swapaxes(0,1)
image_all = image_all.swapaxes(0,2)


with h5py.File('D:\\cuticle-waxs.h5', 'w') as hf:
    hf.create_dataset("data",  data=image_all)






# imgpath='D:\data\mouse1s-2\mouse1s-saxs_00002.tif'
# img=Image.open(imgpath, mode='r')
# image_all = np.array(img)
#
# imgpathf = 'D:\data\mouse1s-2\mouse1s-saxs_'
# for i in range(3, 593):
#     print(i)
#     imgpath = imgpathf + (5 - len(str(i))) * '0' + str(i) + '.tif'
#     img=Image.open(imgpath, mode='r')
#     img_array = np.array(img)
#     image_all = np.dstack((image_all, img_array))
#
# image_all = image_all.swapaxes(0,1)
# image_all = image_all.swapaxes(0,2)
#
#
# with h5py.File('D:\\cuticle-waxs.h5', 'w') as hf:
#     hf.create_dataset("data",  data=image_all)

# def save_h5(times=0):
#     if times == 0:
#         imgpath = 'D:\data\mouse1s-2\mouse1s-saxs_00002.tif'
#         img = Image.open(imgpath, mode='r')
#         image_all = np.array(img)
#
#         h5f = h5py.File('D:\\cuticle-waxs.h5', 'w')
#         dataset = h5f.create_dataset("data", (592, image_all.shape[0], image_all.shape[1]),
#                                      maxshape=(None, image_all.shape[0], image_all.shape[1]),
#                                      # chunks=(1, 1000, 1000),
#                                      dtype='float32')
#     else:
#         h5f = h5py.File('D:\\cuticle-waxs.h5', 'a')
#         dataset = h5f['data']
#     # 关键：这里的h5f与dataset并不包含真正的数据，
#     # 只是包含了数据的相关信息，不会占据内存空间
#     #
#     # 仅当使用数组索引操作（eg. dataset[0:10]）
#     # 或类方法.value（eg. dataset.value() or dataset.[()]）时数据被读入内存中
#     #a = np.random.rand(100, image_all.shape[0], image_all.shape[1]).astype('float32')
#     imgpathf = 'D:\data\mouse1s-2\mouse1s-saxs_'
#     for i in range(3, 593):
#         print(i)
#         imgpath = imgpathf + (5 - len(str(i))) * '0' + str(i) + '.tif'
#         img=Image.open(imgpath, mode='r')
#         img_array = np.array(img)
#         image_all = np.dstack((image_all, img_array))
#     # 调整数据预留存储空间（可以一次性调大些）
#     dataset.resize([times * 100 + 100, 1000, 1000])
#     # 数据被读入内存
#     dataset[times * 100:times * 100 + 100] = a
#     # print(sys.getsizeof(h5f))
#     h5f.close()
#
#
# def load_h5():
#     h5f = h5py.File('data.h5', 'r')
#     data = h5f['data'][0:10]
#     # print(data)
#
#
# if __name__ == '__main__':
#     save_h5(0)
#     # for i in range(20):
#     #     save_h5(i)
#     # 部分数据导入内存
#     # load_h5()