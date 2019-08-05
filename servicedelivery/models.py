from django.db import models
from deals.models import SalesOrderProduct,PurchaseOrderProduct
from products.models import CoaFile
from payments.models import PaymentPayable
#from payments.models import PaymentPayable
# Create your models here. 
class Transporter(models.Model):
    name = models.CharField(max_length=400,blank=True,null=True)
    address = models.CharField(max_length=400,blank=True,null=True)
    contact_person = models.CharField(max_length=400,blank=True,null=True)
    phone_number = models.CharField(max_length=400,blank=True,null=True)
    website_url = models.CharField(max_length=400,blank=True,null=True)
    def __str__(self):
        return self.name

class PurchaseOrderProductPlan(models.Model):
    purchaseorderproduct = models.ForeignKey(PurchaseOrderProduct,on_delete=models.CASCADE)
    planned_dispatch_date_time = models.DateTimeField(null=True,blank=True)
    planned_receive_date_time = models.DateTimeField(null=True,blank=True)
    dispatched_date_time = models.DateTimeField(null=True,blank=True)
    received_date_time = models.DateTimeField(null=True,blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    planned_quantity = models.FloatField()
    freight = models.FloatField()
    transporter = models.ForeignKey(Transporter,on_delete=models.SET_NULL,null=True,blank=True)
    dispatch_delay_reason = models.CharField(max_length = 500 , null=True, blank=True)
    receive_delay_reason = models.CharField(max_length = 500 , null=True, blank=True)
    #paymentpayable = models.ForeignKey(PaymentPayable,on_delete=models.SET_NULL)
    paymentpayable = models.ForeignKey(PaymentPayable,on_delete=models.SET_NULL,null=True,default=None)
    def __str__(self):
        return (self.purchaseorderproduct.purchaseorder.purchaseorder_number + "-" + self.purchaseorderproduct.product.name + "-"+str(self.planned_quantity))
    
    @property
    def total_amount_with_tax(self):
        return (self.total_amount_without_tax + self.tax_amount )
    @property
    def tax_amount(self):
        return (self.total_amount_without_tax * self.purchaseorderproduct.tax_percentage * 0.01)
    @property
    def total_amount_without_tax(self):
        return (self.purchaseorderproduct.purchase_price * self.planned_quantity)
    @property
    def plan_status(self):
        if(self.received_date_time):
            return "received"
        elif(self.dispatched_date_time):
            return "in-transit"
        elif(self.planned_dispatch_date_time):
            return "planned"
        else:
            return "unplanned"
    
class SalesOrderProductPlan(models.Model):
    salesorderproduct = models.ForeignKey(SalesOrderProduct,on_delete=models.CASCADE)
    planned_date_time = models.DateTimeField(null=True,blank=True)
    shipped_date_time = models.DateTimeField(null=True,blank=True)
    delivered_date_time = models.DateTimeField(null=True,blank=True)
    planned_quantity = models.FloatField()
    tracking_number = models.CharField(max_length=300,null=True,blank=True)
    transporter = models.ForeignKey(Transporter,on_delete=models.SET_NULL,null=True,blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    freight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add = True)
    reschedule_reason = models.CharField(max_length = 500 , null=True, blank=True)
    tracking_status = models.CharField(max_length=300 ,null=True,blank=True )
    lr_mailsent_status= models.BooleanField(default=False)
    eta = models.DateTimeField(null=True,blank=True,default=None)
    coafile = models.ForeignKey(CoaFile,on_delete=models.SET_NULL,null=True,blank=True,default=None)
    def __str__(self):
        return (self.salesorderproduct.salesorder.salesorder_number + "-" + self.salesorderproduct.product.name + "-" +str(self.planned_quantity) )
    @property
    def total_amount(self):
        return (self.salesorderproduct.so_selling_price * self.planned_quantity )
    @property
    def plan_status(self):
        if(self.delivered_date_time):
            return "delivered"
        elif(self.shipped_date_time):
            return "in-transit"
        elif(self.planned_date_time):
            return "planned"
        else:
            return "un-planned"
