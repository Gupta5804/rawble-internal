# Generated by Django 2.1.4 on 2019-03-14 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20190305_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='make',
            field=models.CharField(blank=True, default=' ', max_length=100),
        ),
    ]