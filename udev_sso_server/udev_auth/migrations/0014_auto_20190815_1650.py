# Generated by Django 2.1.1 on 2019-08-15 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('udev_auth', '0013_client_user_weibo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_user',
            name='weibo',
            field=models.CharField(max_length=255, null=True),
        ),
    ]