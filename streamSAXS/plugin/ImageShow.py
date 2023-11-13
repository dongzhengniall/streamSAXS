

from util.processing_sequence import ProcessingFunction
from enum import unique, Enum
import numpy as np

class ImageShown2D(ProcessingFunction):
    """
    DESCRIPTION:Showing image
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "2DImage"
    function_tip = "Load Porjection, Falt and Dark images from file"

    def __init__(self):
        super().__init__()
        self._params_dict["slicesRange"] = {"type": "tuple_int","value": None,"text": "Interested Range"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit2, "text": "Interest Data"}
        self._params_dict["Range"] = {"type": "tuple_int", "value": None, "text": "MAXRange"}
    def run_function(self, data):
        self.param_validation()
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Sinogram'
        elif self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Flat'
        elif self.get_param_value("data_interest") == Interest_Data_Type.unit4:
            unit = 'Dark'
        elif self.get_param_value("data_interest") == Interest_Data_Type.unit5:
            unit = 'Recdata'
        try:
            if unit !='Sinogram':
                nx,ny,nz=np.shape(data[unit])
                self.set_param('Range', (0,nx))
                if self.get_param_value("slicesRange") is None or self.get_param_value("slicesRange")[1]>nx:
                    self.set_param('slicesRange', (0,nx))

                return {'data': data,
                        "plot": {"type": "2DV",
                                 "data": data[unit][self.get_param_value("slicesRange")[0]:self.get_param_value("slicesRange")[1],:,:],
                                 "title": unit+':'+str(self.get_param_value("slicesRange"))}}

            if unit =='Sinogram':
                Sinogram = data["Proj"].transpose(1, 0, 2)
                nx,ny,nz=np.shape(Sinogram)
                self.set_param('Range', (0, nx))
                if self.get_param_value("slicesRange") is None or self.get_param_value("slicesRange")[1] > nx:
                    self.set_param('slicesRange', (0, nx))

                return {'data': data,
                        "plot": {"type": "2DV",
                                 "data": Sinogram[self.get_param_value("slicesRange")[0]:self.get_param_value("slicesRange")[1],:,:],
                                 "title": unit+':'+str(self.get_param_value("slices"))}}
        except :
            raise ValueError("Please check "+ unit +"data !!")


@unique
class Interest_Data_Type(Enum):
    unit1 = 'Projection'
    unit2 = 'Sinogram'
    unit3 = 'Flat'
    unit4 = 'Dark'
    unit5 = 'Reconstruction'

class ImageShown3D(ProcessingFunction):
    """
    DESCRIPTION:Showing image
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "3DImage"
    function_tip = "Showning image"

    def __init__(self):
        super().__init__()
        self._params_dict["slicesRange"] = {"type": "tuple_int","value": None,"text": "Slices Range"}
        self._params_dict["ROIRangeY"] = {"type": "tuple_int", "value": None, "text": "Vertical ROI Range"}
        self._params_dict["ROIRangeZ"] = {"type": "tuple_int", "value": None, "text": "Horizontal ROI Range"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit1, "text": "Interest Data"}
        self._params_dict["ShapeX"] = {"type": "int", "value": None, "text": "Number of Slices"}
        self._params_dict["ShapeYZ"] = {"type": "tuple_int", "value": None, "text": "Shape of slice"}

    def run_function(self, data):
        self.param_validation()
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Recdata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = data["Threshold_data"]["data"]
        elif self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = data["Filter_data"]['data']

        try:
            nx,ny,nz=np.shape(data[unit])
            self.set_param('ShapeX', nx)
            self.set_param('ShapeYZ', (ny,nz))

            if self.get_param_value("slicesRange") is None or self.get_param_value("slicesRange")[1]>nx:
                self.set_param('slicesRange', (0,nx))
            if self.get_param_value("ROIRangeY") is None or self.get_param_value("ROIRangeY")[1]>ny:
                self.set_param('ROIRangeY', (0,ny))
            if self.get_param_value("ROIRangeZ") is None or self.get_param_value("ROIRangeZ")[1]>nz:
                self.set_param('ROIRangeZ', (0,nz))

            return {'data': data,
                    "plot": {"type": "3DVS",
                             "data": data[unit][self.get_param_value("slicesRange")[0]:self.get_param_value("slicesRange")[1],
                                                self.get_param_value("ROIRangeY")[0]:self.get_param_value("ROIRangeY")[1],
                                                self.get_param_value("ROIRangeZ")[0]:self.get_param_value("ROIRangeZ")[1]],
                             "title": unit}}

        except :
            raise ValueError("Please check "+ unit +"data !!")








@unique
class Interest_Data_Type3D(Enum):
    unit1 = 'Reconstruction'
    unit2 = 'Filtered Reconstruction'
    unit3 = 'Segmentation'

