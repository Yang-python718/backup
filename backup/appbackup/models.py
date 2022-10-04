from django.conf import settings
from django.db import models
import django.utils.timezone as timezone
from appbackup.utils import caltsm,tiff2jpg


# Create your models here.
class Image(models.Model):
    imagename=models.CharField(max_length=30,verbose_name='影像名字')
    imagetif=models.FileField(upload_to='imagetif',null=True,verbose_name='遥感影像原始文件rrs_tif')
    imagetif2jpg = models.ImageField(upload_to='imagetif2jpg', max_length=100, blank=True, null=True,verbose_name='遥感影像原始文件tif转jpg')
    ioptif = models.FileField(upload_to='ioptif', null=True, verbose_name='遥感影像处理文件iop_tif')
    image = models.ImageField(upload_to='image', max_length=100, blank=True, null=True, verbose_name='遥感影像处理后tiff2jpg')
    SPMtif = models.FileField(upload_to='SPMtif', null=True, verbose_name='悬浮泥沙文件SPM_tif')
    SPMimage = models.ImageField(upload_to='SPMimage', max_length=100, blank=True, null=True, verbose_name='悬浮泥沙文件处理后SPM2jpg')
    createtime=models.DateField(default=timezone.now,verbose_name='创建时间')

    class Meta:
        verbose_name='所有image数据'
        verbose_name_plural=verbose_name

    # def save(self,*args, **kwargs):
    #     import os
    #     print(self.imagetif.url)
    #     # if self.imagetif:
    #     #     if not self.imagetif:
    #     #
    #     #         filename = 'http://127.0.0.1:8080'+settings.MEDIA_URL+self.imagetif.va
    #     #         mytif = caltsm.trantiff(bbw=[0.0037, 0.0022, 0.0013, 0.0006], h0=-1.146, h1=-1.366, h2=-0.469, filename=filename)
    #     #         mytif.openfile()
    #     #         print('打开文件')
    #     #         # print(mytif.b, mytif.a, mytif.c,mytif.proj)
    #     #         mytif.step1()
    #     #         print('step1完成')
    #     #         mytif.step23()
    #     #         print('step23完成')
    #     #         mytif.step4()
    #     #         print('step4完成')
    #     #         mytif.step5()
    #     #         print('step5完成')
    #     #         mytif.step6()
    #     #         print('step6完成')
    #     #         mytif.step7()
    #     #         print('step7完成')
    #     #         realfilename = 'outtiff' + filename.split('/')[1]
    #     #         mytif.write_img(filename=realfilename, im_proj=mytif.proj, im_geotrans=mytif.geotrans, im_data=mytif.result_IP)
    #     #         print('生成文件！结束')
    #
    #     super().save(*args, **kwargs)