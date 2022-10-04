import numpy as np
import os
import sys
from PIL import Image
from osgeo import gdal, gdalconst
os.environ['PROJ_LIB'] = r'C:\Python39\Lib\site-packages\osgeo\data\proj'

class tran():
    def __init__(self):
        self.data=None
        self.out=None
        self.t=None
        self.t=None
        self.c=None
        self.d=None


    def readTif(self,original):
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        ds = gdal.Open(original, gdal.GA_ReadOnly)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        geotransform = ds.GetGeoTransform()
        proj = ds.GetProjection()
        # data = np.empty([4,rows, cols], dtype=float)
        # for i in range(3):
        #     band = ds.GetRasterBand(i)
        #     data1 = band.ReadAsArray()
        #     data[i,:, :] = data1
        data=ds.ReadAsArray(0, 0, cols,rows)
        self.data=data
        return data
    #百分比拉伸
    def stretchImg(self,imgPath, resultPath, lower_percent=0.6, higher_percent=99.4):
        data=self.readTif(imgPath)
        n = data.shape[0]
        out = np.zeros_like(data, dtype=np.uint8)
        for i in range(n):
            a = 0
            b = 255
            c = np.nanpercentile(data[i,:, :], lower_percent)
            d = np.nanpercentile(data[i,:, :], higher_percent)
            t = a + (np.array(data[i,:, :]) - np.array(c)) * (b-a) / (np.array(d) - np.array(c))
            t[t < a] = a
            t[t > b] = b
            self.t=t
            out[i,:, :] = t
            # out[i,:,:]=t
        self.out=out
        Image.fromarray(np.uint8(out.transpose(1, 2, 0))).convert('RGB').save(resultPath, format="png")
        # outImg=Image.fromarray(np.uint8(out))
        # outImg.save(resultPath)

# if __name__ == '__main__':
#     imgpath=r'C:\Users\dell\Desktop\QAA\outtiffS2B_2203_b14_Clip1.tif'
#     respath=r'C:\Users\dell\Desktop\QAA\trantiffS2B_2203_b14_Clip1.jpg'
#     tran=tran()
#     tran.stretchImg(imgpath,respath)