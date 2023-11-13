# -*- coding: utf-8 -*-
"""
@author: WJY
@20220724
"""
import base_function as bf
from io_customized import IoFile

import time

import os
from natsort import natsorted

import numpy as np

import matplotlib.pyplot as plt

import fabio
# import tifffile
from pyFAI.ext.reconstruct import reconstruct
#%%
def creatPath(filePath):
    
    pathList=os.listdir(filePath)
    for i,j in enumerate(pathList):
        pathList[i]=os.path.join(filePath,pathList[i])
    pathList=natsorted(pathList)
    
    return pathList


#-------------------------test for WAXS I~q------------------------------------
#%%
pathList=creatPath(r'E:\data\test\01\data')

resList=[]
fwhmList=[]
#file=r'E:\data\test\01\telson-calib-from-pyFAI.poni'
cali_file=r'E:\data\test\01\telson-calib-from-pyFAI-02.poni'
integrator=IoFile.Load_File_Data(cali_file)
mask_file=r'E:\data\test\01\mask.tif'
mask = IoFile.Load_File_Data(mask_file)

#%%
start=time.time()    
for path in pathList:


    data=IoFile.Load_File_Data(path)
    
    
    result1d=bf.integrateAzimuthal(integrator,data,npt=1000,unit='q_nm^-1',
                                   radial_range=(5,30),azimuth_range=(-180,180),
                                   polarization_factor=0.99,mask=mask)
    
    # result=np.vstack((result1d.radial,result1d.intensity))
    # resList.append(result)
    
    x=result1d.radial
    y=result1d.intensity
    x_range=(520,600)
    x=x[x_range[0]:x_range[1]+1] #attention the last value shoule +1
    y=y[x_range[0]:x_range[1]+1]
    
    resultFit,yfit=bf.singlePeakFit(x,y,peak_type="Vogit+LinearBg")
    fwhmList.append(resultFit['peakCenter'])

end=time.time()
print(end-start)
    
#%%        
# plt.figure(figsize=(6,4))
plt.figure()
for i,j in enumerate(resList):
    plt.plot(j[0,:],j[1,:]+i*500)

plt.legend()

#%%
plt.figure()
fwhm=np.array(fwhmList)
fwhm.reshape()


#-----------------------test for SAXS I~chi and guinier------------------------
#%%
'''
# creat background tif, value=0
data=IoFile.Load_File_Data(r'E:\data\test\mouse1s-saxs_00150.tif')
bg=np.zeros_like(data)
imageio.imsave(r'E:\data\test\bg.tif', bg)
'''

#%%

pathList=creatPath(r'E:\data\test\02\SAXS')


bg_file=r'E:\data\test\02\bg.tif'
bg=IoFile.Load_File_Data(bg_file)
ic_bg=1
noise=0
coeff_sample=1
coeff_bg=1
ic_sample_all=np.loadtxt(r'E:\data\test\02\i0.txt')

#%%

integrator=bf.detectorCalibrationFit2d(1.2461E-10, 3100, 843, 1214, 172, 172, 0, 0)
mask=bf.thresholdMask2D(np.flipud(IoFile.Load_File_Data(pathList[0])),0,80000)

#%%
#path=pathList[9]
correction=True
peakCenter=[]
fwhm=[]
rg=[]
t_parameter=[]

start=time.time() 

for i,path in enumerate(pathList):
    data=IoFile.Load_File_Data(path)
    data[data>1e8]=-1 #attention！
    
    ic_sample=ic_sample_all[i]
    data=bf.normalizeSAXS(data, ic_sample, coeff_sample, bg, ic_bg, coeff_bg, noise)
    data=bf.imageFlip(data)
    
    #result2d=bf.integrate2D(integrator, data, npt_rad=1000,mask=mask)    
    
    '''
    result1d_rad=bf.integrateRadial(integrator, data, npt=100, npt_rad=100,radial_range=(0.6,0.75),azimuth_range=(50,125),unit='chi_rad',mask=mask)#,azimuth_range=(50,125)
    #Attention: azimuth_range is always in degree unit, unit-->only plot
    
    result1d_rad_bgLow=bf.integrateRadial(integrator, data, npt=100, npt_rad=100,radial_range=(0.55,0.6),azimuth_range=(50,125),unit='chi_rad',mask=mask)#,azimuth_range=(50,125)

    result1d_rad_bgHigh=bf.integrateRadial(integrator, data, npt=100, npt_rad=100,radial_range=(0.75,0.8),azimuth_range=(50,125),unit='chi_rad',mask=mask)#,azimuth_range=(50,125)
    
    x=result1d_rad.radial
    y=result1d_rad.intensity
    
    y_low=result1d_rad_bgLow.intensity
    y_high=result1d_rad_bgHigh.intensity
    
    y_sub=y-(y_low+y_high)/2


    resultFit,yfit=bf.singlePeakFit(x,y_sub,autoFit=False,peak_type="Gaussian+LinearBg",peak_center=1.5,fwhm=0.6,area=0.6*175000,fixedSlope=True,fixedIntercept=True)
    peakCenter.append(resultFit['peak_center'])
    fwhm.append(resultFit['fwhm'])
    
    '''
    
    #I~chi
    result1d_rad=bf.integrateRadial(integrator, data, npt=100, npt_rad=100,radial_range=(0.15,0.3),azimuth_range=(-60,60),unit='chi_rad',mask=mask)#,azimuth_range=(50,125)
    x=result1d_rad.radial
    y=result1d_rad.intensity
    
    resultFit,yfit=bf.singlePeakFit(x,y,autoFit=True,peak_type="Gaussian+LinearBg")
    peakCenter.append(resultFit['peak_center'])
    fwhm.append(resultFit['fwhm'])
    
    #I~q
    result1d_azi=bf.integrateAzimuthal(integrator, data, 1000,radial_range=None,azimuth_range=(-20,20),mask=mask) #for guinier SAXS
    q=result1d_azi.radial
    i=result1d_azi.intensity
    
    # curve crop
    q=q[23:710]
    i=i[23:710]
    # curve mask
    q,i=bf.userDefinedMask1D(q, i,(85,95))
    
    #attention!
    # q,i=bf.takePositive1D(q, i) #q,i=bf.userDefinedMask1D(q,i,index=None)
    
    #Porod operation
    xPorod,yPorod,slopefit,lnKfit=bf.porodFit(q, i, (480,676))
    if correction==True:
        i_correct,yPorod_correct=bf.porodCorrect(q, i, slopefit, lnKfit)
        
    
    #Guinier fit
    resultGuinier,fun_lnI=bf.guinierFit(q, i_correct,False,(0,10))
    rg.append(resultGuinier['Rg'])
    
    #integralInvariant
    invQ=bf.integralInvariant(q, i_correct, resultGuinier['Rg'], resultGuinier['I0'], np.exp(lnKfit))

    t=4*invQ/np.pi/np.exp(lnKfit) 
    t_parameter.append(t)
        

end=time.time()
print(end-start)   
    
#%%
peak_center=np.array(peakCenter)
peak_center=peak_center*180/np.pi
peak_center=peak_center.reshape(16,37)



orientation=(np.pi-np.array(fwhm))/np.pi
orientation=orientation.reshape(16,37)
orientation[np.abs(orientation)>1]=np.nan

plt.figure()
plt.imshow(orientation)
plt.colorbar()


Rg=np.array(rg).reshape(16,37)
Rg=np.where(np.abs(peak_center)>10,np.nan,Rg)

plt.figure()
plt.imshow(Rg)
plt.colorbar()


T_para=np.array(t_parameter).reshape(16,37)
T_para[np.abs(peak_center)>10]=np.nan
plt.figure()
plt.imshow(T_para)
plt.colorbar()


peak_center[np.abs(peak_center)>10]=np.nan
plt.figure()
plt.imshow(peak_center)
plt.colorbar()



#%%  
'''
#plot for 2D integration 
I=result2d.intensity
q=result2d.radial
chi=result2d.azimuthal 
q0=q[0:150]
I0=I[:,0:150]
    
extent=[np.min(q0),np.max(q0),np.min(chi),np.max(chi)]
plt.figure()
plt.imshow(I0,extent=extent,aspect='auto',origin='lower')
'''

#plot for 1D integration

plt.figure()
plt.plot(q,np.log(i_correct))

plt.figure()
plt.plot(np.log(q[23:]),np.log(i[23:]))


#plot for peak fit
plt.figure()
plt.plot(x,y)
plt.plot(x,yfit)

plt.figure()
plt.plot(x,y_low)
plt.figure()
plt.plot(x,y_high)

plt.figure()
plt.plot(x,y_sub)
plt.plot(x,yfit)

#plot for guinier fit

x0=q[0:resultGuinier['qmax_Pixel']+6]**2
y0=np.log(i[0:resultGuinier['qmax_Pixel']+6])
xfit=q[resultGuinier['qmin_Pixel']:resultGuinier['qmax_Pixel']+1]**2
yfit=fun_lnI(resultGuinier['I0'],resultGuinier['Rg'],q[resultGuinier['qmin_Pixel']:resultGuinier['qmax_Pixel']+1])
plt.figure()
plt.scatter(x0,y0) 
plt.plot(xfit,yfit)       

#plot for porod
'''
xPorod=q**2
yPorod=np.log(i*q**4)
plt.figure()
plt.plot(xPorod,yPorod)
'''
if correction==False:
    plt.figure()
    plt.plot(xPorod,yPorod)
    plt.xlabel('q^2')
    plt.ylabel('I(q)*q^4')
    plt.legend()
else:
    plt.figure()
    plt.plot(xPorod,yPorod,color='black',label='before correction')
    plt.plot(xPorod,yPorod_correct,color='red',label='after correction')
    plt.plot([0,q[-1]**2],[lnKfit,lnKfit+slopefit*q[-1]**2],color='green',ls='--')
    plt.plot([0,q[-1]**2],[lnKfit,lnKfit],color='green',ls='--')
    plt.xlabel('q^2')
    plt.ylabel('ln(I*q^4)')
    plt.legend()



data = fabio.open(path).data
# data=tifffile.imread(path)
data_mask=reconstruct(data, mask,dummy=-10)
plt.figure()
plt.imshow(np.log(data_mask))
plt.colorbar()

plt.figure()
plt.imshow(np.log(data))
plt.colorbar()




