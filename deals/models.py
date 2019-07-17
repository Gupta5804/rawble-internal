from django.db import models
from contacts.models import ContactBuyer,ContactVendor
from django.contrib.auth.models import User
from products.models import ProductGroup,Product,Make,Unit
import datetime
from gdstorage.storage import GoogleDriveStorage

gd_storage = GoogleDriveStorage()
#from contacts.models import ContactBuyer , ContactVendor
# Create your models here.




class ZohoEstimate(models.Model):
    estimate_id = models.CharField(max_length=100)
    buyer = models.ForeignKey(ContactBuyer,on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    estimate_number = models.CharField(max_length=100)
    date = models.DateField()
    estimate_url = models.CharField(max_length=300)
    expiry_date = models.DateField()
    delivery_terms = models.CharField(max_length=100)
    total = models.FloatField()
    tool_status = models.CharField(max_length = 100,blank=True, default = '')
    salesperson = models.CharField(max_length = 100,blank=True, default = '')
    zoho_location = models.CharField(max_length = 100,default="okhla",null=True,blank=True)
    def __str__(self):
        return str(self.estimate_number)
    @property
    def total_products(self):

        return self.estimateproduct_set.all().count()
    @property
    def products_left(self):
        return self.estimateproduct_set.filter(vendorproductvariation = None).count()

class ZohoSalesOrder(models.Model):
    salesorder_id = models.CharField(max_length=100)
    buyer = models.ForeignKey(ContactBuyer,on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    salesorder_number = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=100)
    date = models.DateField()
    total = models.FloatField()
    salesorder_url = models.CharField(max_length=300,default='',blank=True)
    tool_status = models.CharField(max_length = 100,blank=True, default = '')
    salesperson = models.CharField(max_length = 100,blank=True, default = '')
    estimate = models.ForeignKey(ZohoEstimate,on_delete=models.CASCADE,null=True,blank=True)
    zoho_location = models.CharField(max_length = 100,default="okhla",null=True,blank=True)

    def __str__(self):
        return str(self.salesorder_number)
   
    @property
    def planned_status(self):
        if(self.salesorderproduct_set.count() > 0):
            status = True
            for sop in self.salesorderproduct_set.all():
                if(sop.planned_status == False):
                    status = False
        else : 
            status = False
        return status 
    @property
    def total_products(self):
        return self.salesorderproduct_set.all().count()
    @property
    def products_left(self):
        return self.salesorderproduct_set.filter(vendorproductvariation = None).count()
    @property
    def products_status(self):
        status=""
        if self.salesorderproduct_set.all().count() > 0:
            status="products_saved"
        return status
class ZohoPurchaseOrder(models.Model):
    purchaseorder_id = models.CharField(max_length=100)
    vendor = models.ForeignKey(ContactVendor,on_delete = models.CASCADE )
    purchaseorder_number = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    
    billed_status = models.CharField(max_length=100)
    date = models.DateField()
    
    total = models.FloatField()
    salesorder = models.ForeignKey(ZohoSalesOrder,on_delete = models.SET_NULL ,null=True,blank=True)
    purchaseorder_url = models.CharField(max_length=300,default='',blank=True)
    
    def __str__(self):
        return self.purchaseorder_number

    @property
    def received_status(self):
        
        if(self.purchaseorderproduct_set.count() > 0):
            status = True

            for pop in self.purchaseorderproduct_set.all():
                if ( pop.received_status == False ):
                    status = False
        else:
            status = False
        return status
    
    

class DealVendor(models.Model):
    DELIVERY_TERMS_CHOICES =(
        ('Door Delivery','Door Delivery'),
        ('Ex-Godown','Ex-Godown'),
        ('FOR','FOR'),
        ('Local Transport','Local Transport')
    )
    vendor = models.ForeignKey(ContactVendor,on_delete=models.CASCADE,verbose_name='Vendor')
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    delivery_terms = models.CharField(max_length=40 , choices=DELIVERY_TERMS_CHOICES , default='')
    payment_terms = models.CharField(max_length =100,blank=True)
    time_created = models.DateTimeField(auto_now=True,editable=False)
    relationship_manager = models.CharField(max_length=100,blank=True)
    date = models.DateField(null=True)
    def __str__(self):
        return ("Deal of " + self.vendor.contact_name)

    def save(self,*args,**kwargs):
        self.relationship_manager = self.vendor.relationship_manager
        self.payment_terms = self.vendor.payment_terms
        super(DealVendor,self).save(*args,**kwargs)

class DealVendorProduct(models.Model):
    label_name = models.CharField(max_length=300,blank=True,default='')
    deal = models.ForeignKey(DealVendor,on_delete=models.CASCADE,null=True)
    
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    specs = models.CharField(max_length=30,blank=True)
    quantity = models.FloatField(blank=True,null=True)


    vendor_price = models.FloatField()

    make = models.ForeignKey(Make,max_length = 50,default=None,null=True,blank=True,on_delete=models.SET_DEFAULT)
    unit = models.ForeignKey(Unit,max_length=50,default=None,null=True,blank=True,on_delete=models.SET_DEFAULT)
    price_valid_till = models.DateField(blank=True,default=None,null=True)
    lead_time = models.IntegerField(blank=True,null=True)

    def __str__(self):

        return (self.deal.vendor.contact_name + "(label_name = " + self.label_name +" )" )
    @property
    def expiry_status(self):
        if(self.price_valid_till):
            pass
            
        else:
            self.price_valid_till =  datetime.date.today() - datetime.timedelta(days = 1)
            self.save()
        return (self.price_valid_till - datetime.date.today() ).days
    def save(self,*args,**kwargs):
        
        super(DealVendorProduct,self).save(*args,**kwargs)
        dealproduct = self
        
        try:
            vendorproduct = VendorProduct.objects.get(product = dealproduct.product ,  vendor=dealproduct.deal.vendor)
            try:
                vendorproductvariation = VendorProductVariation.objects.get(vendorproduct = vendorproduct ,dealvendorproduct__specs = dealproduct.specs , dealvendorproduct__quantity = dealproduct.quantity)
                vendorproductvariation.dealvendorproduct = DealVendorProduct.objects.get(id = dealproduct.id)
                vendorproductvariation.save()                
            except:
                vendorproductvariation = VendorProductVariation(vendorproduct = vendorproduct , dealvendorproduct = dealproduct)
                vendorproductvariation.save()
        except:
            vendorproduct = VendorProduct(vendor=dealproduct.deal.vendor, product=dealproduct.product)
            vendorproduct.save()
            vendorproductvariation = VendorProductVariation(vendorproduct=vendorproduct, dealvendorproduct=self)
            vendorproductvariation.save()
        

class VendorProduct(models.Model):
    vendor = models.ForeignKey(ContactVendor, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
class BuyerProduct(models.Model):
    buyer = models.ForeignKey(ContactBuyer,on_delete = models.CASCADE)
    product = models.ForeignKey(Product,on_delete = models.CASCADE)    
    last_selling_price = models.FloatField(null=True,blank=True,default=None)
    average_selling_price = models.FloatField(null=True,blank=True,default=None)
    frequency = models.FloatField(null=True,blank=True,default=None)
    total_quantity = models.FloatField(null=True,blank=True,default=None)
    total_so = models.FloatField(null=True,blank=True,default=None)

class BuyerProductCoaFile(models.Model):
    buyerproduct = models.ForeignKey(BuyerProduct, on_delete = models.CASCADE)
    
    file = models.FileField(upload_to='buyer/coa_files/', storage=gd_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.file.file.name

class BuyerProductMonthTarget(models.Model):
    buyerproduct = models.ForeignKey(BuyerProduct,on_delete = models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    targetprice = models.FloatField()
    targetquantity = models.FloatField()

class BuyerProductMonthSales(models.Model):
    buyerproduct = models.ForeignKey(BuyerProduct,on_delete = models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    so_count = models.IntegerField()
    total_quantity = models.FloatField()
    total_sales = models.FloatField()


class VendorProductVariation(models.Model):
    vendorproduct = models.ForeignKey(VendorProduct, on_delete=models.CASCADE)
    dealvendorproduct = models.ForeignKey(DealVendorProduct, on_delete=models.CASCADE)

    def __str__(self):
    
        return("vpv vp-"+str(self.vendorproduct.id)+"[ vendor = "+self.vendorproduct.vendor.contact_name+" || product = "+self.vendorproduct.product.name+" || deal_id = "+str(self.dealvendorproduct.deal.id)+" ]")


class EstimateProduct(models.Model):
    estimate = models.ForeignKey(ZohoEstimate, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendorproductvariation = models.ForeignKey(VendorProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length = 100, default='unselected')
    quantity = models.FloatField(blank=True, null=True)
    pack_size = models.IntegerField(blank=True, null=True)
    estimate_selling_price = models.FloatField(blank=True, null=True,default=0.0)
    def save(self,*args,**kwargs):
        
        super(EstimateProduct,self).save(*args,**kwargs)
        estimateproduct = self
        
        try:
            buyerproduct = BuyerProduct.objects.get(product = estimateproduct.product ,  buyer=estimateproduct.estimate.buyer)
            
        except:
            buyerproduct = BuyerProduct(buyer=estimateproduct.estimate.buyer,product = estimateproduct.product)
            buyerproduct.save()
    @property
    def amount(self):
        try:
            return (self.estimate_selling_price * self.quantity)
        except:
            return 0
    @property
    def hiya(self):
        if("hiya" in self.product.make.lower()):
            return True
        else:
            return False        
    @property
    def selling_price(self):
        if(self.vendorproductvariation):
            pp = self.vendorproductvariation.dealvendorproduct.vendor_price
            vendor_freight = self.vendorproductvariation.vendorproduct.vendor.freight_per_kg
            customer_freight = self.estimate.buyer.freight_per_kg
            pp2 = pp + vendor_freight
            bpt = self.estimate.buyer.payment_terms_no
            vpt = self.vendorproductvariation.vendorproduct.vendor.payment_terms_no
            if (abs(bpt - vpt) <= 15):
                sp = ( pp * ( 1.07 + 0.0005*( bpt - vpt ) ) ) + customer_freight + vendor_freight
            else:
                sp = ( pp * ( 1.10 + 0.0005*( bpt - vpt ) ) ) + customer_freight + vendor_freight
            return sp

        else:
            return "No Purchase Price Selected"
    def payment_cycle(self):
        if(self.vendorproductvariation ):
            bpt = self.estimate.buyer.payment_terms_no
            vpt = self.vendorproductvariation.vendorproduct.vendor.payment_terms_no

            return (bpt - vpt)
        else:
            return "No Purchase Price Selected"
            
    def save(self,*args,**kwargs):
        if(self.vendorproductvariation):
            self.status = 'selected'
        else:
            self.status = 'unselected'
        
        super(EstimateProduct,self).save(*args,**kwargs)
class SalesOrderProduct(models.Model):
    salesorder = models.ForeignKey(ZohoSalesOrder,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendorproductvariation = models.ForeignKey(VendorProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.FloatField(blank=True, null=True)
    
    
    pack_size = models.IntegerField(blank=True, null=True)
    
    so_selling_price = models.FloatField(blank=True, null=True)
    
    
    
    
    def __str__(self):
        return (self.salesorder.salesorder_number + " product: " + self.product.name)
    def save(self,*args,**kwargs):
        
        super(SalesOrderProduct,self).save(*args,**kwargs)
        salesorderproduct = self
        
        try:
            buyerproduct = BuyerProduct.objects.get(product = salesorderproduct.product ,  buyer=salesorderproduct.salesorder.buyer)
            
        except:
            buyerproduct = BuyerProduct(buyer=salesorderproduct.salesorder.buyer,product = salesorderproduct.product)
            buyerproduct.save()
    
    @property
    def above_base_price(self):
        try:
            if(self.so_selling_price > float(self.selling_price)):
                return True
            else:
                return False
        except:
            return False
    @property
    def amount(self):
        try:
            return (self.so_selling_price * self.quantity )
        except:
            return 0
    @property
    def hiya(self):
        if("hiya" in self.product.make.lower()):
            return True
        else:
            return False
    @property
    def margin_percentage(self):
        try:
            return (self.margin / (self.amount)) * 100
        except:
            return 0
    @property
    def margin(self):
        try:
            margin = (self.so_selling_price - (self.vpv.dealvendorproduct.vendor_price + self.vpv.vendorproduct.vendor.freight_per_kg + self.salesorder.buyer.freight_per_kg +0.0005 *(self.salesorder.buyer.payment_terms_no - self.vpv.vendorproduct.vendor.payment_terms_no))) * self.quantity
            return margin
        except:
            return 0
    @property
    def vpv(self):
        if(self.vendorproductvariation == None):
            estimate = self.salesorder.estimate
            if(estimate == None):
                return None
            else:
                try:
                    estimateproduct = estimate.estimateproduct_set.get(product = self.product)
                    return estimateproduct.vendorproductvariation
                except:
                    return None
               
        else:
            return self.vendorproductvariation    

    @property
    def planned_status(self):
        sum_quantity = 0
        for sopp in self.salesorderproductplan_set.all():
            sum_quantity = sum_quantity + sopp.planned_quantity
        if sum_quantity >= self.quantity:
            return True
        else:
            return False
    @property
    def quantity_dispatched(self):
        quantity_dispatched = 0
        for sopp in self.salesorderproductplan_set.all():
            if(sopp.plan_status == "in-transit" or sopp.plan_status == "delivered"):

                quantity_dispatched = quantity_dispatched + sopp.planned_quantity
        return quantity_dispatched
    @property 
    def quantity_to_plan_max(self):
        quantity_dispatched = 0
        for sopp in self.salesorderproductplan_set.all():
            quantity_dispatched=quantity_dispatched+ sopp.planned_quantity
        return (self.quantity - quantity_dispatched)
    @property
    def selling_price(self):
        if(self.vpv):
            pp = self.vpv.dealvendorproduct.vendor_price
            vendor_freight = self.vpv.vendorproduct.vendor.freight_per_kg
            customer_freight = self.salesorder.buyer.freight_per_kg
            pp2 = pp + vendor_freight
            bpt = self.salesorder.buyer.payment_terms_no
            vpt = self.vpv.vendorproduct.vendor.payment_terms_no
            if (abs(bpt - vpt) <= 15):
                sp = ( pp * ( 1.07 + 0.0005*( bpt - vpt ) ) ) + customer_freight + vendor_freight
            else:
                sp = ( pp * ( 1.10 + 0.0005*( bpt - vpt ) ) ) + customer_freight + vendor_freight
            return sp

        else:
            return "No Purchase Price Selected"
    def payment_cycle(self):
        if(self.vpv ):
            bpt = self.salesorder.buyer.payment_terms_no
            vpt = self.vpv.vendorproduct.vendor.payment_terms_no

            return (bpt - vpt)
        else:
            return "No Purchase Price Selected"

class PurchaseOrderProduct(models.Model):
    
    purchaseorder = models.ForeignKey(ZohoPurchaseOrder,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete = models.CASCADE)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=5)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=5,default=0.0)
    quantity_to_receive = models.DecimalField(max_digits=10, decimal_places=5,default=0.0)
    pack_size = models.DecimalField(max_digits=10, decimal_places=5)
    pickup_date_time = models.DateTimeField(null=True,blank=True,default=None)
    transporter_detail = models.CharField(max_length=300,null=True,blank=True,default='')
    freight = models.FloatField(blank=True,null=True,default=0.0)
    

    @property 
    def received_status(self):
        if self.quantity_received >= self.quantity:
            return True
        else:
            return False
    @property
    def quantity_to_receive_max(self):
        return (self.quantity - self.quantity_received)   