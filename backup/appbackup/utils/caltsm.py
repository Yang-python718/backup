import os

import numpy as np
from osgeo import gdal

os.environ['PROJ_LIB'] = r'C:\Python39\Lib\site-packages\osgeo\data\proj'
import math


class trantiff():
    bbw = None
    h0 = None
    h1 = None
    h2 = None
    b = None
    a = None
    c = None
    dataset = None
    Rrs = None
    proj = None
    geotrans = None
    rrs_result = None
    result_ulanboda = None
    result_a_665 = None
    result_bbp_665 = None
    x_result = None
    result_Y = None
    result_bbplanboda = None
    result_alanboda = None
    bb = None
    result_IP = None

    # 测试变量
    # numpy索引从0开始,维数，行列数都是
    def __init__(self, bbw=None, h0=None, h1=None, h2=None, filename=None):
        self.bbw = bbw
        self.h0 = h0
        self.h1 = h1
        self.h2 = h2
        # self.dataset = gdal.Open(os.path.join(os.getcwd(), filename))
        self.dataset = gdal.Open(filename)

    def openfile(self):
        # dataset = gdal.Open(os.path.join(os.getcwd(), 'sential/S2B_2203_b14_Clip1.tif'))
        self.b = self.dataset.RasterXSize
        self.a = self.dataset.RasterYSize
        self.c = self.dataset.RasterCount
        self.Rrs = self.dataset.ReadAsArray(0, 0, self.b, self.a)
        self.proj = self.dataset.GetProjection()
        self.geotrans = self.dataset.GetGeoTransform()

    def step1(self):
        self.Rrs[self.Rrs < 0] = np.nan
        self.rrs_result = self.rrs(self.Rrs)
        self.result_ulanboda = self.calculate_ulanboda(rrs_result=self.rrs_result)

    def step23(self):
        result_a_665 = np.zeros((self.a, self.b))
        result_bbp_665 = np.zeros((self.a, self.b))
        for i in range(0, self.a):
            for j in range(1, self.b):
                if self.Rrs[3, i, j] < 0.0015:
                    self.x_result = self.calculate_x(rrs_result=self.rrs_result, i=i, j=j)
                    result_a_665[i, j] = 0.4223 + 10 ** (self.h0 + self.h1 * self.x_result + self.h2 * self.x_result ** 2)
                    result_bbp_665[i, j] = (self.result_ulanboda[3, i, j] * result_a_665[i, j]) / (1 - self.result_ulanboda[3, i, j]) - np.array(self.bbw)[2]
                else:
                    result_a_665[i, j] = 0.4223 + 0.39 * (self.Rrs[3, i, j] / (self.Rrs[0, i, j] + self.Rrs[1, i, j])) ** 1.14
                    result_bbp_665[i, j] = (np.array(self.result_ulanboda[3, i, j]) * np.array(result_a_665[i, j])) / (1 - np.array(self.result_ulanboda[3, i, j])) - np.array(self.bbw)[3]
        self.result_a_665 = result_a_665
        self.result_bbp_665 = result_bbp_665

    def step4(self):
        self.result_Y = self.calculate_Y(rrs_result=self.rrs_result)

    # ---------------------------------------有问题start--------------------------------------------------
    def step5(self):
        self.result_bbplanboda = self.calculate_bbplanboda(result_bbp_665=self.result_bbp_665, result_Y=self.result_Y)

    def step6(self):
        self.result_alanboda = self.calculate_alanboda(result_ulanboda=self.result_ulanboda, result_bbplanboda=self.result_bbplanboda, bbw=self.bbw)

    def step7(self):
        bb = self.result_bbplanboda[0:, :] + np.array(self.bbw)[0]
        for i in range(1, 4):
            bb[i, :, :] = self.result_bbplanboda[i, :, :] + np.array(self.bbw)[i]
        self.bb = bb
        self.result_IP = self.calculate_IP(bb=bb, result_alanboda=self.result_alanboda)

    def step8(self):
        TEMSPM = 2036.841 * self.result_IP - 1840.843
        TEMSPM[np.isnan(TEMSPM)] = 0
        self.TEMSPM = TEMSPM
        result_SPM = np.zeros((self.a, self.b))
        for i in range(0, self.a):
            for j in range(1, self.b):
                if self.Rrs[0, i, j] > 0.285:
                    result_SPM[i, j] = -1
        for i in range(0, self.a):
            for j in range(1, self.b):
                result_SPM[i, j] = (TEMSPM[0, i, j] + TEMSPM[1, i, j] + TEMSPM[2, i, j] + TEMSPM[3, i, j]) / 4
        self.SPM = result_SPM

        # 写文件，以写成tif为例
    def write_img(self, filename, im_proj, im_geotrans, im_data):
        # gdal数据类型包括
        # gdal.GDT_Byte,
        # gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
        # gdal.GDT_Float32, gdal.GDT_Float64

        # 判断栅格数据的数据类型
        if 'int8' in im_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in im_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        # 判读数组维数
        if len(im_data.shape) == 3:
            im_bands, im_height, im_width = im_data.shape
        else:
            im_bands, (im_height, im_width) = 1, im_data.shape

        # 创建文件
        driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
        dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
        else:
            for i in range(im_bands):
                dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

        del dataset

    def rrs(self, Rrs):
        Rrs2 = Rrs * 1.7 + 0.52
        rrs_result = Rrs / Rrs2
        return rrs_result

    def calculate_ulanboda(self, rrs_result):
        g1 = 0.1247
        g0 = 0.0895
        rrs_result1 = g0 ** 2 + 4 * g1 * rrs_result
        result_ulanboda = (np.sqrt(rrs_result1) - g0) / (2 * g1)
        return result_ulanboda

    def calculate_x(self, rrs_result, i, j):
        p1 = rrs_result[0, i, j] + rrs_result[1, i, j]
        p2 = rrs_result[2, i, j] + 5 * rrs_result[3, i, j] / rrs_result[1, i, j] * rrs_result[3, i, j]
        x_result = math.log10(p1 / p2)
        return x_result

    def calculate_Y(self, rrs_result):
        result_Y = 2.0 * (1 - 1.2 * np.exp(-0.9 * rrs_result[0, :, :] / rrs_result[2, :, :]))
        return result_Y

    def calculate_bbplanboda(self, result_bbp_665, result_Y):
        bbplanbodaF11 = result_bbp_665 * ((665 / 442)) ** result_Y
        bbplanbodaF12 = result_bbp_665 * ((665 / 492)) ** result_Y
        bbplanbodaF13 = result_bbp_665 * ((665 / 559)) ** result_Y
        bbplanbodaF14 = result_bbp_665 * ((665 / 665)) ** result_Y
        bbplanbodaF1 = [bbplanbodaF11, bbplanbodaF12, bbplanbodaF13, bbplanbodaF14]
        return np.array(bbplanbodaF1)

    def calculate_alanboda(self, result_ulanboda, result_bbplanboda, bbw):
        result_alanboda1 = ((1 - result_ulanboda[0, :, :]) * (result_bbplanboda[0, :, :] + 0.0037)) / result_ulanboda[0, :, :]
        result_alanboda2 = ((1 - result_ulanboda[1, :, :]) * (result_bbplanboda[1, :, :] + 0.0022)) / result_ulanboda[1, :, :]
        result_alanboda3 = ((1 - result_ulanboda[2, :, :]) * (result_bbplanboda[2, :, :] + 0.0013)) / result_ulanboda[2, :, :]
        result_alanboda4 = ((1 - result_ulanboda[3, :, :]) * (result_bbplanboda[3, :, :] + 0.0006)) / result_ulanboda[3, :, :]
        result_alanboda = [result_alanboda1, result_alanboda2, result_alanboda3, result_alanboda4]
        return np.array(result_alanboda)

    def calculate_IP(self, bb, result_alanboda):
        result_IP = bb / (bb + result_alanboda)
        return result_IP


# if __name__ == '__main__':
    # filename = 'sential/S2B_2203_b14_Clip1.tif'
    # mytif = trantiff(bbw=[0.0037, 0.0022, 0.0013, 0.0006], h0=-1.146, h1=-1.366, h2=-0.469, filename=filename)
    # mytif.openfile()
    # print('打开文件')
    # # print(mytif.b, mytif.a, mytif.c,mytif.proj)
    # mytif.step1()
    # print('step1完成')
    # mytif.step23()
    # print('step23完成')
    # mytif.step4()
    # print('step4完成')
    # mytif.step5()
    # print('step5完成')
    # mytif.step6()
    # print('step6完成')
    # mytif.step7()
    # print('step7完成')
    # realfilename = 'outtiff' + filename.split('/')[1]
    # mytif.write_img(filename=realfilename, im_proj=mytif.proj, im_geotrans=mytif.geotrans, im_data=mytif.result_IP)
    # print('生成文件！结束')
