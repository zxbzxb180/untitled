# Generated by Django 2.1.1 on 2019-07-19 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('udev_auth', '0002_auto_20190719_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cas_client',
            name='url',
            field=models.URLField(max_length=1000),
        ),
    ]
