from django.db import models
from ordered_model.models import OrderedModel
from contacts.models import ContactVendor
import datetime
from servicedelivery.models import PurchaseOrderProductPlan 
from contacts.models import ContactVendor

class PaymentPayable(models.Model):
    date = models.DateField()
    mode = models.CharField(max_length=200)

class ChequePayable(models.Model):
    paymentpayable = models.ForeignKey(PaymentPayable,on_delete = models.CASCADE)
    cheque_no = models.CharField(max_length=200)
    vendor = models.ForeignKey(ContactVendor, on_delete = models.SET_NULL)
    amount = models.FloatField()
    
