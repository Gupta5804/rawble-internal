from django.db import models
from deals.models import SalesOrderProduct
from products.models import CoaFile

# Create your models here.
class Transporter(models.Model):
    name = models.CharField(max_length=400,blank=True,null=True)
    address = models.CharField(max_length=400,blank=True,null=True)
    contact_person = models.CharField(max_length=400,blank=True,null=True)
    phone_number = models.CharField(max_length=400,blank=True,null=True)
    website_url = models.CharField(max_length=400,blank=True,null=True)
    def __str__(self):
        return self.name
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
