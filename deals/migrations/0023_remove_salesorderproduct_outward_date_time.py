# Generated by Django 2.1.4 on 2019-06-26 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0022_remove_salesorderproduct_quantity_dispatched'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesorderproduct',
            name='outward_date_time',
        ),
    ]
