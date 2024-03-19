import os.path

import numpy as np
from PIL import Image
import h5py,tifffile
from filetype import filetype
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator


class IoHdf5(object):
    # load h5 file dataset in memory
    @staticmethod
    def Load_H5_Data(file_name, file_dataset):
        def get_data_in_h5_file(f, h5_dataset_dict):
            for k in f.keys():
                d = f[k]
                if isinstance(d, h5py.Group):
                    get_data_in_h5_file(d, h5_dataset_dict)
                elif isinstance(d, h5py.Dataset):
                    h5_dataset_dict[d.name] = {}
                    h5_dataset_dict[d.name]["dataset"] = d
                    h5_dataset_dict[d.name]["size"] = d.size
                else:
                    print('??->', d, 'Unkown Object!')
            return h5_dataset_dict

        file = h5py.File(file_name, 'r')
        dataset = get_data_in_h5_file(file, {})
        select_dataset = file_dataset
        data = dataset[select_dataset]["dataset"][:]
        file.close()
        data = data.squeeze()
        return data

    @staticmethod
    def Save_H5_data(file_name, dataset_name, dataset_value, data_set_type=None, data_length=None, end=None,save_length=None):
        if os.path.exists(file_name):
            f = h5py.File(file_name, 'a')
        else:
            f = h5py.File(file_name, 'w')
        if dataset_name not in f:
            if data_set_type == "attri":
                dataset = f.create_dataset(dataset_name, [data_length], dtype='S10',chunks=True)
            elif len(dataset_value.shape) == 2:
                dataset = f.create_dataset(dataset_name, [data_length, dataset_value.shape[1]],
                                           chunks=True)
            else:
                dataset = f.create_dataset(dataset_name, [data_length, dataset_value.shape[1], dataset_value.shape[2]],
                                           chunks=True)
        dataset = f[dataset_name]
        if data_set_type == "attri":
            dataset[end-save_length+1:end+1] = dataset_value
        else:
            dataset[end-save_length+1:end+1] = dataset_value
        f.close()


class IoTiff(object):
    # load tiff file dataset in memory
    @staticmethod
    def Load_All_Data(file_names):
        tiff_images = []#################
        try:
            for file_name in file_names:
                kind = filetype.guess(file_name)
                if kind.extension == "tif":
                    tiff_image = Image.open(file_name)
                    tiff_image = np.array(tiff_image)#.astype("float32")
                    tiff_images.append(tiff_image)###############
                else:
                    print(file_name + " tiff file false!")
                    return None
            return np.array(tiff_images)
        except:
            print("load tiff file false!")
            return None




class IoFile(object):
    # load tiff and other file in memory
    @staticmethod
    def Load_File_Data(file_name):
        kind = filetype.guess(file_name)
        if kind is None:
            if len(file_name) > 5 and ".poni" == file_name[-5:]:
                integrator = AzimuthalIntegrator.sload(file_name)
                return integrator
            else:
                print('Cannot guess file type!')
                return None
        else:
            if kind.extension == "tif":
                tiff_image = None
                try:
                    tiff_image = Image.open(file_name)
                    tiff_image = np.array(tiff_image).astype("float32")
                except:
                    print("load tiff file false!")
                return tiff_image




class OutCTData(object):
    @staticmethod
    def Save_Tiff_data(Path, data, SlicesStart, ROCRange=None, image_name=None):
        if isinstance(data, np.float64):
            data=data.astype('float32')
        for i in range(data.shape[0]):
            if ROCRange is None:
                tifffile.imwrite(Path + '\\' + image_name+"_"+str(SlicesStart+i).zfill(5)+'.tiff',
                                data[i,:,:])
            else:
                ROCs = np.arange(ROCRange[0], ROCRange[1], ROCRange[2])
                tifffile.imwrite(Path + '\\' + "Slices_" + str(SlicesStart).zfill(4)+'_' + image_name + '_' +str(ROCs[i]).zfill(5) + '.tiff',
                                data[i, :, :].astype('float32'))

    @staticmethod
    def Save_H5_data_Recon(Path, data, RecParas):
        file_name=Path + '\\' + 'Recon.h5'
        with  h5py.File(file_name, 'w') as f:
            f['data/slices']=data
            for key in RecParas.keys():
                f['RecParas/'+key] = RecParas[key]

    def Save_H5_data_Filter(Path, data ,File_name=None):
        file_name=Path + '\\' + File_name+'.h5'
        with  h5py.File(file_name, 'w') as f:
            for key in data.keys():
                f[key] = data[key]




