import json
from django.utils import timezone

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import status
from appbackup.models import Image
from appbackup.serializer import ImageSerializer
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from appbackup.utils import caltsm, tiff2jpg, tiff2jpg2
import os

import json
from django.http import HttpResponse
from django.core import serializers

# Create your views here.
class ImageViewset(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # pagination_class = LimitOffsetPagination


# 上传problem表单文件中的文件
def upload_problem_zip(request):
    data = request.FILES.get('file')
    print('-'*10, type(data))
    originalpath=os.getcwd()
    print(os.getcwd())
    print('源文件名')
    imagename=str(data)
    print(imagename)
    # 获取当前文件
    filename=data.temporary_file_path()
    dataexist=Image.objects.filter(imagename=imagename)
    if dataexist.exists():
        meta={
            'message':'数据已经存在，请直接查询',
            'status':'304'
        }
        return render_json(meta,status=304)
    else:
        Image.objects.create(imagename=imagename,imagetif=data)
        # 源文件转jpg
        print('源文件转jpg')
        imagetif2jpg=originalpath + '\\media\\imagetif\\'+ imagename
        imagetif2jpgrespath = originalpath + '\\media\\imagetif2jpg\\' + 'imagetif2jpg' + imagename.split('.')[0] + '.jpg'
        tran = tiff2jpg.tran()
        tran.stretchImg(imagetif2jpg, imagetif2jpgrespath)

        # 求IOPtif
        print('求IOPtif')
        mytif = caltsm.trantiff(bbw=[0.0037, 0.0022, 0.0013, 0.0006], h0=-1.146, h1=-1.366, h2=-0.469, filename=filename)
        mytif.openfile()
        print('打开文件')
        # print(mytif.b, mytif.a, mytif.c,mytif.proj)
        mytif.step1()
        # print('step1完成')
        mytif.step23()
        # print('step23完成')
        mytif.step4()
        # print('step4完成')
        mytif.step5()
        # print('step5完成')
        mytif.step6()
        # print('step6完成')
        mytif.step7()
        # print('step7完成')
        mytif.step8()
        # print('step8完成')

        realfilename = originalpath+'\\media\\ioptif\\'+'iop'+imagename.split('.')[0]+'.tif'
        mytif.write_img(filename=realfilename, im_proj=mytif.proj, im_geotrans=mytif.geotrans, im_data=mytif.result_IP)

        SPMfilename = originalpath+'\\media\\SPMtif\\'+'SPM'+imagename.split('.')[0]+'.tif'
        mytif.write_img(filename=SPMfilename, im_proj=mytif.proj, im_geotrans=mytif.geotrans, im_data=mytif.SPM)
        print('生成文件！结束')

        imgpath = realfilename
        respath = originalpath+'\\media\\image\\'+'iop2jpg'+imagename.split('.')[0]+'.jpg'
        tran = tiff2jpg.tran()
        tran.stretchImg(imgpath, respath)

        imgpath = SPMfilename
        respath = originalpath + '\\media\\SPMimage\\' + 'SPM2jpg' + imagename.split('.')[0] + '.jpg'
        tran = tiff2jpg2.tran()
        tran.stretchImg(imgpath, respath)

        Image.objects.filter(imagename=imagename).update(imagetif2jpg='imagetif2jpg/'+'imagetif2jpg'+imagename.split('.')[0]+'.jpg',
                                                         ioptif='ioptif/'+'iop'+imagename.split('.')[0]+'.tif',
                                                         image='image/'+'tif2jpg'+imagename.split('.')[0]+'.jpg',
                                                         SPMtif='SPMtif/' + 'SPM' + imagename.split('.')[0] + '.tif',
                                                         SPMimage='SPMimage/' + 'SPM2jpg' + imagename.split('.')[0] + '.jpg',
                                                         )

        print("666666666666,path=", data)
        return render_json({"path": "media/imagetif/"+str(data)})


def render_json(data, status=200):
    return HttpResponse(json.dumps(data), content_type="text/json", status=status)

def searchtime(request,year,month):
    year=year
    month=month
    qs=Image.objects.filter(createtime__year=year,createtime__month=month)
    if qs:
        json_data=serializers.serialize('json',qs)
        return HttpResponse(json_data,content_type="application/json")

def searchimage(request,imagename):
    imagename=imagename
    qs=Image.objects.filter(imagename=imagename)
    if qs:
        json_data = serializers.serialize('json', qs)
        return HttpResponse(json_data, content_type="application/json")

def searchall(request):
    qs=Image.objects.all()
    json_data = serializers.serialize('json', qs)
    return HttpResponse(json_data, content_type="application/json")

