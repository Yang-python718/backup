# Generated by Django 3.2 on 2022-10-04 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appbackup', '0007_auto_20221004_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='SPMimage',
            field=models.ImageField(blank=True, null=True, upload_to='SPMimage', verbose_name='悬浮泥沙文件处理后SPM2jpg'),
        ),
        migrations.AlterField(
            model_name='image',
            name='SPMtif',
            field=models.FileField(null=True, upload_to='SPMtif', verbose_name='悬浮泥沙文件SPM_tif'),
        ),
    ]
