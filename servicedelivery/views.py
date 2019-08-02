from django.shortcuts import render,redirect
from deals.models import ZohoPurchaseOrder,PurchaseOrderProduct,ZohoSalesOrder,SalesOrderProduct,BuyerProductCoaFile
from contacts.models import ContactBuyer
from django.core.management import call_command
import requests
from django.template.loader import render_to_string
import json
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from products.models import Product , CoaFile
from datetime import date
import datetime
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
from servicedelivery.models import Transporter , SalesOrderProductPlan,PurchaseOrderProductPlan
from servicedelivery.filters import SOPPFilter
from django.db.models import Q
# Create your views here.
def nextoutward_summary(request):
    today = date.today()
    day = today
    for i in range(10):
        if(day.weekday() in [0,2,4]):
            next_outward_date = day
            break
        day = day + datetime.timedelta(days=1)
    day= today
    for p in range(10):
        day = day - datetime.timedelta(days=1)
        if(day.weekday() in [0,2,4]):
            previous_outward_date = day
            break
    sopps = SalesOrderProductPlan.objects.filter(planned_date_time__date = next_outward_date).order_by("-salesorderproduct__salesorder__salesorder_number")
    planned_total_amount = 0
    dispatched_total_amount = 0
    for sopp in sopps:
        planned_total_amount = planned_total_amount + sopp.total_amount
        if(sopp.plan_status == "in-transit" or sopp.plan_status == "delivered"):
            dispatched_total_amount = dispatched_total_amount + sopp.total_amount
    dispatch_percentage = 0
    try:
        dispatch_percentage = (dispatched_total_amount / planned_total_amount)* 100
    except:
        pass
        
    rendered = render_to_string('servicedelivery/helper_ajax/nextoutward_summary.html', context = {'sopps':sopps,'next_outward_date':next_outward_date,'planned_total_amount':planned_total_amount , 'dispatched_total_amount':dispatched_total_amount,'dispatch_percentage':dispatch_percentage} ,request=request)
    return  JsonResponse({'snippet':rendered})
def nextoutward_dispatch(request):
    today = date.today()
    day = today
    for i in range(10):
        if(day.weekday() in [0,2,4]):
            next_outward_date = day
            break
        day = day + datetime.timedelta(days=1)
    day= today
    for p in range(10):
        day = day - datetime.timedelta(days=1)
        if(day.weekday() in [0,2,4]):
            previous_outward_date = day
            break
    sopps = SalesOrderProductPlan.objects.filter(planned_date_time__date = next_outward_date).order_by("-salesorderproduct__salesorder__salesorder_number")
    planned_total_amount = 0
    dispatched_total_amount = 0
    for sopp in sopps:
        planned_total_amount = planned_total_amount + sopp.total_amount
        if(sopp.plan_status == "in-transit" or sopp.plan_status == "delivered"):
            dispatched_total_amount = dispatched_total_amount + sopp.total_amount
    dispatch_percentage = 0
    try:
        dispatch_percentage = (dispatched_total_amount / planned_total_amount)* 100
    except:
        pass
        
    rendered = render_to_string('servicedelivery/helper_ajax/nextoutward_dispatch.html', context = {'sopps':sopps,'next_outward_date':next_outward_date,'planned_total_amount':planned_total_amount , 'dispatched_total_amount':dispatched_total_amount,'dispatch_percentage':dispatch_percentage} ,request=request)
    return  JsonResponse({'snippet':rendered})
def previousoutward(request):
    today = date.today()
    day = today
    for i in range(10):
        if(day.weekday() in [0,2,4]):
            next_outward_date = day
            break
        day = day + datetime.timedelta(days=1)
    day= today
    for p in range(10):
        day = day - datetime.timedelta(days=1)
        if(day.weekday() in [0,2,4]):
            previous_outward_date = day
            break
    sopps = SalesOrderProductPlan.objects.filter(planned_date_time__date = previous_outward_date).order_by("-salesorderproduct__salesorder__salesorder_number")
    planned_total_amount = 0
    dispatched_total_amount = 0
    for sopp in sopps:
        planned_total_amount = planned_total_amount + sopp.total_amount
        if(sopp.plan_status == "in-transit" or sopp.plan_status == "delivered"):
            dispatched_total_amount = dispatched_total_amount + sopp.total_amount
    dispatch_percentage = 0
    try:
        dispatch_percentage = (dispatched_total_amount / planned_total_amount)* 100
    except:
        pass
        
    rendered = render_to_string('servicedelivery/helper_ajax/previousoutward.html', context = {'sopps':sopps,'previous_outward_date':previous_outward_date,'planned_total_amount':planned_total_amount , 'dispatched_total_amount':dispatched_total_amount,'dispatch_percentage':dispatch_percentage} ,request=request)
    return  JsonResponse({'snippet':rendered})

def inward_servicedelivery_stock(request):
    return render(request,'servicedelivery/inward_stock.html')
def inward_servicedelivery_intransit(request):
    if request.method == "GET":
        popps = PurchaseOrderProductPlan.objects.filter(planned_receive_date_time__date__lt = date.today())
        popps_intransit = []
        for popp in popps:
            if(popp.plan_status == 'in-transit'):
                popps_intransit.append(popp)
        
        
        return render(request,'servicedelivery/inward_intransit.html',{'popps_intransit':popps_intransit})
    if request.method == "POST":
        if "replan" in request.POST:
            selected_popp_ids = request.POST.getlist('selected_popp_id')
            
            planned_receive_date_time = request.POST.get('planned_receive_date_time')
            receive_delay_reason = request.POST.get('receive_delay_reason')
            popp_email = []
            for selected_popp_id in selected_popp_ids:
                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
               
                popp.planned_receive_date_time = planned_receive_date_time
                popp.receive_delay_reason = receive_delay_reason
                popp.save()
                popp_email.append(popp)
            if(popp_email):
                subject = "Items Rescheduled to Receive"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    
                    'planned_receive_date_time':planned_receive_date_time,
                    'dispatch_delay_reason':dispatch_delay_reason,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/receive_delay_reason.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "mark-as-received" in request.POST:
            selected_popp_ids = request.POST.getlist('selected_popp_id')
            popp_email = []
            for selected_popp_id in selected_popp_ids:
                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
                popp.dispatched_date_time = popp.planned_dispatch_date_time
                popp.save()
                popp_email.append(popp)
            if(popp_email):
                subject = "Items Received Today"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/received_today.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        
        return redirect('inward_servicedelivery_intransit')
def inward_servicedelivery_report(request):
    return render(request,'servicedelivery/inward_report.html')
def inward_servicedelivery_expired(request):
    if request.method == "GET":
        popps = PurchaseOrderProductPlan.objects.filter(planned_dispatch_date_time__date__lt = date.today())
        popps_expired = []
        for popp in popps:
            if(popp.plan_status == 'planned'):
                popps_expired.append(popp)
        
        return render(request,'servicedelivery/inward_expired.html',{'popps_expired':popps_expired})
    if request.method == "POST":
        if "replan" in request.POST:
            selected_popp_ids = request.POST.getlist('selected_popp_id')
            planned_dispatch_date_time = request.POST.get('planned_dispatch_date_time')
            planned_receive_date_time = request.POST.get('planned_receive_date_time')
            dispatch_delay_reason = request.POST.get('dispatch_delay_reason')
            popp_email = []
            for selected_popp_id in selected_popp_ids:
                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
                popp.planned_dispatch_date_time = planned_dispatch_date_time
                popp.planned_receive_date_time = planned_receive_date_time
                popp.dispatch_delay_reason = dispatch_delay_reason
                popp.save()
                popp_email.append(popp)
            if(popp_email):
                subject = "Items Rescheduled to Dispatch From Vendor's End"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    'planned_dispatch_date_time':planned_dispatch_date_time,
                    'planned_receive_date_time':planned_receive_date_time,
                    'dispatch_delay_reason':dispatch_delay_reason,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/dispatch_delay_reason.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "mark-as-dispatched" in request.POST:
            selected_popp_ids = request.POST.getlist('selected_popp_id')
            popp_email = []
            for selected_popp_id in selected_popp_ids:
                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
                popp.dispatched_date_time = popp.planned_dispatch_date_time
                popp.save()
                popp_email.append(popp)
            if(popp_email):
                subject = "Items Dispatched From Vendor's End Today"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/dispatched_today.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        return redirect('inward_servicedelivery_expired')    
def salesorder_outward(request):
    salesorder_id = request.GET.get('slug',None)
    salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_ids = {'okhla':'667580392','baddi':'665963577'}
    
    
    organization_id = organization_ids[salesorder.zoho_location]
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.get("https://books.zoho.com/api/v3/salesorders/" + salesorder_id,params = parameters)
    salesorder_api = response.json()['salesorder']
    for item in salesorder_api['line_items']:
        product = Product.objects.get(item_id = item['item_id'])
        item['product'] = product
        for item_custom_field in item['item_custom_fields']:
            if item_custom_field['label'] == 'Pack Size':
                item['pack_size'] = item_custom_field['value']
        try:
            sop = salesorder.salesorderproduct_set.get(product__item_id = item['item_id'])
            item['sop'] = sop
            item['sop_saved'] = True
            
        except:
            item['sop_saved'] = False
    transporters = Transporter.objects.all().order_by("name")
    dispatchdates = []
    today = date.today()
    day = today
    for i in range(30):
        if(day.weekday() in [0,2,4]):
            dispatchdates.append(day)
        day = day + datetime.timedelta(days=1)

    rendered = render_to_string('servicedelivery/helper_ajax/salesorder_outward.html', context = {'salesorder':salesorder,'salesorder_api':salesorder_api, 'transporters':transporters ,'dispatchdates':dispatchdates},request=request)
    
    return JsonResponse({'so_snippet': rendered})
def inward_dispatchtoday(request):
    popps = PurchaseOrderProductPlan.objects.filter(planned_dispatch_date_time__date = date.today())
    popps_undispatched = []
    for popp in popps:
        if(popp.plan_status == "planned"):
            popps_undispatched.append(popp)


    rendered = render_to_string('servicedelivery/helper_ajax/inward_dispatchtoday.html', context = {'popps_undispatched':popps_undispatched},request=request)
    return JsonResponse({'snippet':rendered})
def inward_dispatchtoday_summary(request):
    popps = PurchaseOrderProductPlan.objects.filter(planned_dispatch_date_time__date= date.today())
    

    rendered = render_to_string('servicedelivery/helper_ajax/inward_dispatchtoday_summary.html', context = {'popps':popps},request=request)
    return JsonResponse({'snippet':rendered})
def inward_receivingtoday(request):
    popps = PurchaseOrderProductPlan.objects.filter(planned_receive_date_time__date = date.today())
    popps_unreceived = []
    for popp in popps:
        if(popp.plan_status == "in-transit"):
            popps_unreceived.append(popp)

    rendered = render_to_string('servicedelivery/helper_ajax/inward_receivingtoday.html', context = {'popps_unreceived':popps_unreceived},request=request)
    return JsonResponse({'snippet':rendered})
def inward_receivingtoday_summary(request):
    popps = PurchaseOrderProductPlan.objects.filter(planned_receive_date_time__date = date.today())

    rendered = render_to_string('servicedelivery/helper_ajax/inward_receivingtoday_summary.html', context = {'popps':popps},request=request)
    return JsonResponse({'snippet':rendered})

def purchaseorder_pickup(request):
    
    purchaseorder_id = request.GET.get('slug',None)
    purchaseorder = ZohoPurchaseOrder.objects.get(purchaseorder_id = purchaseorder_id)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.get("https://books.zoho.com/api/v3/purchaseorders/" + purchaseorder_id,params = parameters)
    purchaseorder_api = response.json()['purchaseorder']
    for item in purchaseorder_api['line_items']:
        product = Product.objects.get(item_id = item['item_id'])
        
        item['product'] = product
        for item_custom_field in item['item_custom_fields']:
            if item_custom_field['label'] == 'Pack Size':
                item['pack_size'] = item_custom_field['value']
        
        try:
            pop = purchaseorder.purchaseorderproduct_set.get(product__item_id = item['item_id'])
            item['pop'] = pop
            item['pop_saved'] = True
            
        except:
            item['pop_saved'] = False
    transporters = Transporter.objects.all().order_by("name")  
    rendered = render_to_string('servicedelivery/helper_ajax/purchaseorder_pickup.html', context = {'purchaseorder':purchaseorder,'purchaseorder_api':purchaseorder_api,'transporters':transporters},request=request)
    
    return JsonResponse({'po_snippet': rendered})

def inward_servicedelivery_new(request):
    if request.method == "GET":
        purchase_orders = ZohoPurchaseOrder.objects.all().order_by("-purchaseorder_number")
        return render(request,'servicedelivery/inward_new.html',{'purchaseorders':purchase_orders})
    if request.method == "POST":
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_id = '667580392'
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        if "mail-receive-summary" in request.POST:
            popps = PurchaseOrderProductPlan.objects.filter(planned_receive_date_time__date = date.today())
            if(popps):
                subject = "Items Planned to receive today"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popps:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popps":popps,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/receive_today_summary.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "mail-dispatch-summary" in request.POST:
            popps = PurchaseOrderProductPlan.objects.filter(planned_dispatch_date_time__date = date.today())
            if(popps):
                subject = "Items Planned to Dispatch today From Vendor's End"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popps:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popps":popps,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/dispatch_today_summary.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()    
        if "dispatched-today" in request.POST:
            selected_popp_ids = request.POST.getlist("selected-popp")
            popp_email = []
            for selected_popp_id in selected_popp_ids:

                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
                popp.dispatched_date_time = datetime.datetime.now()
                popp.save()
                popp_email.append(popp)
                ## EMAIL CODE
            if(popp_email):
                subject = "Items Dispatched From Vendor's End Today"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/dispatched_today.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "received-today" in request.POST:
            selected_popp_ids = request.POST.getlist("selected-popp")
            popp_email = []
            for selected_popp_id in selected_popp_ids:

                popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
                popp.received_date_time = datetime.datetime.now()
                popp.save()
                popp_email.append(popp)
                ## EMAIL CODE
            if(popp_email):
                subject = "Items Received Today"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount_without_tax = 0
                total_amount_with_tax = 0
                for popp in popp_email:
                    total_quantity = total_quantity + popp.planned_quantity
                    total_amount_without_tax = total_amount_without_tax + popp.total_amount_without_tax
                    total_amount_with_tax = total_amount_with_tax + popp.total_amount_with_tax
                ctx = {
                    "popp_email":popp_email,
                    #"users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount_without_tax":total_amount_without_tax,
                    "total_amount_with_tax":total_amount_with_tax,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/inward/received_today.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "received-pickup" in request.POST:
            pop_ids = request.POST.getlist("pop_id")
            transporter_details = request.POST.getlist("transporter_detail")
            freights = request.POST.getlist("freight")
            received_pop_ids = request.POST.getlist("received")
            quantity_to_receives = request.POST.getlist("quantity_to_receive")
            print(received_pop_ids)
            for i,pop_id in enumerate(pop_ids):
                if(freights[i] == ''):
                        freight = 0.0
                else:
                    freight = freights[i]
                if(quantity_to_receives[i] == ''):
                    quantity_to_receive = 0.0
                else:
                    quantity_to_receive = quantity_to_receives[i]
                pop = PurchaseOrderProduct.objects.get(id=pop_id)
                pop.transporter_detail = transporter_details[i]
                pop.freight = freight
                pop.quantity_to_receive = quantity_to_receive
                pop.save()
            pop_email = []
            for received_pop_id in received_pop_ids:
                pop_received = PurchaseOrderProduct.objects.get(id=received_pop_id)
                pop_received.quantity_received = pop_received.quantity_received + pop_received.quantity_to_receive
                
                
                pop_received.save()
                pop_email.append(pop_received)
            print(pop_email)
            if(pop_email):
                subject = "Items Received Today (Reminder)"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount = 0
                for pop in pop_email:
                    total_quantity = total_quantity + pop.quantity_to_receive
                    total_amount = total_amount + ( pop.quantity_to_receive * pop.purchase_price )
                ctx = {
                    "pop_email":pop_email,
                    "users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount":total_amount,
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/pickup_received.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()    

        if "po-pickup" in request.POST:
            purchaseorder_id = request.POST.get("purchaseorder_id")
            product_ids = request.POST.getlist("product_id")
            quantitys = request.POST.getlist("quantity")
            planned_quantitys = request.POST.getlist("planned_quantity")
            pack_sizes = request.POST.getlist("pack_size")
            planned_dispatch_date_time = request.POST.get("planned_dispatch_date_time")
            planned_receive_date_time = request.POST.get("planned_receive_date_time")
            purchase_prices = request.POST.getlist("purchase_price")
            transporter_id = request.POST.getlist("transporter_id")
            freight = request.POST.get("freight")
            selected_product_item_ids = request.POST.getlist("selected_product_item_id")
            tax_percentages = request.POST.getlist("tax_percentage")
            purchaseorder = ZohoPurchaseOrder.objects.get(purchaseorder_id=purchaseorder_id)
            if freight == '':
                freight=0
            freight_for_each = float(freight)/len(selected_product_item_ids)
            if ( purchaseorder.purchaseorderproduct_set.count() == 0 ):
                
                for i,product_id in enumerate(product_ids):
                    
                    purchaseorder = ZohoPurchaseOrder.objects.get(purchaseorder_id=purchaseorder_id)
                    product = Product.objects.get(item_id = product_ids[i])
                    
                    
                    pop = PurchaseOrderProduct(
                        purchaseorder=purchaseorder,
                        product=product,
                        purchase_price=purchase_prices[i],
                        quantity=quantitys[i],
                        pack_size=pack_sizes[i],
                        tax_percentage = tax_percentages[i],

                        )
                    
                    pop.save()
                    
            
            for selected_product_item_id in selected_product_item_ids:
                for i,product_id in enumerate(product_ids):
                    if product_id == selected_product_item_id:
                        try:
                            transporter = Transporter.objects.get(id=transporter_id)
                        except:
                            transporter = None
                        popp = PurchaseOrderProductPlan(
                            purchaseorderproduct = purchaseorder.purchaseorderproduct_set.get(product__item_id=product_id),
                            planned_dispatch_date_time = planned_dispatch_date_time,
                            planned_receive_date_time = planned_receive_date_time,
                            freight = freight_for_each,
                            planned_quantity = planned_quantitys[i],
                            transporter = transporter

                        )
                        popp.save()

        return redirect("inward_servicedelivery_new")
                
def todayspickup(request):
    today = date.today()
    purchaseorderproducts = PurchaseOrderProduct.objects.all().filter(pickup_date_time__date=today)
    rendered = render_to_string('servicedelivery/helper_ajax/todayspickup.html', context = {'purchaseorderproducts':purchaseorderproducts} ,request=request)
    return  JsonResponse({'po_snippet':rendered})

def todaysdispatch(request):
    today = date.today()
    salesorderproductplans = SalesOrderProductPlan.objects.filter(planned_date_time__date=today).order_by("salesorderproduct__salesorder__salesorder_number")
    transporters = Transporter.objects.all()
    rendered = render_to_string('servicedelivery/helper_ajax/todaysdispatch.html',context={"salesorderproductplans":salesorderproductplans,"transporters":transporters},request=request)
    return JsonResponse({'po_snippet':rendered})

def outward_servicedelivery_report(request):
    #closed_salesorders = ZohoSalesOrder.objects.filter(status="closed")
    #
    #salesorders = ZohoSalesOrder.objects.all().exclude(id__in=closed_salesorders)
    sopp_list = SalesOrderProductPlan.objects.all().order_by("-salesorderproduct__salesorder__salesorder_number","-created_at")
    sopp_filter = SOPPFilter(request.GET, queryset=sopp_list)
    hiya_dispatched_amount_okhla = 0
    not_hiya_dispatched_amount_okhla = 0
    hiya_dispatched_amount_baddi = 0
    not_hiya_dispatched_amount_baddi = 0
    for sopp in sopp_filter.qs :
        if(sopp.plan_status == "in-transit" or sopp.plan_status == "delivered" ):

            if ("hiya" in sopp.salesorderproduct.product.make.lower()):
                if(sopp.salesorderproduct.salesorder.zoho_location == "okhla"):
                    hiya_dispatched_amount_okhla = hiya_dispatched_amount_okhla + (sopp.total_amount)
                elif(sopp.salesorderproduct.salesorder.zoho_location == "baddi"):
                    hiya_dispatched_amount_baddi = hiya_dispatched_amount_baddi + (sopp.total_amount)
            else:
                if(sopp.salesorderproduct.salesorder.zoho_location == "okhla"):
                    not_hiya_dispatched_amount_okhla = hiya_dispatched_amount_okhla + (sopp.total_amount)
                elif(sopp.salesorderproduct.salesorder.zoho_location == "baddi"):
                    not_hiya_dispatched_amount_baddi = hiya_dispatched_amount_baddi + (sopp.total_amount)
    hiya_pending_amount = 0
    not_hiya_pending_amount = 0
    
    salesorders = ZohoSalesOrder.objects.filter(Q(status="open") | Q(status="approved"))
    uncategorized_pending_amount = 0
    for salesorder in salesorders:
        if(salesorder.salesorderproduct_set.count() == 0):
            uncategorized_pending_amount = uncategorized_pending_amount + salesorder.total
        for sop in salesorder.salesorderproduct_set.all():
            if(salesorder.status == "open" or salesorder.status == "approved"):
                if("hiya" in sop.product.make.lower()):
                    remaining_amount = (sop.quantity - sop.quantity_dispatched) * sop.so_selling_price
                    hiya_pending_amount = hiya_pending_amount + remaining_amount
                
                else:
                    remaining_amount = (sop.quantity - sop.quantity_dispatched) * sop.so_selling_price
                    not_hiya_pending_amount = not_hiya_pending_amount + remaining_amount
               
    #uncategorized_pending_amount = 0
    #hiya_pending_amount = 0
    #hiya_sop = []
    #not_hiya_sop = []
    #not_hiya_pending_amount = 0
    #total_salesorders = salesorders.count()
    #unplanned_so_remaining = 0
    #for salesorder in salesorders:
    #    if salesorder.planned_status == False:
    #        unplanned_so_remaining = unplanned_so_remaining + 1
    #    if(salesorder.salesorderproduct_set.count() == 0):
    #        uncategorized_pending_amount = uncategorized_pending_amount + salesorder.total
    #    else:
    #        for sop in salesorder.salesorderproduct_set.all():
    #            if("hiya" in sop.product.make.lower()):
    #                remaining_amount = (sop.quantity - sop.quantity_dispatched) * sop.so_selling_price
    #                hiya_pending_amount = hiya_pending_amount + remaining_amount
    #                hiya_sop.append(sop)
    #            else:
    #                remaining_amount = (sop.quantity - sop.quantity_dispatched) * sop.so_selling_price
    #                not_hiya_pending_amount = not_hiya_pending_amount + remaining_amount
    #                not_hiya_sop.append(sop)
    #for salesorder_number in ZohoSalesOrder.objects.values_list('salesorder_number', flat=True).distinct():
    #    ZohoSalesOrder.objects.filter(pk__in=ZohoSalesOrder.objects.filter(salesorder_number=salesorder_number)#.values_list('id', flat=True)[1:]).delete()
    #total_pending = uncategorized_pending_amount + hiya_pending_amount + not_hiya_pending_amount
    return render(request,'servicedelivery/outward_report.html',{
        'uncategorized_pending_amount':uncategorized_pending_amount,
        'hiya_pending_amount':hiya_pending_amount,
        'not_hiya_pending_amount':not_hiya_pending_amount,
        'total_pending_amount':not_hiya_pending_amount + hiya_pending_amount + uncategorized_pending_amount,
        #'total_salesorders':total_salesorders ,
        #'total_pending':total_pending,
        #'unplanned_so_remaining':unplanned_so_remaining,
        #'hiya_sop':hiya_sop,
        #'not_hiya_sop':not_hiya_sop,
        'hiya_dispatched_amount_okhla':hiya_dispatched_amount_okhla,
        'not_hiya_dispatched_amount_okhla':not_hiya_dispatched_amount_okhla,
        'hiya_dispatched_amount_baddi':hiya_dispatched_amount_baddi,
        'not_hiya_dispatched_amount_baddi':not_hiya_dispatched_amount_baddi,
        'total_dispatched_amount_okhla':not_hiya_dispatched_amount_okhla + hiya_dispatched_amount_okhla,
        'total_dispatched_amount_baddi':not_hiya_dispatched_amount_baddi + hiya_dispatched_amount_baddi,
        'total_dispatched_amount':not_hiya_dispatched_amount_okhla + hiya_dispatched_amount_okhla + not_hiya_dispatched_amount_baddi + hiya_dispatched_amount_baddi,
        'filter':sopp_filter
        })
def outward_servicedelivery_intransit(request):
    if request.method == "GET":
        salesorderproductplans=SalesOrderProductPlan.objects.all()
        salesorderproductplans_dispatched=[]
        sopps_lr_shared = {}
        for sopp in salesorderproductplans :
            if sopp.plan_status == "in-transit":
                salesorderproductplans_dispatched.append(sopp)
                if(sopp.tracking_number != '' and sopp.tracking_number != None):

                    try:
                        sopps_lr_shared[sopp.tracking_number].append(sopp)
                    except:
                        sopps_lr_shared[sopp.tracking_number] = [sopp]
                
        print("point-2:----->",sopps_lr_shared)
        print("point-1:----->",salesorderproductplans_dispatched)
        return render(request,'servicedelivery/outward_intransit.html',{'salesorderproductplans_dispatched':salesorderproductplans_dispatched,'sopps_lr_shared':sopps_lr_shared})
    if(request.method == "POST"):
        if "status-updated"in request.POST:
            lr_number = request.POST.get("lr_number")
            tracking_status = request.POST.get("tracking_status")
            eta = request.POST.get("eta")
            sopps = SalesOrderProductPlan.objects.filter(tracking_number=lr_number)
            buyer = sopps[0].salesorderproduct.salesorder.buyer
            subject = "Order Live Status Update"
            to = [buyer.email]
            from_email = 'admin@rawble.com'
            users = User.objects.all()
            users_sales = User.objects.filter(groups__name="Sales Team")
            ctx = {
                "sopps":sopps,
                "users_sales":users_sales,
                "buyer":buyer,
                "lr_number":lr_number,
                "tracking_status":tracking_status,
                "eta":eta


                }
            cc_email = ["gupta.rishabh.abcd@gmail.com"]
            for user in users:
                cc_email.append(str(user.email))

                
            message = render_to_string('emails/external/current_status.html', ctx)
            text_content = strip_tags(message)
            #EmailMessage(subject, message, to=to, from_email=from_email).send()
            msg = EmailMultiAlternatives(subject, text_content, from_email, to,cc=cc_email)
            msg.attach_alternative(message, "text/html")
            msg.send()
            sopps.update(tracking_status=tracking_status)
            sopps.update(eta=eta)

        if "delivered" in request.POST:
            lr_number = request.POST.get("lr_number")
            sopps = SalesOrderProductPlan.objects.filter(tracking_number=lr_number)
            buyer = sopps[0].salesorderproduct.salesorder.buyer
            subject = "Order Delivered"
            to = [buyer.email]
            from_email = 'admin@rawble.com'
            users = User.objects.all()
            users_sales = User.objects.filter(groups__name="Sales Team")
            ctx = {
                "sopps":sopps,
                "users_sales":users_sales,
                "buyer":buyer,
                "lr_number":lr_number,


                }
            cc_email = ["gupta.rishabh.abcd@gmail.com"]
            for user in users:
                cc_email.append(str(user.email))

                
            message = render_to_string('emails/external/order_delivered.html', ctx)
            text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
            msg = EmailMultiAlternatives(subject, text_content, from_email, to,cc=cc_email)
            msg.attach_alternative(message, "text/html")
            msg.send()
            sopps.update(delivered_date_time=datetime.datetime.now())
        if "lr-submit" in request.POST :
            sopp_ids = request.POST.getlist("lr_sopp_id")
            lr_number = request.POST.get("lr_number")
            sopp_lr = []
            for sopp_id in sopp_ids:
                sopp = SalesOrderProductPlan.objects.get(id=sopp_id)
                sopp.tracking_number = lr_number
                sopp.save()
                sopp_lr.append(sopp)
            buyer_sopps = {}
            for sopp in sopp_lr:
                buyer = sopp.salesorderproduct.salesorder.buyer
                
                try:
                    buyer_sopps[buyer.contact_name].append(sopp)
                except:
                    buyer_sopps[buyer.contact_name] = [sopp]
            print(buyer_sopps)
            if (buyer_sopps):
                for buyer,sopps in buyer_sopps.items():

                    subject = "LR Details For Your Orders"
                    to = []
                    from_email = 'admin@rawble.com'
                    users = User.objects.all()
                    users_sales = User.objects.filter(groups__name="Sales Team")
                    ctx = {
                    "sopps":sopps,
                    "users_sales":users_sales,
                    "buyer":buyer,
                    "lr_number":lr_number,


                    }
                    cc_email = ["gupta.rishabh.abcd@gmail.com"]
                    for user in users:
                        cc_email.append(str(user.email))

                    to.append(sopps[0].salesorderproduct.salesorder.buyer.email)
                    message = render_to_string('emails/external/lr_details.html', ctx)
                    text_content = strip_tags(message)
                    #EmailMessage(subject, message, to=to, from_email=from_email).send()
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to,cc=cc_email)
                    msg.attach_alternative(message, "text/html")
                    msg.send()
        return redirect("outward_servicedelivery_intransit")
def outward_servicedelivery_shipping(request):
    if request.method == "GET":
        sopps = SalesOrderProductPlan.objects.all().order_by("-salesorderproduct__salesorder__salesorder_number")
        sopps_expired = []
        sopps_from_today=[]
        for sopp in sopps:
            if( sopp.plan_status == "planned"):
                if (sopp.planned_date_time.date() - datetime.date.today()).days < 0 :
                    sopps_expired.append(sopp)
                else:
                    sopps_from_today.append(sopp)

        transporters = Transporter.objects.all().order_by("name")
        dispatchdates = []
        today = date.today()
        day = today
        for i in range(30):
            if(day.weekday() in [0,2,4]):
                dispatchdates.append(day)
            day = day + datetime.timedelta(days=1)
        return render(request,'servicedelivery/outward_shipping.html',{'sopps_expired':sopps_expired,'sopps_from_today':sopps_from_today,'transporters':transporters,'dispatchdates':dispatchdates})
    if request.method == "POST":
        if "replan" in request.POST:
            selected_sopp_ids = request.POST.getlist('selected_sopp_id')
            planned_date = request.POST.get('planned_date')
            planned_time = request.POST.get('planned_time')
            reason = request.POST.get('reason')
            transporter_id = request.POST.get('transporter_id')
            try:
                transporter = Transporter.objects.get(id=transporter_id)
            except:
                transporter = None
            sopp_email = []
            for selected_sopp_id in selected_sopp_ids:
                sopp = SalesOrderProductPlan.objects.get(id = selected_sopp_id)
                sopp.planned_date_time = planned_date + " " + planned_time
                sopp.transporter = transporter
                sopp.reason = reason
                sopp.save()
                sopp_email.append(sopp)
            if(sopp_email):
                subject = "Items Rescheduled to Dispatch"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount = 0
                
                for sopp in sopp_email:
                    total_quantity = total_quantity + sopp.planned_quantity
                    total_amount = total_amount + sopp.total_amount
                    
                ctx = {
                    "sopp_email":sopp_email,
                    #"users_sales":users_sales,
                    'planned_date':planned_date,
                    'planned_time':planned_time,
                    'reason':reason,
                    "total_quantity":total_quantity,
                    "total_amount":total_amount,
                    
                }
                for user in users:
                    to.append(str(user.email))
        

                message = render_to_string('emails/outward/delay_reason.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                msg.send()
        if "mark-as-dispatched" in request.POST:
            selected_sopp_ids = request.POST.getlist('selected_sopp_id')
            
            buyer_sopps = {}
            for selected_sopp_id in selected_sopp_ids:
                sopp = SalesOrderProductPlan.objects.get(id = selected_sopp_id)
                sopp.shipped_date_time = sopp.planned_date_time
                sopp.save()
                
                buyer = sopp.salesorderproduct.salesorder.buyer
                try:
                    buyer_sopps[buyer.contact_name].append(sopp)
                except:
                    buyer_sopps[buyer.contact_name] = [sopp]
            
            if (buyer_sopps):
                for buyer,sopps in buyer_sopps.items():

                    subject = "Order Dispatched"
                    to = []
                    from_email = 'admin@rawble.com'
                    users = User.objects.all()
                    #to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
            
                    users = User.objects.all()
                    users_sales = User.objects.filter(groups__name="Sales Team")
                    
                    
                    ctx = {
                        "sopp_email":sopps,
                        #"users_sales":users_sales,
                        "buyer":buyer
                    }
                    cc_email = ["gupta.rishabh.abcd@gmail.com"]
                    for user in users:
                        cc_email.append(str(user.email))
        
                    to.append(sopps[0].salesorderproduct.salesorder.buyer.email)
                    message = render_to_string('emails/external/order_dispatched.html', ctx)
                    text_content = strip_tags(message)
                    #EmailMessage(subject, message, to=to, from_email=from_email).send()
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to,cc=cc_email)
                    msg.attach_alternative(message, "text/html")
                    msg.send()
        
        return redirect("outward_servicedelivery_shipping")
def outward_service_delivery(request):
    if request.method == "GET":
        
        closed_salesorders = ZohoSalesOrder.objects.filter(status="closed")
        salesorders = ZohoSalesOrder.objects.all().order_by("buyer__contact_name","-salesorder_number").exclude(id__in=closed_salesorders)
        salesorders_unplanned = []
        for salesorder in salesorders:
            if(salesorder.planned_status == False):


                salesorders_unplanned.append(salesorder)
            
        today = date.today()
        day = today
        for i in range(10):
            if(day.weekday() in [0,2,4]):
                next_outward_date = day
                break
            day = day + datetime.timedelta(days=1)
        day= today
        for p in range(10):
            day = day - datetime.timedelta(days=1)
            if(day.weekday() in [0,2,4]):
                previous_outward_date = day
                break
        return render(request, 'servicedelivery/outward.html', {'salesorders_unplanned': salesorders_unplanned,'next_outward_date':next_outward_date,'previous_outward_date':previous_outward_date})
    if request.method == "POST":
        if "mail-nextoutward-summary" in request.POST:
            today = date.today()
            day = today
            for i in range(10):
                if(day.weekday() in [0,2,4]):
                    next_outward_date = day
                    break
                day = day + datetime.timedelta(days=1)
            day= today
            for p in range(10):
                day = day - datetime.timedelta(days=1)
                if(day.weekday() in [0,2,4]):
                    previous_outward_date = day
                    break
            sopps = SalesOrderProductPlan.objects.filter(planned_date_time__date=next_outward_date)
            subject = "Next Outward Plan Summary ["+str(next_outward_date)+"]"
            to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
            from_email = 'admin@rawble.com'
            users = User.objects.all()
            users_sales = User.objects.filter(groups__name="Sales Team")
            total_quantity = 0
            total_amount = 0
            for sopp in sopps:
                total_quantity = total_quantity + sopp.planned_quantity
                total_amount = total_amount + ( sopp.total_amount )
            ctx = {
                "sopp_email":sopps,
                "users_sales":users_sales,
                "total_quantity":total_quantity,
                "total_amount":total_amount,
                "next_outward_date":next_outward_date,

            }
            #for user in users:
            #    to.append(str(user.email))


            message = render_to_string('emails/outward/nextoutward_summary.html', ctx)
            text_content = strip_tags(message)
            #EmailMessage(subject, message, to=to, from_email=from_email).send()
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(message, "text/html")
            msg.send()  
        if "sopp-save" in request.POST:
            sopp_ids = request.POST.getlist("sopp_id")
            transporter_ids = request.POST.getlist("transporter_id")
            quantity_to_dispatchs = request.POST.getlist("quantity_to_dispatch")
            freights = request.POST.getlist("freight")
            
            for i,sopp_id in enumerate(sopp_ids):
                try:
                    if(request.POST.get("coafile_id-"+str(sopp_id)) != ""):
                        coafile = CoaFile.objects.get(id = request.POST.get("coafile_id-"+str(sopp_id)) )
                    else:
                        coafile=None
                except:
                    coafile = None
                if(transporter_ids[i] == ""):
                    transporter = None
                else:
                    transporter = Transporter.objects.get(id = transporter_ids[i])
                
                if(freights[i] == ''):
                        freight = 0.0
                else:
                    freight = freights[i]
                if(quantity_to_dispatchs[i] == ''):
                    quantity_to_dispatch = 0.0
                else:
                    quantity_to_dispatch = quantity_to_dispatchs[i]
                sopp = SalesOrderProductPlan.objects.get(id = sopp_id)
                sopp.transporter = transporter
                sopp.freight = freight
                sopp.planned_quantity = quantity_to_dispatch
                sopp.coafile = coafile
                sopp.save()
                

        if "dispatched-outward" in request.POST:
            sopp_ids = request.POST.getlist("sop_id")
            transporter_ids = request.POST.getlist("transporter_id")
            quantity_to_dispatchs = request.POST.getlist("quantity_to_dispatch")
            freights = request.POST.getlist("freight")
            
            dispatched_sopp_ids = request.POST.getlist("dispatched")
            
            
            for i,sopp_id in enumerate(sopp_ids):
                try:
                    if(request.POST.get("coafile_id-"+str(sopp_id)) != ""):
                        coafile = CoaFile.objects.get(id = request.POST.get("coafile_id-"+str(sopp_id)) )
                    else:
                        coafile=None
                except:
                    coafile = None

                if(transporter_ids[i] == ""):
                    transporter = None
                else:
                    transporter = Transporter.objects.get(id = transporter_ids[i])
               
                if(freights[i] == ''):
                        freight = 0.0
                else:
                    freight = freights[i]
                if(quantity_to_dispatchs[i] == ''):
                    quantity_to_dispatch = 0.0
                else:
                    quantity_to_dispatch = quantity_to_dispatchs[i]
                sopp = SalesOrderProductPlan.objects.get(id=sopp_id)
                sopp.transporter = transporter
                sopp.freight = freight
                sopp.planned_quantity = quantity_to_dispatch
                sopp.coafile = coafile
                sopp.save()
            sopp_email = []
            for dispatched_sopp_id in dispatched_sopp_ids:
                sopp_dispatched = SalesOrderProductPlan.objects.get(id=dispatched_sopp_id)
                sopp_dispatched.shipped_date_time = datetime.datetime.now()
                
                
                sopp_dispatched.save()
                
                sopp_email.append(sopp_dispatched)
            print(sopp_email)
            if( sopp_email ):
                subject = "Items Dispatched Today (Reminder)"
                to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
                from_email = 'admin@rawble.com'
                users = User.objects.all()
                users_sales = User.objects.filter(groups__name="Sales Team")
                total_quantity = 0
                total_amount = 0
                for sopp in sopp_email:
                    total_quantity = total_quantity + sopp.planned_quantity
                    total_amount = total_amount + ( sopp.planned_quantity * sopp.salesorderproduct.so_selling_price )
                ctx = {
                    "sopp_email":sopp_email,
                    "users_sales":users_sales,
                    "total_quantity":total_quantity,
                    "total_amount":total_amount

                }
                for user in users:
                    to.append(str(user.email))


                message = render_to_string('emails/outward_dispatched.html', ctx)
                text_content = strip_tags(message)
                #EmailMessage(subject, message, to=to, from_email=from_email).send()
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(message, "text/html")
                
                msg.send()  
        if "so-outward" in request.POST:
            salesorder_id = request.POST.get("salesorder_id")
            product_ids = request.POST.getlist("product_id")
            quantitys = request.POST.getlist("quantity")
            planned_quantitys = request.POST.getlist("planned_quantity")
            pack_sizes = request.POST.getlist("pack_size")
            
            planned_date = request.POST.get("planned_date")
            planned_time = request.POST.get("planned_time")
            selling_prices = request.POST.getlist("selling_price")
            selected_product_item_ids = request.POST.getlist("selected_product_item_id")
            freight = request.POST.get("freight")
            transporter_id = request.POST.get("transporter_id")
            salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
            if freight == '':
                freight=0
            freight_for_each = (float(freight) / len(selected_product_item_ids))
            if ( salesorder.salesorderproduct_set.count() == 0 ):
                sops=[]
                for i,product_id in enumerate(product_ids):
                    if(pack_sizes[i] == ''):
                        pack_sizes[i] = 0
                    salesorder = ZohoSalesOrder.objects.get(salesorder_id=salesorder_id)
                    product = Product.objects.get(item_id = product_ids[i])
                    
                    try:
                        sop = salesorder.salesorderproduct_set.get(product = product)
                    except:
                        sop = SalesOrderProduct(
                            salesorder=salesorder,
                            product=product,
                            so_selling_price=selling_prices[i],
                            quantity=quantitys[i],
                            pack_size=pack_sizes[i],
                            )
                    sop.save()
                    sops.append(sop)
            for selected_product_item_id in selected_product_item_ids:
                for i,product_id in enumerate(product_ids):
                    if product_id == selected_product_item_id :
                        try:
                            transporter = Transporter.objects.get(id=transporter_id)
                        except:
                            transporter = None
                        sopp = SalesOrderProductPlan(
                            salesorderproduct = salesorder.salesorderproduct_set.get(product__item_id = product_id),
                            #planned_date_time__date = planned_date,
                            #planned_date_time__time = planned_time,
                            freight = freight_for_each,
                            planned_quantity = planned_quantitys[i],
                            transporter = transporter

                        ) 
                        sopp.planned_date_time = planned_date + " " + planned_time
                        #sopp.planned_date_time.time = planned_time
                        sopp.save()
                    

        return redirect("outward_servicedelivery")


def report_service_delivery(request):
    if request.method == 'GET':
        today = date.today()
        print (date.today())
        purchaseorderproducts = PurchaseOrderProduct.objects.all().filter(pickup_date_time__date=today)
        total_receiving_amount = 0
        total_receiving_quantity = 0
        total_receiving_freight = 0
        for purchaseorderproduct in purchaseorderproducts:
            total_receiving_amount += int(purchaseorderproduct.purchase_price)*int(purchaseorderproduct.quantity)
            total_receiving_quantity += int(purchaseorderproduct.quantity)
            total_receiving_freight += int(purchaseorderproduct.freight)
        salesorderproducts = SalesOrderProduct.objects.all().filter(outward_date_time__date=today)
        total_dispatching_amount = 0
        total_dispatching_quantity = 0
        total_dispatching_freight = 0
        for salesorderproduct in salesorderproducts:
            total_dispatching_amount += int(salesorderproduct.so_selling_price)*int(salesorderproduct.quantity)
            total_dispatching_quantity += int(salesorderproduct.quantity)
            total_dispatching_freight += int(salesorderproduct.freight)
        return render(request,'servicedelivery/report.html',
                      {"purchaseorderproducts":purchaseorderproducts,
                       "salesorderproducts":salesorderproducts,
                       "total_receiving_amount":total_receiving_amount,
                       "total_receiving_quantity":total_receiving_quantity,
                       "total_dispatching_amount":total_dispatching_amount,
                       "total_dispatching_quantity":total_dispatching_quantity,
                       "total_receiving_freight":total_receiving_freight,
                       "total_dispatching_freight":total_dispatching_freight})
    if request.method == 'POST':
        daterange = request.POST.get('daterange')
        startdate,enddate = daterange.split("/")
        startdate = parse_date(startdate)
        enddate = parse_date(enddate)

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)+1):
                yield start_date + timedelta(n)

        purchaseorderproducts = PurchaseOrderProduct.objects.none()
        for single_date in daterange(startdate, enddate):
            purchaseorderproducts |= PurchaseOrderProduct.objects.all().filter(pickup_date_time__date=single_date)
        total_receiving_amount = 0
        total_receiving_quantity = 0
        total_receiving_freight = 0
        for purchaseorderproduct in purchaseorderproducts:
            total_receiving_amount += int(purchaseorderproduct.purchase_price) * int(purchaseorderproduct.quantity)
            total_receiving_quantity += int(purchaseorderproduct.quantity)
            total_receiving_freight += int(purchaseorderproduct.freight)
        salesorderproducts = SalesOrderProduct.objects.none()
        for single_date in daterange(startdate, enddate):
            salesorderproducts |= SalesOrderProduct.objects.all().filter(outward_date_time__date=single_date)
        total_dispatching_amount = 0
        total_dispatching_quantity = 0
        total_dispatching_freight = 0
        for salesorderproduct in salesorderproducts:
            total_dispatching_amount += int(salesorderproduct.so_selling_price) * int(salesorderproduct.quantity)
            total_dispatching_quantity += int(salesorderproduct.quantity)
            total_dispatching_freight += int(salesorderproduct.freight)
        return render(request, 'servicedelivery/report.html',
                      {"purchaseorderproducts": purchaseorderproducts, "salesorderproducts": salesorderproducts,
                       "total_receiving_amount": total_receiving_amount,
                       "total_receiving_quantity": total_receiving_quantity,
                       "total_dispatching_amount": total_dispatching_amount,
                       "total_dispatching_quantity": total_dispatching_quantity,
                       "total_receiving_freight": total_receiving_freight,
                       "total_dispatching_freight": total_dispatching_freight})




def refresh_purchase_orders(request):
    call_command('update_purchaseorders_from_zoho')
    return redirect('inward_servicedelivery_new')

def refresh_sales_order(request):
    call_command('update_salesorders_from_zoho')
    return redirect('inward_servicedelivery')

def send_mail_pickup(request):
    call_command('todays_pickup_email')
    return redirect('inward_servicedelivery')
def send_mail_outward(request):
    call_command('todays_outward_email')
    return redirect('outward_servicedelivery')