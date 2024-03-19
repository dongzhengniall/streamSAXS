from util.processing_sequence import ProcessingFunction
from enum import unique, Enum
import numpy as np
import plugin.CT_Process_Function as CTF
from util.io import OutCTData
import tifffile

class GenSino(ProcessingFunction):
    """
    DESCRIPTION:Generation sinogram
    Parameters:
        data_source_file : dist
    Returns:
    """
    function_text = "Sinogram"
    function_tip = " sinogram."
    def __init__(self):
        super().__init__()

        self._params_dict["X"] = {"type": "int", "value": 91, "text": "X"}
        self._params_dict["Y"] = {"type": "int", "value": 61, "text": "Y"}
        self._params_dict["sinoLable"] = {"type": "enum", "value": Sino_Type.unit4,
                                              "text": "Algorithm"}

    def run_function(self, data):
        data['sino'] = {}
        if self.get_param_value("sinoLable") == Sino_Type.unit1:
            unit = 'peak_center'
        if self.get_param_value("sinoLable") == Sino_Type.unit2:
            unit = 'area'
        if self.get_param_value("sinoLable") == Sino_Type.unit3:
            unit = 'fwhm'
        if self.get_param_value("sinoLable") == Sino_Type.unit4:
            unit = 'PeakInt'

        if unit == 'PeakInt':
            sinodata = data['PeakInt']
        else :
            sinodata = data['peakfit'][unit]

        if 'data' in data['sino'].keys():

            sino, label = CTF.GenSino(X=self.get_param_value("X"), Y=self.get_param_value("Y"),
                                      data=sinodata, sino = data['sino']['data'])
        else:
            print('hhhh')
            sino, label = CTF.GenSino(X=self.get_param_value("X"), Y=self.get_param_value("Y"),
                                      data=sinodata ,sino =None)

        data['sino']['data'] = sino
        data['sino']['label'] = label
        print(sino)
        return {'data': data,
                "plot": {"type": "2DV",
                         "data": sino,
                         "title": 'Sino'}}


@unique
class Sino_Type(Enum):
    unit1 = 'PeakPos'
    unit2 = 'PeakArea'
    unit3 = 'PeakFWHM'
    unit4 = 'ROIPeakIntensity'





class Recon2D(ProcessingFunction):
    """
    DESCRIPTION:Data Reconstruction
    Parameters:
        data_source_file : dist
    Returns:
    """
    function_text = "Reconstruction"
    function_tip = " Reconstruction."

    def __init__(self):
        super().__init__()
        # self._params_dict["DataSave"] = {"type": "ct_save",
        #                                  "value":'E:/ProcessingSoft/data/hetao/tmp11',
        #                                  "text": "Save Slices",
        #                                  "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["RecAlgorithm"] = {"type": "enum", "value": Algorithm_Type.unit1,
                                              "text": "Algorithm"}
        self._params_dict["Iter"] = {"type": "int", "value": 1, "text": "Number of Iteration"}
        self._params_dict["AngleScale"] = {"type": "float", "value": 180, "text": "Angle Scale"}
        self._params_dict["BeamCenter"] = {"type": "float", "value": 42, "text": "Rotation Axis"}
        self._params_dict["AxisTilt"] = {"type": "float", "value": 0, "text": "Tilt of ROC"}

        #self._params_dict["SliceRange"] = {"type": "tuple_int", "value": (250,255), "text": "Slice Range"}

        #self._params_dict["mask"] = {"type": "bool", "value": True, "text": " Mask"}
        
    def run_function(self, data):
        '''
        if 'sino' not in data:
            pass
            return {"data": data}
        else:
            sino = data['sino']['data']
            if data['sino']['label']  == False:
                pass
                return {"data": data}
            else:

                if self.get_param_value("RecAlgorithm") == Algorithm_Type.unit1:
                    unit = 'FBP'
                if self.get_param_value("RecAlgorithm") == Algorithm_Type.unit2:
                    unit = 'FP'
                elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit3:
                    unit = 'BP'
                elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit4:
                    unit = 'SIRT'
                elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit5:
                    unit = 'SART'
                elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit6:
                    unit = 'ART'
                elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit7:
                    unit = 'CGLS'

                nx,ny=np.shape(sino)
                if self.get_param_value("BeamCenter") is None:
                    self.set_param("BeamCenter",int(ny / 2))

                REC_F = CTF.Recon_parallel(RAlgorithm=unit, Iter=self.get_param_value("Iter"),
                                           AngleScale=np.deg2rad(self.get_param_value("Iter"))),
                data["Recdata"] = REC_F.Recon_single_sinogram(sino, ROC=self.get_param_value("BeamCenter"))

                return {"data": data,
                        "plot": {"type": "3DVS", "data": data["Recdata"]},
                        "title":"Reconstruction"}
        '''

        if self.get_param_value("RecAlgorithm") == Algorithm_Type.unit1:
            unit = 'FBP'
        if self.get_param_value("RecAlgorithm") == Algorithm_Type.unit2:
            unit = 'FP'
        elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit3:
            unit = 'BP'
        elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit4:
            unit = 'SIRT'
        elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit5:
            unit = 'SART'
        elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit6:
            unit = 'ART'
        elif self.get_param_value("RecAlgorithm") == Algorithm_Type.unit7:
            unit = 'CGLS'
        sino =data['image']

        print(np.shape(sino))
        nx, ny = np.shape(sino)
        #print(sino)

        sino = np.flipud(sino)
        if self.get_param_value("BeamCenter") is None:
            self.set_param("BeamCenter", int(ny / 2))

        # data["Recdata"] = CTF.Recon_parallel_Tomopy(sino, theta = np.deg2rad(self.get_param_value("AngleScale")) ,
        #                                             center= self.get_param_value("BeamCenter"), algorithm=unit, num_iter = self.get_param_value("Iter"))
        #print(unit,)
        REC_F = CTF.Recon_parallel(RAlgorithm=unit, Iter=self.get_param_value("Iter"),
                                   AngleScale=np.deg2rad(self.get_param_value("AngleScale")))

        data["Recdata"] = REC_F.Recon_single_sinogram(sino, ROC=self.get_param_value("BeamCenter"))

        return {"data": data,
                "plot": {"type": "2DV", "data": data["Recdata"]},
                "title": "Reconstruction"}

    def param_validation(self):
        pass

@unique
class Algorithm_Type(Enum):
    unit1 = 'FBP'
    unit2 = 'FP'
    unit3 = 'BP'
    unit4 = 'SIRT'
    unit5 = 'SART'
    unit6 = 'ART'
    unit7 = 'CGLS'
