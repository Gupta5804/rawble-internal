# Generated by Django 2.1.4 on 2019-06-26 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicedelivery', '0003_auto_20190625_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorderproductplan',
            name='lr_mailsent_status',
            field=models.BooleanField(default=False),
        ),
    ]
