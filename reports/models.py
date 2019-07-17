from django.db import models
from products.models import Product


class Invoice(models.Model):

    invoice_id = models.BigIntegerField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    date = models.DateField()
    quantity = models.FloatField()
    url = models.CharField(max_length = 500)
    price = models.FloatField()

class Bill(models.Model):

    bill_id = models.BigIntegerField()
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length = 300)
    quantity = models.FloatField()
    date= models.DateField()
    price = models.FloatField()

# Create your models here.
