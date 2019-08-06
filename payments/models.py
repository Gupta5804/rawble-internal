from django.db import models
from ordered_model.models import OrderedModel
from contacts.models import ContactVendor
import datetime
from contacts.models import ContactVendor

class PaymentPayable(models.Model):
    
    mode = models.CharField(max_length=200,null=True,blank=True)
    vendor = models.ForeignKey(ContactVendor, on_delete = models.SET_NULL,null=True,blank=True)

class ChequePayable(models.Model):
    paymentpayable = models.ForeignKey(PaymentPayable,on_delete = models.CASCADE)
    cheque_no = models.CharField(max_length=200,null=True,blank=True)
    date = models.DateField()
    amount = models.FloatField()
    
