# Generated by Django 2.1.4 on 2019-06-21 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0015_auto_20190620_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderproduct',
            name='quantity_received',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='purchaseorderproduct',
            name='quantity_to_receive',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
    ]