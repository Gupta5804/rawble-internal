from django.shortcuts import render,redirect
from products.models import Product
from django.contrib.auth.models import User
from contacts.models import ContactBuyer, ContactVendor
from deals.models import ZohoEstimate, VendorProductVariation
from django.core.management import call_command
from datetime import datetime
from deals.models import ZohoPurchaseOrder

def dashboard(request):
        #total_products = Product.objects.count()
        #total_users = User.objects.count()
        #total_vendors = ContactVendor.objects.count()
        #total_buyers = ContactBuyer.objects.count()
        #total_estimates = ZohoEstimate.objects.count()
        #vendorproductvariations = VendorProductVariation.objects.all()
        #relationship_managers = []
        #for buyer in ContactBuyer.objects.all():
        #        if(buyer.relationship_manager not in relationship_managers):
        #                relationship_managers.append(buyer.relationship_manager)
#
        #month_string = datetime.now().strftime('%B')
        #month_int = datetime.now().strftime('%m')
        user_groups = []
        for group in request.user.groups.all():
            user_groups.append(group.name)
        pos = []
        for po in ZohoPurchaseOrder.objects.all().order_by("-date"):
                if(po.status != "billed" and po.status != "cancelled" and po.planned_status == False):
                        pos.append(po)

        return render(request,'home.html',{'user_groups':user_groups,'pos':pos})

def refresh_contacts(request):
    call_command('contacts_update_from_zoho')
    return redirect('home')
def refresh_products(request):
    call_command('products_update_from_zoho')
    return redirect('home')
    
def SeeAll(request):
    vendorproductvariation = VendorProductVariation.objects.all()
    return render(request, 'seeall.html', {"vendorproductvariation": vendorproductvariation})