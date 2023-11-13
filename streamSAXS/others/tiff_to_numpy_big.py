import numpy as np
from PIL import Image
import h5py
import os


def load_tiff(imgpath):
    img = Image.open(imgpath, mode='r')
    image = np.array(img)
    return image


def load_h5():
    h5f = h5py.File('data.h5', 'r')
    data = h5f['data'][0:10]
    # print(data)


def save_bunch_tiff_to_h5(data_range, bunch, input_path_prefix, num, output_path, dataset_name):
    """
    :param image_range: start number and end number of image name
    :param bunch: data size of each save operation
    :param input_path_prefix: the prefix of input path
    :param num: the number of digits in input path
    :param output_path:save path of h5
    :param dataset_name:the dataset name in h5
    :param type:the type of data(image, txt_int, txt_float32)
    """

    def init_dataset(path, name, shape, type='float32'):
        if os.path.exists(output_path):
            h5f = h5py.File(path, 'a')
        else:
            h5f = h5py.File(path, 'w')
        h5f.create_dataset(name, shape, maxshape=(None, shape[1], shape[2]), dtype=type)
        h5f.close()

    def save_data_in_dataset(path, name, dataset_start, shape, data):
        h5f = h5py.File(path, 'a')
        dataset = h5f[name]
        dataset.resize([dataset_start + shape[0], shape[1], shape[2]])
        dataset[dataset_start:dataset_start + shape[0]] = data
        h5f.close()

    length = data_range[1] - data_range[0] + 1
    imgpath = input_path_prefix + (num - len(str(data_range[0]))) * '0' + str(data_range[0]) + '.tif'
    image = load_tiff(imgpath=imgpath)
    shape = (length, image.shape[0], image.shape[1])
    init_dataset(path=output_path, name=dataset_name, shape=shape)
    m = length // bunch
    r = length % bunch
    for i in range(m + 1):
        n = bunch if i < m else r
        image_bunch = np.full((n, shape[1], shape[2]), float('nan'))
        for j in range(n):
            path = input_path_prefix + (5 - len(str(i * bunch + j + data_range[0]))) * '0' + str(
                i * bunch + j + data_range[0]) + '.tif'
            print(path)
            image = load_tiff(imgpath=path)
            image_bunch[j:] = image

        save_data_in_dataset(path=output_path, name=dataset_name, dataset_start=i * bunch,
                             shape=(n, shape[1], shape[2]), data=image_bunch)


def save_txt_to_h5(input_path, output_path, dataset_name):
    f = open(input_path, encoding='gbk')
    txt = []
    for line in f:
        txt.append(float(line.strip()))
    data = np.array(txt)
    if os.path.exists(output_path):
        with h5py.File(output_path, 'a') as hf:
            hf.create_dataset(dataset_name, data=data)
    else:
        with h5py.File(output_path, 'w') as hf:
            hf.create_dataset(dataset_name, data=data)
    print(txt)


if __name__ == '__main__':
    output_path = 'D:\data\mouse1s-saxs_bg.h5'
    # bunch tiff image
    path_prefix = 'D:\\data\\pyfai\\bg_'
    dataset_name = "data"
    type = "image"
    start_end = (1, 1)
    bunch = 10
    num = 5
    save_bunch_tiff_to_h5(data_range=start_end, bunch=bunch, input_path_prefix=path_prefix, num=num, output_path=output_path,
                    dataset_name=dataset_name)
    # i0
    input_path = 'D:\\data\\pyfai\\bg-i0.txt'
    dataset_name = "i0"
    save_txt_to_h5(input_path, output_path, dataset_name)
