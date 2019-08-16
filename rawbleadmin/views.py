from django.shortcuts import render,redirect
from products.models import Product
from django.contrib.auth.models import User
from contacts.models import ContactBuyer, ContactVendor
from deals.models import ZohoEstimate, VendorProductVariation
from django.core.management import call_command
from datetime import datetime
from deals.models import ZohoPurchaseOrder,ZohoSalesOrder
from servicedelivery.models import PurchaseOrderProductPlan,SalesOrderProductPlan
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
        popps_expired = []
        popps_expired_amount = 0
        popps_intransit= []
        popps_intransit_amount = 0
        sos = []
        for po in ZohoPurchaseOrder.objects.all().order_by("-date"):
                if(po.status != "billed" and po.status != "cancelled" and po.planned_status == False):
                        pos.append(po)
        for so in ZohoSalesOrder.objects.all().order_by("-date"):
                if(so.status == "open" and so.planned_status == False):
                        sos.sppend(so)

        for popp in PurchaseOrderProductPlan.objects.all().order_by("-purchaseorderproduct__purchaseorder__purchaseorder_number"):
                if(popp.plan_status == "planned"):
                        popps_expired.append(popp)
                        popps_expired_amount = popps_expired_amount + popp.total_amount_with_tax
                elif(popp.plan_status == "in-transit"):
                        popps_intransit.append(popp)
                        popps_intransit_amount = popps_intransit_amount + popp.total_amount_with_tax
        return render(request,'home.html',{'user_groups':user_groups,'pos':pos,'sos':sos,'popps_expired':popps_expired,'popps_expired_amount':popps_expired_amount,'popps_intransit':popps_intransit,'popps_intransit_amount':popps_intransit_amount })

def refresh_contacts(request):
    call_command('contacts_update_from_zoho')
    return redirect('home')
def refresh_products(request):
    call_command('products_update_from_zoho')
    return redirect('home')
    
def SeeAll(request):
    vendorproductvariation = VendorProductVariation.objects.all()
    return render(request, 'seeall.html', {"vendorproductvariation": vendorproductvariation})