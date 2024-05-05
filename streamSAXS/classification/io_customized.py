import fabio
import h5py
#from filetype import filetype
from PIL import Image
import numpy as np

import base_function as bf


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


class IoFile(object):
    # load tiff and other file in memory
    @staticmethod
    def Load_File_Data(file_name):
        
        data=None
        
        if file_name.endswith('.poni'):
            try:
                data = bf.detectorCalibrationPyfai(file_name)
                # data --> integrator
            except:
                print("Load poni file false!")

        elif file_name.endswith('.tif') or file_name.endswith('.tiff'):
            try:
                data=Image.open(file_name, mode='r')
                data = np.array(data).astype(np.float32)
            except:
                print("Load tif or tiff file false!")
        elif file_name.endswith('.edf'):
            try:
                data=fabio.open(file_name).data.astype(np.float32)
            except:
                print("Load edf file false!")
                
        else:
            print('File type is not supproted!')

        return data
            
            