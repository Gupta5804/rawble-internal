from django.db import models
from gdstorage.storage import GoogleDriveStorage
from django.contrib.auth.models import User
# Define Google Drive Storage
gd_storage = GoogleDriveStorage()


class ProductGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):

    STATUS_CHOICES = (
        ('Ac', 'active'),
        ('In', 'inactive')
    )
    group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    item_id = models.BigIntegerField(primary_key=True)
    hsn_or_sac = models.CharField(max_length=500)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, blank=True)
    unit = models.CharField(max_length=50)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='In')
    product_type = models.CharField(max_length=50)
    sku = models.CharField(max_length=500)
    make = models.CharField(max_length=100, default=" ", blank=True)
    stock_on_hand = models.IntegerField(default=0)
    zoho_location = models.CharField(max_length=200,default="okhla",null=True,blank=True)
    
    def is_active(self):
        return self.status is 'Ac'

    def __str__(self):
        return self.name

    @property
    def name_search(self):
        name_search = self.name.replace(" ", "+")
        return name_search
    
    @property
    def item_id_str(self):
        return str(self.item_id)


class CoaFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to='coa_files/', storage=gd_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.file.file.name


class Make(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Unit(models.Model):

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
