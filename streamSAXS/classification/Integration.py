# -*- coding: utf-8 -*-
"""
@author: WJY
"""

# lib for framework
from xrd.util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# lib for function
import base_function as bf

#%%
#------------------------------------------------------------------------------
class Integrate2D(ProcessingFunction):
    
    function_text = "Integration 2D"
    function_tip = "2Dimage --> x:q(nm^-1,A^-1)/2theta(degree)/r(mm); y:chi(degree/rad); z:I. This operation can be used firstly to chooose 1D integration range."
    
    def __init__(self):
        super().__init__()
        self._params_dict["npt_radial"] = {"type": "int", "value": None, "text": "Number of radial points"}
        self._params_dict["radial_unit"] = {"type": "enum", "value": Integrate2D_Unit.unit1, "text": "Radial Range Unit"}
        self._params_dict["radial_range"] = {"type": "tuple_float", "value": None, "text": "Radial Range",
                                             "tip":"(Inner Limit,Outer Limit). Unit is same as 'Radial Range Unit'.If not provided, range is simply (min, max)."}
        self._params_dict["npt_azimuth"] = {"type": "int", "value": 360, "text": "Number of azimuthal points",
                                            'tip': 'Too few points may lead to huge rounding errors.'}
        self._params_dict["azimuth_range"] = {"type": "tuple_float", "value": None, "text": "Azimuth Range",
                                             "tip":"(Inner Limit,Outer Limit) in degree. If not provided, range is simply (min, max)."}
        self._params_dict["polarization_factor"] = {"type": "float", "value": None, "text": "Polarization Factor",
                                                    "tip":"-1 (vertical) ~ +1 (horizontal). Default[None] is no correction, 0 for circular polarization or random."}

        
    def run_function(self, data,objectset):
        self.param_validation()
        # self.isData2D()
        
        
        # radial unit 
        if self.get_param_value("radial_unit")==Integrate2D_Unit.unit1: 
            radialUnit='q_nm^-1'
        elif self.get_param_value("radial_unit")==Integrate2D_Unit.unit2:              
            radialUnit='q_A^-1'
        elif self.get_param_value("radial_unit")==Integrate2D_Unit.unit3: 
            radialUnit='2th_deg'
        elif self.get_param_value("radial_unit")==Integrate2D_Unit.unit4: 
            radialUnit='2th_rad'
        elif self.get_param_value("radial_unit")==Integrate2D_Unit.unit5: 
            radialUnit='r_mm'
        
        if 'mask' in data:
            mask=data['mask']
        else:
            mask=None
            
        result2d = bf.integrate2D(objectset['integrator'],data['image'], mask,
                                  npt_rad=self.get_param_value("npt_radial"),unit=radialUnit,
                                  radial_range=self.get_param_value("radial_range"),
                                  npt_azim=self.get_param_value("npt_azimuth"),
                                  azimuth_range=self.get_param_value("azimuth_range"),
                                  polarization_factor=self.get_param_value("polarization_factor"))

        
        return {'data': {'x': result2d.radial, 'y': result2d.azimuthal,'z':result2d.intensity},
                'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'chi (degree)'},
                'plot':{'data':{'x': result2d.radial, 'y': result2d.azimuthal,'z':result2d.intensity},
                        'type':'2DXY',
                        'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'chi (degree)'}}
                }
            
    def param_validation(self):
        if self.get_param_value("npt_radial") is None:
            raise ValueError("The number of radial points must be input")
        if self.get_param_value("npt_azimuth") is None:
            raise ValueError("The number of Azimuthal points must be input")

   
@unique    
class Integrate2D_Unit(Enum):
    unit1 = 'q (nm^-1)'
    unit2 = 'q (A^-1)'
    unit3 = '2'+chr(952)+' (degree)'
    unit4 = '2'+chr(952)+' (rad)'
    unit5 = 'r (mm)'
    
#------------------------------------------------------------------------------
class IntegrateAzimuthal(ProcessingFunction):
    function_text = "Azimuthal Integration"
    function_tip = "2D image --> 1D curve I~q(nm^-1,A^-1)/2theta(degree)/r(mm)"

    def __init__(self):
        super().__init__()
        self._params_dict["npt"] = {"type": "int", "value": None, "text": "Number of output points"}
        self._params_dict["out_unit"] = {"type": "enum", "value": IntegrateAzimuthal_Unit.unit1, "text": "Output Unit"}
        self._params_dict["radial_range"] = {"type": "tuple_float", "value": None, "text": "Radial Range",
                                             "tip":"(Inner Limit,Outer Limit).Unit is same as 'Output Unit'.If not provided, range is simply (min, max)."}
        self._params_dict["azimuth_range"] = {"type": "tuple_float", "value": (-180,180), "text": "Azimuth Range",
                                              "tip":"(Lower angle, upper angle) in degree. Angle must between -180 and 180. 0 degree is in the direction of the left horizontal line. [Clockwise]. If not provided, range is simply (min, max)."}        
        self._params_dict["polarization_factor"] = {"type": "float", "value": None, "text": "Polarization Factor",
                                                    "tip":"-1 (vertical) ~ +1 (horizontal). Default[None] is no correction, 0 for circular polarization or random."}

    def run_function(self, data,objectset):
        self.param_validation()
        # self.isData2D()
        
        if self.get_param_value("outUnit")==IntegrateAzimuthal_Unit.unit5:
            unit='r_mm'
        if self.get_param_value("outUnit")==IntegrateAzimuthal_Unit.unit4:
            unit='2th_rad'
        elif self.get_param_value("outUnit")==IntegrateAzimuthal_Unit.unit3:
            unit='2th_deg'
        elif self.get_param_value("outUnit")==IntegrateAzimuthal_Unit.unit2:            
            unit='q_A^-1'
        elif self.get_param_value("outUnit")==IntegrateAzimuthal_Unit.unit1:            
            unit='q_nm^-1'

        if 'mask' in data:
            mask=data['mask']
        else:
            mask=None        
    
        result1d=bf.integrateAzimuthal(objectset['integrator'], data['image'], mask,
                                       npt=self.get_param_value("npt"), unit=unit, 
                                       radial_range=self.get_param_value("radial_range"),
                                       azimuth_range=self.get_param_value("azimuth_range"),
                                       polarization_factor=self.get_param_value("polarization_factor"),
                                       )

        return {'data': {'x': result1d.radial, 'y': result1d.intensity},
                'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'},
                'plot':{'data':{'x': result1d.radial, 'y': result1d.intensity},
                        'type':'1DP',
                        'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'}}
                }

    def param_validation(self):
        if self.get_param_value("npt") is None:
            raise ValueError("The number of output points must be input")
            
@unique
class IntegrateAzimuthal_Unit(Enum):
    unit1 = 'q (nm^-1)'
    unit2 = 'q (A^-1)'
    unit3 = '2'+chr(952)+' (degree)'
    unit4 = '2'+chr(952)+' (rad)'
    unit5 = 'r (mm)'

#------------------------------------------------------------------------------
class IntegrateRadial(ProcessingFunction):
    function_text = "Radial Integration"
    function_tip = "2D image --> 1D curve I~chi(degree/rad)"
    
    def __init__(self):
        super().__init__()
        self._params_dict["npt"] = {"type": "int", "value": None, "text": "Number of output points"}
        self._params_dict["out_unit"] = {"type": "enum", "value": IntegrateRadial_OutUnit.unit1, "text": "Output Unit"}
        self._params_dict["azimuth_range"] = {"type": "tuple_float", "value": None, "text": "Azimuth Range",
                                              "tip":"(Lower angle, upper angle) in degree. Angle must between -180 and 180. 0 degree is in the direction of the left horizontal line. [Clockwise]. If not provided, range is simply (min, max)."}        
        self._params_dict["npt_radial"] = {"type": "int", "value": None, "text": "Number of radial points",'tip': 'Too few points may lead to huge rounding errors.'}
        self._params_dict["radial_unit"] = {"type": "enum", "value": IntegrateRadial_RadialUnit.unit1, "text": "Radial Range Unit"}
        self._params_dict["radial_range"] = {"type": "tuple_float", "value": None, "text": "Radial Range",
                                             "tip":"(Inner Limit,Outer Limit).Unit is same as 'Radial Range Unit'.If not provided, range is simply (min, max)."}
        self._params_dict["polarization_factor"] = {"type": "float", "value": None, "text": "Polarization Factor",
                                                    "tip":"-1 (vertical) ~ +1 (horizontal). Default[None] is no correction, 0 for circular polarization or random."}

        
    def run_function(self, data,objectset):
        self.param_validation()
        # self.isData2D()
        
        #azimuth unit
        if self.get_param_value("out_unit")==IntegrateRadial_OutUnit.unit1:
            azimuthUnit='chi_deg'
        if self.get_param_value("out_unit")==IntegrateRadial_OutUnit.unit2:
            azimuthUnit='chi_rad'
        
        # radial unit 
        if self.get_param_value("radial_unit")==IntegrateRadial_RadialUnit.unit1: 
            radialUnit='q_nm^-1'
        elif self.get_param_value("radial_unit")==IntegrateRadial_RadialUnit.unit2:              
            radialUnit='q_A^-1'
        elif self.get_param_value("radial_unit")==IntegrateRadial_RadialUnit.unit3: 
            radialUnit='2th_deg'
        elif self.get_param_value("radial_unit")==IntegrateRadial_RadialUnit.unit4: 
            radialUnit='2th_rad'
        elif self.get_param_value("radial_unit")==IntegrateRadial_RadialUnit.unit5: 
            radialUnit='r_mm'
        
        if 'mask' in data:
            mask=data['mask']
        else:
            mask=None
            
        result1d=bf.integrateRadial(objectset['integrator'], data['image'], mask,
                                    npt=self.get_param_value("npt"),npt_rad=self.get_param_value("npt_radial"),
                                    unit=azimuthUnit,azimuth_range=self.get_param_value("azimuth_range"),
                                    radial_unit=radialUnit,radial_range=self.get_param_value("radial_range"),                                                            
                                    polarization_factor=self.get_param_value("polarization_factor")
                                    )
        
        return {'data': {'x': result1d.radial, 'y': result1d.intensity},
                'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'},
                'plot':{'data':{'x': result1d.radial, 'y': result1d.intensity},
                        'type':'1DP',
                        'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'}}
                }
        
    
    def param_validation(self):
        if self.get_param_value("npt") is None:
            raise ValueError("The number of output points must be input")
        if self.get_param_value("npt_radial") is None:
            raise ValueError("The number of radial points must be input")
            

@unique    
class IntegrateRadial_OutUnit(Enum):
    unit1 = 'chi (degree)'
    unit2 = 'chi (rad)'
    
@unique    
class IntegrateRadial_RadialUnit(Enum):
    unit1 = 'q (nm^-1)'
    unit2 = 'q (A^-1)'
    unit3 = '2'+chr(952)+' (degree)'
    unit4 = '2'+chr(952)+' (rad)'
    unit5 = 'r (mm)'

#------------------------------------------------------------------------------
class IntegrateRadial_BgDel(ProcessingFunction):
    function_text = "Radial Integration & Background Deduction"
    function_tip = "2D image --> 1D curve I~chi(degree/rad)"
    
    def __init__(self):
        super().__init__()
        self._params_dict["npt"] = {"type": "int", "value": None, "text": "Number of output points"}
        self._params_dict["out_unit"] = {"type": "enum", "value": IntegrateRadial_BgDel_OutUnit.unit1, "text": "Output Unit"}
        self._params_dict["azimuth_range"] = {"type": "tuple_float", "value": None, "text": "Azimuth Range",
                                              "tip":"(Lower angle, upper angle) in degree. Angle must between -180 and 180. 0 degree is in the direction of the left horizontal line. [Clockwise]. If not provided, range is simply (min, max)."}        
        self._params_dict["npt_radial"] = {"type": "int", "value": None, "text": "Number of radial points",'tip': 'Too few points may lead to huge rounding errors.'}
        self._params_dict["radial_unit"] = {"type": "enum", "value": IntegrateRadial_BgDel_RadialUnit.unit1, "text": "Radial Range Unit"}
        self._params_dict["radial_range"] = {"type": "tuple_float", "value": None, "text": "Radial Range",
                                             "tip":"(Inner Limit,Outer Limit).Unit is same as 'Radial Range Unit'."}
        self._params_dict["polarization_factor"] = {"type": "float", "value": None, "text": "Polarization Factor",
                                                    "tip":"-1 (vertical) ~ +1 (horizontal). Default[None] is no correction, 0 for circular polarization or random."}
        self._params_dict["radial_range_low"] = {"type": "tuple_float", "value": None, "text": "Lower Range for Background",
                                                 "tip":"(Inner Limit,Outer Limit).Unit is same as 'Radial Range Unit'."}
        self._params_dict["radial_range_high"] = {"type": "tuple_float", "value": None, "text": "Higher Range for Background",
                                                  "tip":"(Inner Limit,Outer Limit).Unit is same as 'Radial Range Unit'."}

        
    def run_function(self, data,objectset):
        self.param_validation()
        # self.isData2D()
        
        #azimuth unit
        if self.get_param_value("out_unit")==IntegrateRadial_BgDel_OutUnit.unit1:
            azimuthUnit='chi_deg'
        if self.get_param_value("out_unit")==IntegrateRadial_BgDel_OutUnit.unit2:
            azimuthUnit='chi_rad'
        
        # radial unit 
        if self.get_param_value("radial_unit")==IntegrateRadial_BgDel_RadialUnit.unit1: 
            radialUnit='q_nm^-1'
        elif self.get_param_value("radial_unit")==IntegrateRadial_BgDel_RadialUnit.unit2:              
            radialUnit='q_A^-1'
        elif self.get_param_value("radial_unit")==IntegrateRadial_BgDel_RadialUnit.unit3: 
            radialUnit='2th_deg'
        elif self.get_param_value("radial_unit")==IntegrateRadial_BgDel_RadialUnit.unit4: 
            radialUnit='2th_rad'
        elif self.get_param_value("radial_unit")==IntegrateRadial_BgDel_RadialUnit.unit5: 
            radialUnit='r_mm'
        
        if 'mask' in data:
            mask=data['mask']
        else:
            mask=None
            
        result1d=bf.integrateRadial(objectset['integrator'], data['image'], mask,
                                    npt=self.get_param_value("npt"),npt_rad=self.get_param_value("npt_radial"),
                                    unit=azimuthUnit,azimuth_range=self.get_param_value("azimuth_range"),
                                    radial_unit=radialUnit,radial_range=self.get_param_value("radial_range"),                                                            
                                    polarization_factor=self.get_param_value("polarization_factor")
                                    )
        resultBgLow=bf.integrateRadial(objectset['integrator'], data['image'], mask,
                                       npt=self.get_param_value("npt"),npt_rad=self.get_param_value("npt_radial"),
                                       unit=azimuthUnit,azimuth_range=self.get_param_value("azimuth_range"),
                                       radial_unit=radialUnit,radial_range=self.get_param_value("radial_range_low"),                                                            
                                       polarization_factor=self.get_param_value("polarization_factor")
                                       )
        resultBgHigh=bf.integrateRadial(objectset['integrator'], data['image'], mask,
                                       npt=self.get_param_value("npt"),npt_rad=self.get_param_value("npt_radial"),
                                       unit=azimuthUnit,azimuth_range=self.get_param_value("azimuth_range"),
                                       radial_unit=radialUnit,radial_range=self.get_param_value("radial_range_high"),                                                            
                                       polarization_factor=self.get_param_value("polarization_factor")
                                       )
        intensity=result1d.intensity-(resultBgLow.intensity+resultBgHigh.intensity)/2
        
        return {'data': {'x': result1d.radial, 'y': intensity},
                'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'},
                'plot':{'data':{'x': result1d.radial, 'y': intensity},
                        'type':'1DP',
                        'label':{'xlabel':self.get_param_value("outUnit"),'ylabel':'Intensity'}}
                }
        
    
    def param_validation(self):
        if self.get_param_value("npt") is None:
            raise ValueError("The number of output points must be input")
        if self.get_param_value("npt_radial") is None:
            raise ValueError("The number of radial points must be input")
        if self.get_param_value("radial_range") is None:
            raise ValueError("'Radial Range' must be input")
        if self.get_param_value("radial_range_low") is None:
            raise ValueError("'Lower Range for Background' must be input")
        if self.get_param_value("radial_range_high") is None:
            raise ValueError("'Higher Range for Background' must be input")
            

@unique    
class IntegrateRadial_BgDel_OutUnit(Enum):
    unit1 = 'chi (degree)'
    unit2 = 'chi (rad)'
    
@unique    
class IntegrateRadial_BgDel_RadialUnit(Enum):
    unit1 = 'q (nm^-1)'
    unit2 = 'q (A^-1)'
    unit3 = '2'+chr(952)+' (degree)'
    unit4 = '2'+chr(952)+' (rad)'
    unit5 = 'r (mm)'