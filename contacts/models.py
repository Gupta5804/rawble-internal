from django.db import models
from products.models import Product



# Create your models here.
class ContactBuyer(models.Model):
    STATUS_CHOICES = (
        ('Ac','active'),
        ('In','inactive')
    )

    #CONTACT_TYPE_CHOICES =(
    #    ('C','customer'),
    #    ('V','vendor')
    #)
    contact_id = models.BigIntegerField(primary_key = True)
    contact_name = models.CharField(max_length = 100)
    website = models.CharField(max_length=100)
    #contact_type = models.CharField(max_length = 2 , choices = CONTACT_TYPE_CHOICES,default = 'C')
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    status = models.CharField(max_length = 2  , choices = STATUS_CHOICES , default = 'In')
    email = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 30)
    mobile = models.CharField(max_length = 30)
    payment_terms = models.CharField(max_length = 50)
    outstanding_receivable = models.FloatField()
    outstanding_payable = models.FloatField()
    place_of_contact = models.CharField(max_length = 100)
    currency_code = models.CharField(max_length = 100)
    relationship_manager = models.CharField(max_length = 100)
    gst_no = models.CharField(max_length=100)
    freight_per_kg = models.FloatField(default=0.00)
    place_of_contact = models.CharField(max_length=200)
    zoho_location = models.CharField(max_length=200,default="okhla",null=True,blank=True)
    def __str__(self):
        return self.contact_name
    def is_active(self):
        return self.status is 'Ac'
    #def is_customer(self):
    #    return self.contact_type is 'C'
    #def is_vendor(self):
    #    return self.contact_type is 'V'    
    @property
    def payment_terms_no(self):
        if(self.payment_terms == "Due On Receipt" or self.payment_terms == "Due on delivery"):
            return 0
        elif(self.payment_terms == "Advance"):
            return 7
        else:
            try:
                return(int(self.payment_terms.split()[1]))
            except:
                pass
    
class ContactVendor(models.Model):
    STATUS_CHOICES = (
        ('Ac','active'),
        ('In','inactive')
    )

    #CONTACT_TYPE_CHOICES =(
    #    ('C','customer'),
    #    ('V','vendor')
    #)
    contact_id = models.BigIntegerField(primary_key = True)
    contact_name = models.CharField(max_length = 100)
    website = models.CharField(max_length=100)
    #contact_type = models.CharField(max_length = 2 , choices = CONTACT_TYPE_CHOICES,default = 'C')
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    status = models.CharField(max_length = 2  , choices = STATUS_CHOICES , default = 'In')
    email = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 30)
    mobile = models.CharField(max_length = 30)
    payment_terms = models.CharField(max_length = 50)
    outstanding_receivable = models.FloatField()
    outstanding_payable = models.FloatField()
    place_of_contact = models.CharField(max_length = 100)
    currency_code = models.CharField(max_length = 100)
    relationship_manager = models.CharField(max_length = 100)
    gst_no = models.CharField(max_length=100)
    place_of_contact = models.CharField(max_length=200,default = '',null=True,blank=True)
    freight_per_kg = models.FloatField(default=0.00)
    zoho_location = models.CharField(max_length=200,default="okhla",null=True,blank=True)
    def __str__(self):
        return self.contact_name
    def is_active(self):
        return self.status is 'Ac'
    #def is_customer(self):
    #    return self.contact_type is 'C'
    #def is_vendor(self):
    #    return self.contact_type is 'V'

    @property
    def payment_terms_no(self):
        if(self.payment_terms == "Due On Receipt" or self.payment_terms == "Due on delivery"):
            return 0
        elif(self.payment_terms == "Advance"):
            return 7
        else:
            try:
                return(int(self.payment_terms.split()[1]))
            except:
                pass