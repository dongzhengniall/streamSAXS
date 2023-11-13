import fabio
import h5py
from filetype import filetype
# from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
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
        kind = filetype.guess(file_name)
        if kind is None:
            if len(file_name) > 5 and ".poni" == file_name[-5:]:
                integrator = bf.detectorCalibrationPyfai(file_name)
                return integrator
            else:
                print('Cannot guess file type!')
                return None
        else:
            if kind.extension == "tif":
                tiff_image = None
                try:
                    tiff_image = fabio.open(file_name).data.astype("float32")
                except:
                    print("load tiff file false!")
                return tiff_image
