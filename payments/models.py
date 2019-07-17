from django.db import models
from ordered_model.models import OrderedModel
from contacts.models import ContactVendor
import datetime
# Create your models here.
class Payment(OrderedModel):
    DELIVERY_TERMS_CHOICES =(
        ('Door Delivery','Door Delivery'),
        ('Ex-Godown','Ex-Godown'),
        ('FOR','FOR'),
        ('Local Transport','Local Transport')
    )
    PAYMENT_TYPE_CHOICES =(
    ('advance','advance'),
    ('unpaid_bill','unpaid_bill')
    )
    payment_type = models.CharField(max_length=50,choices =PAYMENT_TYPE_CHOICES,default='advance')
    vendor = models.ForeignKey(ContactVendor,on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_terms = models.CharField(max_length=100,blank=True)
    reason = models.CharField(max_length=100,blank=True)
    comment = models.CharField(max_length=100,blank=True)
    date = models.DateField(blank=True,null=True)

    time_created = models.DateTimeField(auto_now=True,editable=False)
    delivery_terms = models.CharField(max_length=40 , choices=DELIVERY_TERMS_CHOICES , default='')
    bill_id = models.CharField(max_length = 90 , blank=True, default= '')
    bill_number = models.CharField(max_length = 100 , blank=True,default='')
    due_date = models.DateField(blank=True,default="1111-11-11")
    bill_url = models.CharField(max_length=300,blank=True,default='')
    bill_status = models.CharField(max_length=60,blank=True,default='')
    due_days = models.CharField(max_length=150,blank=True,default='')
    bill_total = models.CharField(max_length=200,blank=True,default='')
    bill_time_created = models.CharField(max_length=200,blank=True,default='')
    check_sent_status = models.BooleanField(default = False)
    def __str__(self):
        return(self.payment_type +" Payment for "+ self.vendor.contact_name + " of " + str(self.amount))
    def save(self,*args,**kwargs):
        self.payment_terms = self.vendor.payment_terms

        super(Payment,self).save(*args,**kwargs)
