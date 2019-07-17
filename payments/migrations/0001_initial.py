# Generated by Django 2.1.4 on 2019-01-17 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('payment_type', models.CharField(choices=[('advance', 'advance'), ('unpaid_bill', 'unpaid_bill')], default='advance', max_length=50)),
                ('amount', models.FloatField()),
                ('payment_terms', models.CharField(blank=True, max_length=100)),
                ('reason', models.CharField(blank=True, max_length=100)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('date', models.DateField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now=True)),
                ('delivery_terms', models.CharField(choices=[('Door Delivery', 'Door Delivery'), ('Ex-Godown', 'Ex-Godown'), ('FOR', 'FOR'), ('Local Transport', 'Local Transport')], default='', max_length=40)),
                ('bill_id', models.CharField(blank=True, default='', max_length=90)),
                ('bill_number', models.CharField(blank=True, default='', max_length=100)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('bill_url', models.CharField(blank=True, default='', max_length=300)),
                ('bill_status', models.CharField(blank=True, default='', max_length=60)),
                ('due_days', models.CharField(blank=True, default='', max_length=150)),
                ('bill_total', models.CharField(blank=True, default='', max_length=200)),
                ('bill_time_created', models.CharField(blank=True, default='', max_length=200)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.ContactVendor')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
    ]
