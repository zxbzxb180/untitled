# Generated by Django 2.1.1 on 2019-08-15 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('udev_auth', '0012_merge_20190806_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_user',
            name='weibo',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
