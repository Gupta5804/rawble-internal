# Generated by Django 2.1.4 on 2019-07-09 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_make'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='zoho_location',
            field=models.CharField(blank=True, default='okhla', max_length=200, null=True),
        ),
    ]
