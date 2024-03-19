import numpy as np
# lib for construction
import astra#,tomopy
import matplotlib.pylab as plt
#lib for filter
import cv2,tifffile


#%%
############################################
############ Pre Construction  #############
############################################
def AveImg(data):
    return np.mean(data, axis=0)

class PreRecon():
    '''
    背景矫正：图片平均，归一化，去除负值，本低去除，
    '''
    def __init__(self,Proj,Flat=None,Dark=None,RemoveZeros=True):
        '''
        :param Proj: Projection # 3D array
        :param Flat: Flat images   # 3D array
        :param Dark: Drak  iamges # 3D array
        :param RemoveZeros # bool
        '''
        if RemoveZeros:
            Proj[Proj<0]=0
        self.Proj=Proj
        self.FlatAve=None
        self.DarkAve=None
        if Flat is not None:
            if RemoveZeros:
                Flat[Flat<0]=0
            self.FlatAve = AveImg(Flat)
        self.Flat = Flat
        if Dark is not None:
            if RemoveZeros:
                Dark[Dark<0]=0
            self.DarkAve=AveImg(Dark)
        self.Dark = Dark

    def normalize(self):
        '''
        Normalize raw projection data using the flat and dark field projections
        :return:
        '''
        if self.Flat is not None and self.Dark is not None:
            NorProj = (self.Proj-self.DarkAve)/ (self.FlatAve-self.DarkAve)
        if self.Flat is not None and self.Dark is None:
            NorProj = self.Proj/ self.FlatAve
        else:
            NorProj = self.Proj
        return NorProj

    def AveDark(self):
        return self.DarkAve
    def AveFalt(self):
        return self.FlatAve

    def normalize_Dark(self):
        '''
        Normalize raw projection data using the dark field projections
        :return:
        '''
        NorProj = self.Proj-self.DarkAve
        return NorProj
    def normalize_Flat(self):
        '''
        Normalize raw projection data using the dark flat projections
        :return:
        '''
        NorProj = self.Proj/self.FlatAve
        return NorProj

    def minus_log(self,data):
        '''
        Computation of the minus log of a given array.
        :param data: # 3D array
        :return: MlData
        '''
        MlData = np.log(np.max(data)/data)
        return MlData

def GenSino(X, Y, data ,sino):
    label = False
    if sino is None :
        sino = np.zeros([X, Y])
        sino[np.isnan(sino)] = np.nan
        print(sino)

    num = np.count_nonzero(~np.isnan(data))
    if num == 0:
        sino[0,0] = data
    else :
        pos_x = (num)//X
        pos_y = (num)%X
        sino[pos_x,pos_y] = data

    if num  == X*Y:
        label = True
    return sino,label



#%%
#########################################
############ Recontruction  #############
#########################################

################平移转轴###########

def ProjCorrection(Proj, ROC):
    '''
    :param Proj: # 3D array
                 # projection images
    :param ROC: # float
                # Rotation of Center
    :return ProjCorr: # 3D array
                      # Corrected projection images
    '''
    nx, ny, nz = np.shape(Proj)
    if ROC == int(nz / 2):
        ProjCorr=Proj
    else:
        dx = int(nz / 2)-ROC
        MAT = np.float32([[1, 0, dx], [0, 1, 0]])
        ProjCorr = np.zeros(Proj.shape, dtype=np.float32)

        for i in range(Proj.shape[0]):
            img = Proj[i]
            # print(np.shape(img),(img.shape[1], img.shape[0]))
            img_rot = cv2.warpAffine(img, MAT, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REPLICATE)  # 平移
            ProjCorr[i] = img_rot

        # for i in range(nx):
        #     if ROC > nz / 2:
        #         start = ROC * 2 - nz
        #         ProjCorr=Proj[:,:, start + 1:]
        #     else:
        #         end = ROC * 2
        #         ProjCorr=Proj[:,:, :end + 1]
    return ProjCorr

################旋转转轴###########

def Correct_axis(imgarr, rotate_point, tilt):
    '''校正转轴的函数
       imgarr：三维数组
       rotate_center:图片旋转时所围绕的点，旋转后该点的横坐标即为转轴位置
       tilt：转轴倾角，单位角度'''
    if tilt == 0:
        #print('转轴倾角为0，无需校正')
        return imgarr
    correct_imgarr = np.zeros(imgarr.shape, dtype=np.float32)
    # print('rotate_point',rotate_point)
    #print('tilt:',tilt)
    m = cv2.getRotationMatrix2D(rotate_point, tilt, 1)  # 构造旋转矩阵
    # print(imgarr.shape[0])
    for i in range(imgarr.shape[0]):
        img = imgarr[i]
        # print(np.shape(img),(img.shape[1], img.shape[0]))
        img_rot = cv2.warpAffine(img, m, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REPLICATE)  # 旋转BORDER_REPLICATE
        correct_imgarr[i] = img_rot

    return correct_imgarr
#########################################
##################锥束重构################
#########################################

#############mask###############
def define_mask(data,SSD=None,SDD=None,DetectorSize=None):
    nx,ny,nz =np.shape(data)
    c = np.linspace(-nz/2, nz/2, nz)
    x, y = np.meshgrid(c, c)
    R = nz/2
    tmp = np.array((x ** 2 + y ** 2 < R  ** 2), dtype=float)
    mask = np.zeros([ny,nz,nz])
    for i in range(ny):
        mask[i,:,:] = tmp

    return mask

class Recon_cone():
    #int
    def __init__(self,DetectorSize,SSD,SDD,RAlgorithm=None,Iter=None,AngleScale=None, mask=None):
        '''
            :ROC:        #int
                         # Rotation of center
            :param DetectorSize: # float
                                 # size of each probe element of the flat plate detector
            :param SSD: # float
                        # distance from the ray source to the center of the object
            :param SDD: # float
                        # distance from the center of the object to the flat plate detector

            :param RAlgorithm: # str
                               # Algorithm of Reconstruction
                                ”BP3D_CUDA“ ”FDK_CUDA“ ”SIRT3D_CUDA“ ”CGLS3D_CUDA“
            :param Iter: # int
                         # Number of Iteration
            :param AngleScale: # float
                               # scale of projection angles
            :return:
                Rec: # 3D array
                     # The reconstruction slices

        '''
        #########Paras initialization###############

        self.DetectorSize = DetectorSize
        self.SSD = SSD
        self.SDD = SDD
        if RAlgorithm is None:
            self.RAlgorithm = 'FDK_CUDA'
        else:
            self.RAlgorithm = RAlgorithm
        if AngleScale is None:
            self.AngleScale = 2 * np.pi
        else:
            self.AngleScale = AngleScale
        if Iter is None:
            self.Iter = 1
        else:
            self.Iter = Iter
        self.DetectorScale = self.SSD * self.DetectorSize / (self.SSD + self.SDD)  # 放大比
        self.mask = mask


    def Recon_Function(self, Proj, ROC):
        '''
        :param
            Proj:  # 3D array
                   # projection images
        :ROC:  # int
        '''
        Proj=ProjCorrection(Proj, ROC)
        if self.mask is not None:
            self.mask = define_mask(Proj,self.SSD,self.SDD,self.DetectorSize)

        ########按照astra库要求角度放在第二个维度########
        Proj=Proj.transpose(1, 0, 2)
        nx, ny, nz = np.shape(Proj)
        #print(nx,ny,nz)
        Angles = np.linspace(self.AngleScale, 0, ny, False)########记得更改，角度反是因为实际设备和astra里的几何不一致##########
        #Angles = np.linspace(0,self.AngleScale, ny, False)  ########记得更改，角度反是因为实际设备和astra里的几何不一致##########
        #################Reconstruction###########
        proj_geom = astra.creators.create_proj_geom('cone', self.DetectorSize / self.DetectorScale,
                                                    self.DetectorSize / self.DetectorScale,
                                                    nx, nz, Angles, self.SSD / self.DetectorScale,
                                                    self.SDD / self.DetectorScale)
        # vol_geom = astra.creators.create_vol_geom(ny, nx, nx)
        vol_geom = astra.creators.create_vol_geom(nz, nz, nx)
        proj_id = astra.data3d.create('-sino', proj_geom, Proj)
        rec_id = astra.data3d.create('-vol', vol_geom)
        if self.mask is not None:
            mask_id = astra.data3d.create('-vol', vol_geom, self.mask)

        cfg_fdk = astra.astra_dict(self.RAlgorithm)
        cfg_fdk['ProjectionDataId'] = proj_id
        cfg_fdk['ReconstructionDataId'] = rec_id
        if self.mask is not None:
            cfg_fdk['option'] = {}
            cfg_fdk['option']['ReconstructionMaskId'] = mask_id

        alg_id = astra.algorithm.create(cfg_fdk)
        astra.algorithm.run(alg_id, self.Iter)
        ##########重构数据############
        Rec = astra.data3d.get(rec_id)
        ######################清空内存###################
        astra.algorithm.delete(alg_id)
        astra.data3d.delete(rec_id)
        astra.data3d.delete(proj_id)
        if self.mask is not None:
            astra.data2d.delete(mask_id)
        ###########################################
        if self.RAlgorithm == 'FDK_CUDA':
            Rec= Rec*self.mask
            Rec = Rec.astype('float32')

        return Rec

    def FindCenter(self,Proj,ROCRange):
        '''
        :param SlicesNum: # int
        :param CenterRang: # tuple
        :param Path: # str
        :return:
            slices_ROC: # list
            label: # dist
        '''
        nx,nz = np.shape(Proj)
        Proj=Proj.reshape(nx,1,nz)
        MinROC = ROCRange[0]
        MaxROC = ROCRange[1]
        StepROC = ROCRange[2]

        i=0
        ROCs = np.arange(MinROC,MaxROC,StepROC)
        slices_Find_ROC=np.zeros([len(ROCs),nz,nz])
        for ROC_tmp in ROCs:
            slice=self.Recon_Function(Proj,ROC_tmp)

            #print(np.shape(slice))
            slices_Find_ROC[i, :slice.shape[1],:slice.shape[2]] = slice
            i=i+1

        return slices_Find_ROC

#########################################
##################平行光重构################
#########################################

class Recon_parallel():
    def __init__(self, RAlgorithm=None, Iter=None, AngleScale=None):
        if RAlgorithm is None:
            self.RAlgorithm = 'FBP'
        else:
            self.RAlgorithm = RAlgorithm
        if AngleScale is None:
            self.AngleScale = np.pi
        else:
            self.AngleScale = AngleScale
        if Iter is None:
            self.Iter = 1
        else:
            self.Iter = Iter

    def Recon_single_sinogram(self, sino, ROC):
        nx, ny = np.shape(sino)
        sino_corr = ProjCorrection(sino.reshape(1,nx,ny), ROC)
        mask = define_mask(sino.reshape(1,nx,ny))
        sino_corr = sino_corr[0,:,:]

        # print(nx,ny,nz)
        Angles = np.linspace(0,self.AngleScale, num=nx, endpoint=True)

        proj_geom = astra.creators.create_proj_geom('parallel', 1.0, ny,  Angles)
        vol_geom = astra.creators.create_vol_geom(ny, ny)

        sinogram_id = astra.data2d.create('-sino', proj_geom, sino_corr)
        # create forward projection
        proj_id = astra.create_projector('strip', proj_geom, vol_geom)
        mask_id = astra.data2d.create('-vol', vol_geom, True)
        # # Create a data object for the reconstruction
        rec_id = astra.data2d.create('-vol', vol_geom)
        #
        # # create configuration
        rec_id = astra.data2d.create('-vol', vol_geom)
        cfg = astra.astra_dict(self.RAlgorithm)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sinogram_id
        cfg['ProjectorId'] = proj_id
        cfg['option'] = {}
        #cfg['option']['ReconstructionMaskId'] = mask_id

        # 1. Use a standard Ram-Lak filter
        #cfg['option']['FilterType'] = 'ram-lak'

        alg_id = astra.algorithm.create(cfg)
        astra.algorithm.run(alg_id,self.Iter)
        rec_RL = astra.data2d.get(rec_id)

        astra.algorithm.delete(alg_id)
        return rec_RL#*mask[0,:,:]



# def Recon_parallel_Tomopy(sino, theta, center, algorithm, num_iter):
#     nx, ny = np.shape(sino)
#     # print(nx,ny)
#     sino = sino.reshape([nx,-1,ny])
#     slice = tomopy.recon(sino, theta, center=center, algorithm=algorithm, num_iter=num_iter)
#
#     return  slice[0,:,:]

#########################################
############ Filter  #############
#########################################



def NonLocalMeans(data,h,search_window,block_size):
    if data.ndim ==2:
        Fdata=cv2.fastNlMeansDenoising(data,None,h,search_window,block_size)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=cv2.fastNlMeansDenoising(data[i,:,:],None,h,search_window,block_size)
    return Fdata

def Blur(data, ksize):
    if data.ndim ==2:
        Fdata=cv2.blur(data,ksize)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=cv2.blur(data[i,:,:],ksize)
    return Fdata

def GaussianBlur( data, ksize,sigmaX,sigmaY):
    if data.ndim ==2:
        Fdata=cv2.GaussianBlur(data, ksize,sigmaX,sigmaY)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=cv2.GaussianBlur(data[i,:,:], ksize,sigmaX,sigmaY)
    return Fdata

def MedianBlur(data, ksize):
    if data.ndim ==2:
        Fdata=cv2.medianBlur(data,ksize)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=cv2.medianBlur(data[i,:,:],ksize)
    return Fdata

def BilateralFilter( data, d,sigmaColor,sigmaSpace):
    if data.ndim ==2:
        Fdata=cv2.bilateralFilter(data,d,sigmaColor,sigmaSpace)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=cv2.bilateralFilter(data[i,:,:],d,sigmaColor,sigmaSpace)
    return Fdata


#########################################
############ threshold  #############
#########################################
def InteractiveThreshold( data,Imin,Imax,Ttype):
    if data.ndim ==2:
        ret,Fdata=cv2.threshold(data,Imin,Imax,Ttype)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            ret,Fdata[i,:,:]=cv2.threshold(data[i,:,:],Imin,Imax,Ttype)
    return Fdata

def KmeansSegmentation2D(image,nclusters,CriteriaType,max_iter,epsilon,attempts,FlagsType):
    criteria = (CriteriaType, max_iter, epsilon)
    k = nclusters
    img1 = image.reshape((image.shape[0] * image.shape[1], 1))
    img1 = np.float32(img1)
    compactness, labels, centers = cv2.kmeans(img1, k, None, criteria, attempts, FlagsType)
    return labels.reshape((image.shape[0], image.shape[1]))

def KmeansSegmentation(data,nclusters,CriteriaType,max_iter,epsilon,attempts,FlagsType):
    if data.ndim ==2:
        Fdata=KmeansSegmentation2D(data,nclusters,CriteriaType,max_iter,epsilon,attempts,FlagsType)
    else:
        Fdata=np.zeros(np.shape(data))
        for i in range(data.shape[0]):
            Fdata[i,:,:]=KmeansSegmentation2D(data[i,:,:],nclusters,CriteriaType,max_iter,epsilon,attempts,FlagsType)
    return Fdata


'''
thres = cv2.threshold(gray, -0.2, 0, cv2.THRESH_BINARY_INV)
'''