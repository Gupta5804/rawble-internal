# Generated by Django 2.1.4 on 2019-08-05 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20190709_1348'),
        ('payments', '0002_auto_20190118_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChequePayable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cheque_no', models.CharField(blank=True, max_length=200, null=True)),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='PaymentPayable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('mode', models.CharField(blank=True, max_length=200, null=True)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.ContactVendor')),
            ],
        ),
        migrations.RemoveField(
            model_name='payment',
            name='vendor',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.AddField(
            model_name='chequepayable',
            name='paymentpayable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.PaymentPayable'),
        ),
    ]
