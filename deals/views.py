from django.shortcuts import render,redirect
from django.views.generic import CreateView,ListView,DeleteView,DetailView
from deals.models import DealVendor,DealVendorProduct,ZohoEstimate,VendorProduct,VendorProductVariation,EstimateProduct,ZohoSalesOrder,SalesOrderProduct
from contacts.models import ContactBuyer,ContactVendor
from products.models import Product,ProductGroup,Unit,Make,CoaFile
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect,HttpResponse
from reports.models import Invoice,Bill
from django.core.management import call_command
from django.db.models import Sum
#from deals.forms import DealBuyerCreateForm,DealBuyerProductFormSet,DealVendorCreateForm,DealVendorProductFormSet
import requests
import json
import itertools
import datetime
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from deals.tables import DealVendorTable
from django_plotly_dash import DjangoDash
from django_tables2 import RequestConfig
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from deals.filters import SOFilter
def salesreport_mail_admin(request):
    
    start_of_month = datetime.date.today().replace(day=1)
    so_qs = ZohoSalesOrder.objects.filter(date__gte = start_of_month)
    
    salespersons_list = so_qs.order_by().values('salesperson').distinct()
    salespersons={}
    total_profit = 0
    total_sales = 0
    for salesperson in salespersons_list:
        salespersons[salesperson['salesperson']] = {'total_profit':0,'total_sales':0,'profit_percentage':0}

    for so in so_qs:
        for sop in so.salesorderproduct_set.all():
            if(sop.hiya == False and sop.salesorder.buyer.contact_name != 'NUPLANET VENTURES INDIA PVT LTD (BADDI)'):
                total_profit = total_profit + sop.margin
                total_sales = total_sales + sop.amount
                salespersons[so.salesperson]['total_profit'] = salespersons[so.salesperson]['total_profit'] + sop.margin
                salespersons[so.salesperson]['total_sales'] = salespersons[so.salesperson]['total_sales'] + sop.amount
    profit_percentage = 0
    try:
        profit_percentage = (total_profit/total_sales)*100
    except:
        pass
    for salesperson,stats in salespersons.items():
        stats['profit_percentage'] = 0
        try:
            stats['profit_percentage'] = (stats['total_profit']/stats['total_sales'])*100
        except:
            pass
            

    subject = "Chemicals Profit Report of "+ str(datetime.datetime.now().strftime('%B'))+","+str(datetime.datetime.now().strftime('%Y')) + " Till Date"
    to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
    from_email = 'admin@rawble.com'
    cc_email=[]
    users_sales = User.objects.filter(groups__name="Sales Team")
    users_purchase = User.objects.filter(groups__name="Purchase Team")
    ctx = {
            "salespersons":salespersons,
            "total_profit":total_profit,
            "total_sales":total_sales,
            "profit_percentage":profit_percentage,
        }
    for user in users_sales:
        cc_email.append(str(user.email))
    #for user in users_purchase:
    #    cc_email.append(str(user.email))

    message = render_to_string('emails/salesreport_mail_admin.html', ctx)
    text_content = strip_tags(message)
    #EmailMessage(subject, message, to=to, from_email=from_email).send()
    msg = EmailMultiAlternatives(subject, text_content, from_email, to ,cc=cc_email )
    msg.attach_alternative(message, "text/html")
    msg.send()
    
    return redirect('sales_report')
def overall_stats(request):
    if request.method == "GET":
        first_day = request.GET.get('first_day')
        last_day = request.GET.get('last_day')
        start_of_month = datetime.date.today().replace(day=1,month=7)
        sops = SalesOrderProduct.objects.filter(salesorder__date__gte=first_day,salesorder__date__lte=last_day)
        eps = EstimateProduct.objects.filter(estimate__date__gte=first_day,estimate__date__lte=last_day)
        total_sop_count = 0
        total_profit = 0
        total_sales = 0
        total_ep_count=0
        total_ep_amount = 0
        for ep in eps:
            if(ep.hiya == False):
                total_ep_count = total_ep_count + 1
                total_ep_amount = total_ep_amount + ep.amount

        for sop in sops:
            if(sop.hiya == False and sop.salesorder.buyer.contact_name != 'NUPLANET VENTURES INDIA PVT LTD (BADDI)'):
                total_sop_count = total_sop_count + 1
                total_profit = total_profit + sop.margin
                total_sales = total_sales + sop.amount
        profit_per_sales_percentage = 0
        try:
            profit_per_sales_percentage = (total_profit/total_sales) * 100
        except:
            pass
        conversion_percentage = 0
        try:
            conversion_percentage = (total_sales / total_ep_amount) * 100
        except:
            pass

        rendered = render_to_string(
            'deals/helper_ajax/overall_stats.html',
            context={
                'total_ep_count':total_ep_count,
                'total_ep_amount':total_ep_amount,
                'conversion_percentage':conversion_percentage,
                'total_sop_count':total_sop_count,
                'total_profit':total_profit,
                'total_sales':total_sales,
                'profit_per_sales_percentage':profit_per_sales_percentage
                })
        return JsonResponse({'overall_stats_snippet':rendered})
def salesperson_stats(request):
    if request.method == "GET":
        salesperson = request.GET.get('salesperson')
        first_day = request.GET.get('first_day')
        last_day = request.GET.get('last_day')

        start_of_month = datetime.date.today().replace(day=1,month=7)
        eps = EstimateProduct.objects.filter(estimate__salesperson = salesperson, estimate__date__gte = first_day,estimate__date__lte=last_day)
        sops = SalesOrderProduct.objects.filter(salesorder__salesperson = salesperson,salesorder__date__gte=first_day,salesorder__date__lte=last_day)
        total_sop_count = 0
        total_profit = 0
        total_sales = 0
        total_ep_count=0
        total_ep_amount = 0
        for ep in eps:
            if(ep.hiya == False):
                total_ep_count = total_ep_count + 1
                total_ep_amount = total_ep_amount + ep.amount

        for sop in sops:
            if(sop.hiya == False and sop.salesorder.buyer.contact_name != 'NUPLANET VENTURES INDIA PVT LTD (BADDI)'):
                total_sop_count = total_sop_count + 1
                total_profit = total_profit + sop.margin
                total_sales = total_sales + sop.amount
        profit_per_sales_percentage = 0
        try:
            profit_per_sales_percentage = (total_profit/total_sales) * 100
        except:
            pass
        conversion_percentage = 0
        try:
            conversion_percentage = (total_sales / total_ep_amount) * 100
        except:
            pass
        
        rendered = render_to_string(
            'deals/helper_ajax/salesperson_stats.html',
            context={
                'salesperson':salesperson,
                'total_ep_count':total_ep_count,
                'total_ep_amount':total_ep_amount,
                'total_sop_count':total_sop_count,
                'total_sales':total_sales,
                'conversion_percentage':conversion_percentage,
                'total_profit':total_profit,
                'profit_per_sales_percentage':profit_per_sales_percentage})
        return JsonResponse({'salesperson_stats_snippet':rendered})

def sales_report(request):
    so_list = ZohoSalesOrder.objects.all()
    month = request.GET.get("month")
    month_int = int(float(month))

    month_str = datetime.date(1900, month_int, 1).strftime('%B')

    print month
    so_filter = SOFilter(request.GET, queryset=so_list)
    salespersons = so_filter.qs.order_by().values('salesperson').distinct()
    print(salespersons)
    salesperson_buyer = {}
    for salesperson in salespersons:
        salesperson_buyer[salesperson['salesperson']] = {}
    
    print(salesperson_buyer)
    total_margin = 0
    for so in so_filter.qs :
        for sop in so.salesorderproduct_set.all().order_by("-salesorder__salesorder_number"):
            if(sop.hiya == False and sop.salesorder.buyer.contact_name != 'NUPLANET VENTURES INDIA PVT LTD (BADDI)'):
                try:
                    salesperson_buyer[so.salesperson][so.buyer.contact_name].append(sop)
                except:
                    salesperson_buyer[so.salesperson][so.buyer.contact_name] = [sop]
        print(salesperson_buyer)
        #try:
        #    #print(salesperson)
        #    #print(salesperson[so.salesperson][so.buyer.contact_name])
        #    salesperson_buyer[so.salesperson][so.buyer.contact_name].append(so)
        #    print("1")
        #except:
        #    
        #    salesperson_buyer[so.salesperson][so.buyer.contact_name] = [so]
        #    print("2")
        #for sop in so.salesorderproduct_set.all():
        #    if(sop.hiya == False):
        #        total_margin = total_margin + sop.margin

    #print(salesperson)
    #for estimate_number in ZohoEstimate.objects.values_list('estimate_number', flat=True).distinct():
    #    ZohoEstimate.objects.filter(pk__in=ZohoEstimate.objects.filter(estimate_number=estimate_number).values_list('id',# flat=True)[1:]).delete()
    return render(request,'deals/sales_report.html',{'filter':so_filter,'salesperson_buyer':salesperson_buyer,'total_margin':total_margin,"month":month})
# Create your views here.
def zoho_salesorders(request):
    if request.method == 'GET':
        start_of_month = datetime.date.today().replace(day=1)
        salesorders = ZohoSalesOrder.objects.all().order_by('-date')
        return render(request,'deals/zoho_salesorders.html',{'salesorders':salesorders})
    if request.method == 'POST':
        if "unquote-so" in request.POST:

            salesorder_id = request.POST.get('salesorder_id')
            salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
            
            salesorder.tool_status = ''
            salesorder.salesorderproduct_set.all().delete()
            salesorder.save()
        if "unquote-estimate" in request.POST:
    
            estimate_id = request.POST.get('estimate_id')
            estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
            
            estimate.tool_status = ''
            estimate.estimateproduct_set.all().delete()
            estimate.save()
        return redirect('zoho_salesorders')
def zoho_estimates(request):
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    if request.method == 'GET':

        estimates = ZohoEstimate.objects.all().order_by('-estimate_number')[:2000]
        
        return render(request,'deals/zoho_estimates.html',{'estimates':estimates})
    if request.method == 'POST':
        if "move_to_draft" in request.POST:

            estimate_id = request.POST.get('estimate_id')
            estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
            
            estimate.tool_status = ''
            estimate.estimateproduct_set.all().delete()
            estimate.save()
        if "mark_as_accepted" in request.POST:
            estimate_id = request.POST.get('estimate_id')
            print(estimate_id)
            parameters={'authtoken':auth_token,'organization_id':organization_id}
            response = requests.post("https://books.zoho.com/api/v3/estimates/"+str(estimate_id)+"/status/accepted",params = parameters)
            call_command('update_estimates_from_zoho')
        if "mark_as_declined" in request.POST:
            estimate_id = request.POST.get('estimate_id')
            print(estimate_id)
            parameters={'authtoken':auth_token,'organization_id':organization_id}
            response = requests.post("https://books.zoho.com/api/v3/estimates/"+str(estimate_id)+"/status/declined",params = parameters)
            call_command('update_estimates_from_zoho')
        
        return redirect('zoho_estimates')

def update_zoho_estimates(request):
    call_command('update_estimates_from_zoho')
    return redirect('zoho_estimates')
def update_so(request):
    call_command('update_salesorders_from_zoho')
    return redirect('zoho_salesorders')
def estimate_products(request):
    if request.method == "GET":
        vendors = ContactVendor.objects.all().order_by('contact_name')
        required_products = EstimateProduct.objects.filter(vendorproductvariation = None).distinct('product')
        all_products = EstimateProduct.objects.all().distinct('product')
        return render(request,'deals/estimate_products.html',{'required_products': required_products,'all_products':all_products , 'vendors':vendors })
    if request.method == "POST":
        if "add_vendor" in request.POST:
            delivery_terms = request.POST.get('delivery_terms')
            specs = request.POST.get('specs')
            vendor_price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            expiry = request.POST.get('expiry')
            product_id = request.POST.get('product_id')
            label_name = request.POST.get('label_name')
            contact_id = request.POST.get('contact_id')
            d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id= contact_id ),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
            d1.save()
            dp = DealVendorProduct(
                deal = DealVendor.objects.get(id = d1.id),
                specs = specs,
                vendor_price = vendor_price,
                quantity = quantity,
                price_valid_till = expiry , 
                product = Product.objects.get(item_id = product_id),
                label_name = label_name,

            )
            dp.save()
        
        if "update_product" in request.POST:
            new_price = request.POST.get("newprice")
            dealproduct_id = request.POST.get("dealproduct_id")
            expiry = request.POST.get("expiry")
            delivery_terms = request.POST.get("delivery_terms")
            contact_id = request.POST.get("contact_id")
            
            print(new_price,dealproduct_id,expiry)
            d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id=contact_id),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
            d1.save()
            dp = DealVendorProduct.objects.get(id=dealproduct_id)
            dp.id = None
            dp.deal = d1
            dp.vendor_price = new_price
            dp.price_valid_till = expiry
            dp.save()

        return redirect('estimate_products')

def zoho_salesorder_inprogress(request,pk):
    salesorder = ZohoSalesOrder.objects.get(salesorder_id = pk)
    if request.method == 'GET':
        salesorder = ZohoSalesOrder.objects.get(salesorder_id = pk)
        
        return render(request,'deals/zoho_salesorder_inprogress.html',{'salesorder':salesorder})

    if request.method == 'POST':
        vendorproductvariation_ids = request.POST.getlist('vendorproductvariation_id')
        salesorderproduct_ids = request.POST.getlist('salesorderproduct_id')
        for i,salesorderproduct_id in enumerate(salesorderproduct_ids):
            salesorderproduct = SalesOrderProduct.objects.get(id = salesorderproduct_id)
            if(vendorproductvariation_ids[i]):
                salesorderproduct.vendorproductvariation = VendorProductVariation.objects.get(id = vendorproductvariation_ids[i])
            else:
                salesorderproduct.vendorproductvariation = None

            salesorderproduct.save()
        subject = "Quotations (Sales Order)[UPDATED Prices] - "+str(salesorder.buyer) + " || Date: [ " + str(salesorder.date) + " ]"
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users_sales = User.objects.filter(groups__name="Sales Team")
        users_purchase = User.objects.filter(groups__name="Purchase Team")
        ctx = {
            "salesorder":salesorder,
            "users_sales":users_sales,

        }
        for user in users_sales:
            to.append(str(user.email))
        for user in users_purchase:
            to.append(str(user.email))

        message = render_to_string('emails/salesorder_in_progress.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(message, "text/html")
        msg.send()
        #print(rates)
        headers = {
            'content-type': "multipart/form-data;",
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            
            }
        return redirect('zoho_salesorder_inprogress',pk=pk)
def zoho_estimate_inprogress(request,pk):
    estimate = ZohoEstimate.objects.get(estimate_id = pk)
    if request.method == 'GET':
        estimate = ZohoEstimate.objects.get(estimate_id = pk)
        
        return render(request,'deals/zoho_estimate_inprogress.html',{'estimate':estimate})

    if request.method == 'POST':
        vendorproductvariation_ids = request.POST.getlist('vendorproductvariation_id')
        estimateproduct_ids = request.POST.getlist('estimateproduct_id')
        for i,estimateproduct_id in enumerate(estimateproduct_ids):
            estimateproduct = EstimateProduct.objects.get(id = estimateproduct_id)
            if(vendorproductvariation_ids[i]):
                estimateproduct.vendorproductvariation = VendorProductVariation.objects.get(id = vendorproductvariation_ids[i])
            else:
                estimateproduct.vendorproductvariation = None

            estimateproduct.save()
        subject = "Quotations [UPDATED Prices] - "+str(estimate.buyer) + " || Date: [ " + str(estimate.date) + " ]"
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users_sales = User.objects.filter(groups__name="Sales Team")
        users_purchase = User.objects.filter(groups__name="Purchase Team")
        ctx = {
            "estimate":estimate,
            "users_sales":users_sales,

        }
        for user in users_sales:
            to.append(str(user.email))
        for user in users_purchase:
            to.append(str(user.email))

        message = render_to_string('emails/estimate_in_progress.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject,text_content,from_email,to)
        msg.attach_alternative(message, "text/html")
        msg.send()
        #print(rates)
        headers = {
            'content-type': "multipart/form-data;",
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            
            }
        salesorders = estimate.zohosalesorder_set.all()
        for so in salesorders:
            auth_token = 'd56b2f2501f266739e12b86b706d0078'
            parameters={'authtoken':auth_token}
            organization_ids = {'okhla':'667580392','baddi':'665963577'}
            parameters['organization_id'] = organization_ids[so.zoho_location]
            response=requests.get("https://books.zoho.com/api/v3/salesorders/"+str(so.salesorder_id),params = parameters)
            print(response.text)
            salesorder_api = response.json()['salesorder']

            for item in salesorder_api['line_items']:
                sop_qs = SalesOrderProduct.objects.filter(salesorder=so,product = Product.objects.get(pk=item['item_id']))
                if(sop_qs):
                    if(len(sop_qs) > 1):
                        sop_to_delete = sop_qs[1:]
                        sop_to_delete.delete()
                    sop = sop_qs[0]
                    sop.so_selling_price = item['rate']
                    sop.quantity = item['quantity']
                    sop.save()
                else:
                    sop = SalesOrderProduct(
                       salesorder = so,
                       product = Product.objects.get(pk=item['item_id']),
                       quantity = item['quantity'],
                       so_selling_price = item['rate'],
                        
                    )
                    sop.save()
        return redirect('zoho_estimate_inprogress',pk=pk)
def zoho_salesorder(request,pk):
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    salesorder_id = str(pk)
    salesorder_db = ZohoSalesOrder.objects.get(salesorder_id=salesorder_id)
    organization_ids = {'okhla':'667580392','baddi':'665963577'}
    organization_id = organization_ids[salesorder_db.zoho_location]
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items','salesorders':'/salesorders'}
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.get("https://books.zoho.com/api/v3/salesorders/"+str(pk),params = parameters)
    salesorder=response.json()['salesorder']
    if(request.method == 'GET'):
        salesorder_db = ZohoSalesOrder.objects.get(salesorder_id=salesorder_id)
        #base_url = "https://books.zoho.com/api/v3"
        #parameters['item_id'] = item['item_id']
        #estimate_product_vendorproducts = VendorProduct.objects.filter()
        items=[]
        for item in salesorder['line_items']:
            #product =  Product.objects.get(item['item_id'])
            print(item['item_id'])
            item = {'item_id':item['item_id']}
            items.append(item)
        for item in items:
            vendorproducts = VendorProduct.objects.filter(product = Product.objects.get(item_id = item['item_id']))
            item['vendorproducts'] = vendorproducts
        for item in salesorder['line_items']:
            group = Product.objects.get(item_id = item['item_id']).group

            item['group'] = group
        units = Unit.objects.all()
        makes = Make.objects.all().order_by('name')
        return render(request,'deals/zoho_salesorder.html',{'salesorder_db':salesorder_db,'salesorder':salesorder,'items':items,'units':units,'makes':makes})
    
    if(request.method =='POST'):
        vendorproductvariation_ids = request.POST.getlist('vendorproductvariation_id')
        product_ids = request.POST.getlist('product_id')
        
        
        
        rates= request.POST.getlist('rate')
        quantitys = request.POST.getlist('quantity')
        #makes = request.POST.getlist('make')
        pack_sizes =request.POST.getlist('pack_size')
        estimate_products_list = []
        for i,product_id in enumerate(product_ids):
            zoho_salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
            try:
                vendorproductvariation = VendorProductVariation.objects.get(id=vendorproductvariation_ids[i])
            except:
                vendorproductvariation = None
            sop_qs = SalesOrderProduct.objects.filter(salesorder = zoho_salesorder,product=Product.objects.get(pk=product_id))
            if(sop_qs):
                if(len(sop_qs) > 1):
                    sop_to_delete = sop_qs[1:]
                    sop_to_delete.delete()
                sop = sop_qs[0]
                sop.vendorproductvariation = vendorproductvariation
                sop.so_selling_price = rates[i]
                sop.quantity = quantitys[i]
                sop.save()

            else:    
                salesorder_product = SalesOrderProduct(
                    salesorder=zoho_salesorder,
                    product = Product.objects.get(pk = product_id),
                    vendorproductvariation = vendorproductvariation,
                    quantity = quantitys[i],
                    pack_size = pack_sizes[i],
                    so_selling_price = rates[i]
                )
                salesorder_product.save()
            
        
        zoho_salesorder.tool_status = 'in-progress'
        zoho_salesorder.save()

        print(estimate_products_list)
        
        subject = "Quotations (Sales Order) - "+str(zoho_salesorder.buyer) + " || Date: [ " + str(zoho_salesorder.date) + " ]"
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users_sales = User.objects.filter(groups__name="Sales Team")
        users_purchase = User.objects.filter(groups__name="Purchase Team")
        ctx = {
            "salesorder":ZohoSalesOrder.objects.get(salesorder_id = salesorder_id),
            
            "users_sales":users_sales,

        }
        for user in users_sales:
            to.append(str(user.email))
        for user in users_purchase:
            to.append(str(user.email))

        message = render_to_string('emails/salesorder_in_progress.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(message, "text/html")
        msg.send()
        #print(rates)
        #headers = {
        #    'content-type': "multipart/form-data;",
        #    'Content-Type': "application/json",
        #    'cache-control': "no-cache",
        #    
        #    }
        #line_items=[]
        #for i,product_id in enumerate(product_ids):
        ##    
        #    item = {'item_id':product_id,'quantity':quantitys[i] ,'rate':rates[i],'item_custom_fields':[{"index": 1,#"label": "Make","placeholder": "cf_make","value":Product.objects.get(item_id = product_id).make },{"index": #2,"label": "Pack Size","placeholder": "cf_pack_size","value":pack_sizes[i]}]}
        #    line_items.append(item)
        ##for i,item in enumerate(estimate['line_items']):
        #    item['rate'] = rates[i]
        #    item['quantity'] =quantitys[i]
        #    #item['unit'] = units[i]
        #    for custom_field in item['item_custom_fields']:
        #        if(custom_field['placeholder'] =='cf_make') :
        #            custom_field['value']= makes[i]
        #        if(custom_field['placeholder'] =='cf_pack_size') :
        #            custom_field['value']= pack_sizes[i]
                    

        
        #data_string = "JSONString=" + json.dumps(data['JSONString'])
        ##JSONString = json.dumps(JSONString)
        ##print(JSONString)
        #parameters['JSONString'] = str({'customer_id':estimate['customer_id'],'line_items':line_items})
        ##payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"JSONString\"\r\n\r\n" + json.dumps(data)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        #print("----->>>>dd",data_string)
        
        #response=requests.put("https://books.zoho.com/api/v3/estimates/"+str(pk),params = parameters,headers=headers)
        #print(response.text)
        #estimate_zoho = response.json()['estimate']
        #estimate_db = ZohoEstimate.objects.get(estimate_id=pk)
        #estimate_db.status = estimate_zoho['status']
        #estimate_db.save() 
        
        return redirect('zoho_salesorder_inprogress',pk=pk)
          
def zoho_estimate(request,pk):
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    organization_ids = {'okhla':'667580392','baddi':'665963577'}
    zoho_estimate_id = str(pk)
    estimate_db = ZohoEstimate.objects.get(estimate_id=zoho_estimate_id)
    parameters['organization_id'] = organization_ids[estimate_db.zoho_location]
    response = requests.get("https://books.zoho.com/api/v3/estimates/"+str(pk),params = parameters)
    estimate=response.json()['estimate']
    if(request.method == 'GET'):
        estimate_db = ZohoEstimate.objects.get(estimate_id=zoho_estimate_id)
        base_url = "https://books.zoho.com/api/v3"
        #parameters['item_id'] = item['item_id']
        estimate_product_vendorproducts = VendorProduct.objects.filter()
        items=[]
        for item in estimate['line_items']:
            #product =  Product.objects.get(item['item_id'])
            print(item['item_id'])
            item = {'item_id':item['item_id']}
            items.append(item)
        for item in items:
            vendorproducts = VendorProduct.objects.filter(product = Product.objects.get(item_id = item['item_id']))
            item['vendorproducts'] = vendorproducts
        for item in estimate['line_items']:
            group = Product.objects.get(item_id = item['item_id']).group

            item['group'] = group
        units = Unit.objects.all()
        makes = Make.objects.all().order_by('name')
        return render(request,'deals/zoho_estimate.html',{'estimate_db':estimate_db,'estimate':estimate,'items':items,'units':units,'makes':makes})
    
    if(request.method =='POST'):
        vendorproductvariation_ids = request.POST.getlist('vendorproductvariation_id')
        product_ids = request.POST.getlist('product_id')
        
        
        
        rates= request.POST.getlist('rate')
        quantitys = request.POST.getlist('quantity')
        #makes = request.POST.getlist('make')
        pack_sizes =request.POST.getlist('pack_size')
        estimate_products_list = []
        zoho_estimate = ZohoEstimate.objects.get(estimate_id = zoho_estimate_id)
        for i,product_id in enumerate(product_ids):
            zoho_estimate = ZohoEstimate.objects.get(estimate_id = zoho_estimate_id)
            try:
                vendorproductvariation = VendorProductVariation.objects.get(pk=vendorproductvariation_ids[i])
            except:
                vendorproductvariation = None
            estimate_product_qs = EstimateProduct.objects.filter(estimate = zoho_estimate,product=Product.objects.get(pk=product_id))
            if(estimate_product_qs):
                if(len(estimate_product_qs) > 1):
                    estimate_product_to_delete = estimate_product_qs[1:]
                    estimate_product_to_delete.delete()
                estimate_product = estimate_product_qs[0]
                estimate_product.estimate_selling_price = rates[i]
                estimate_product.quantity = quantitys[i]
                estimate_product.save()
            else:
                estimate_product = EstimateProduct(
                    estimate=zoho_estimate,
                    product = Product.objects.get(pk = product_id),
                    vendorproductvariation = vendorproductvariation,
                    quantity = quantitys[i],
                    pack_size = pack_sizes[i],
                    estimate_selling_price = rates[i]
                    )
                estimate_product.save()
            
        
        zoho_estimate.tool_status = 'in-progress'
        zoho_estimate.save()

        print(estimate_products_list)
        
        subject = "Quotations - "+str(zoho_estimate.buyer) + " || Date: [ " + str(zoho_estimate.date) + " ]"
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users_sales = User.objects.filter(groups__name="Sales Team")
        users_purchase = User.objects.filter(groups__name="Purchase Team")
        ctx = {
            "estimate":ZohoEstimate.objects.get(estimate_id = zoho_estimate_id),
            
            "users_sales":users_sales,

        }
        for user in users_sales:
            to.append(str(user.email))
        for user in users_purchase:
            to.append(str(user.email))

        message = render_to_string('emails/estimate_in_progress.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(message, "text/html")
        msg.send()
        #print(rates)
        headers = {
            'content-type': "multipart/form-data;",
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            
            }
        line_items=[]
        for i,product_id in enumerate(product_ids):
        #    
            item = {'item_id':product_id,'quantity':quantitys[i] ,'rate':rates[i],'item_custom_fields':[{"index": 1,"label": "Make","placeholder": "cf_make","value":Product.objects.get(item_id = product_id).make },{"index": 2,"label": "Pack Size","placeholder": "cf_pack_size","value":pack_sizes[i]}]}
            line_items.append(item)
        #for i,item in enumerate(estimate['line_items']):
        #    item['rate'] = rates[i]
        #    item['quantity'] =quantitys[i]
        #    #item['unit'] = units[i]
        #    for custom_field in item['item_custom_fields']:
        #        if(custom_field['placeholder'] =='cf_make') :
        #            custom_field['value']= makes[i]
        #        if(custom_field['placeholder'] =='cf_pack_size') :
        #            custom_field['value']= pack_sizes[i]
                    

        
        #data_string = "JSONString=" + json.dumps(data['JSONString'])
        ##JSONString = json.dumps(JSONString)
        ##print(JSONString)
        parameters['JSONString'] = str({'customer_id':estimate['customer_id'],'line_items':line_items})
        ##payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"JSONString\"\r\n\r\n" + json.dumps(data)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        #print("----->>>>dd",data_string)
        
        response=requests.put("https://books.zoho.com/api/v3/estimates/"+str(pk),params = parameters,headers=headers)
        print(response.text)
        #estimate_zoho = response.json()['estimate']
        #estimate_db = ZohoEstimate.objects.get(estimate_id=pk)
        #estimate_db.status = estimate_zoho['status']
        #estimate_db.save() 
        salesorders = zoho_estimate.zohosalesorder_set.all()
        for so in salesorders:
            auth_token = 'd56b2f2501f266739e12b86b706d0078'
            parameters={'authtoken':auth_token}
            organization_ids = {'okhla':'667580392','baddi':'665963577'}
            parameters['organization_id'] = organization_ids[so.zoho_location]
            response=requests.get("https://books.zoho.com/api/v3/salesorders/"+str(so.salesorder_id),params = parameters)
            print(response.text)
            salesorder_api = response.json()['salesorder']

            for item in salesorder_api['line_items']:
                sop_qs = SalesOrderProduct.objects.filter(salesorder=so,product = Product.objects.get(pk=item['item_id']))
                if(sop_qs):
                    if(len(sop_qs) > 1):
                        sop_to_delete = sop_qs[1:]
                        sop_to_delete.delete()
                    sop = sop_qs[0]
                    sop.so_selling_price = item['rate']
                    sop.quantity = item['quantity']
                    sop.save()
                else:
                    sop = SalesOrderProduct(
                       salesorder = so,
                       product = Product.objects.get(pk=item['item_id']),
                       quantity = item['quantity'],
                       so_selling_price = item['rate'],
                        
                    )
                    sop.save()


                
        return redirect('zoho_estimate_inprogress',pk=pk)   
def salesorder_margin(request):
    salesorder_id = request.GET.get('slug',None)
    salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.get("https://books.zoho.com/api/v3/salesorders/" + salesorder_id,params = parameters)
    salesorder_api = response.json()['salesorder']
    total_margin = 0
    total_products = 0
    for line_item in salesorder_api['line_items']:
        item_id = line_item['item_id']
        try:
            salesorder_product = salesorder.salesorderproduct_set.get(product__item_id = item_id)
        except:
            salesorder_product = None
        if(line_item['rate'] != 0 ):
            margin = (line_item['rate'] - salesorder_product.vendorproductvariation.dealvendorproduct.vendor_price)/line_item['rate']
            line_item['margin'] = margin*100
            total_margin = total_margin + (margin*100)
            total_products = total_products + 1
        else:
            margin = "Please Update Price in Zoho to Check Margin"
            line_item['margin'] = margin
    
    if(total_products != 0):
        overall_margin = total_margin / total_products
    else:
        overall_margin = "Please Update Price in Zoho to Check Overall Margin"
    rendered = render_to_string('deals/helper_ajax/salesorder_margin.html', context = {'salesorder':salesorder,'salesorder_api':salesorder_api,'overall_margin':overall_margin})
    return JsonResponse({'salesorder_margin_snippet': rendered})
def salesorder_approve(request,salesorder_id):
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.post("https://books.zoho.com/api/v3/salesorders/" + str(salesorder_id)+"/approve",params = parameters)
    return redirect("zoho_estimates")
def estimate_margin(request):
    estimate_id = request.GET.get('slug',None)
    estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    response = requests.get("https://books.zoho.com/api/v3/estimates/" + estimate_id,params = parameters)
    estimate_api = response.json()['estimate']
    total_margin = 0
    total_products = 0
    for line_item in estimate_api['line_items']:
        item_id = line_item['item_id']
        estimate_product = estimate.estimateproduct_set.get(product__item_id = item_id)
        if(line_item['rate'] != 0 ):
            margin = (line_item['rate'] - estimate_product.vendorproductvariation.dealvendorproduct.vendor_price)/line_item['rate']
            line_item['margin'] = margin*100
            total_margin = total_margin + (margin*100)
            total_products = total_products + 1
        else:
            margin = "Please Update Price in Zoho to Check Margin"
            line_item['margin'] = margin
    
    if(total_products != 0):
        overall_margin = total_margin / total_products
    else:
        overall_margin = "Please Update Price in Zoho to Check Overall Margin"

    rendered = render_to_string('deals/helper_ajax/estimate_margin.html', context = {'estimate':estimate,'estimate_api':estimate_api,'overall_margin':overall_margin})
    return JsonResponse({'margin_snippet': rendered})
def relationship_manager_buyers(request):
    if request.method == "GET":
        relationship_manager = request.GET.get('relationship_manager')
        buyers = ContactBuyer.objects.filter(relationship_manager=relationship_manager).order_by('contact_name')
        rendered = render_to_string('deals/helper_ajax/relationship_manager_buyers.html',context={'buyers':buyers})
        return JsonResponse({'relationship_manager_snippet':rendered})
def estimate_addproduct_ajax(request):
    if request.method == "GET":
        new_product_id = request.GET.get('new_product_id')
        quantity = request.GET.get('quantity')
        pack_size = request.GET.get('pack_size')
        estimate_id = request.GET.get('estimate_id')
        product = Product.objects.get(item_id = new_product_id)
        estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
        rendered = render_to_string('deals/helper_ajax/estimate_addproduct.html',context={'product':product,'quantity':quantity,'pack_size':pack_size,'estimate':estimate})
        return JsonResponse({'estimate_addproduct_ajax_snippet':rendered})
def salesorder_updatevendorvariation_ajax(request):
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id)
        rendered = render_to_string('deals/helper_ajax/salesorder_updatevendorvariation.html', context = {'product':product},request=request)
        return JsonResponse({'salesorder_updatevendorvariation_ajax_snippet': rendered})
    if request.method =="POST":
        vendor_id = request.POST.get('vendor')
        product_id = request.POST.get('product_id')
        expiry = request.POST.get('expiry')
        price = request.POST.get('price')
        specs = request.POST.get('specs')
        quantity = request.POST.get('quantity')
        delivery_terms = request.POST.get('delivery_terms')
        salesorder_id = request.POST.get('salesorder_id')
        label_name = request.POST.get('label_name')
        contact_id = request.POST.get('contact_id')
        dealproduct_id = request.POST.get('dealproduct_id')


        salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
        product= Product.objects.get(item_id = product_id)

        d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id=contact_id),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
        d1.save()
        dp = DealVendorProduct.objects.get(id=dealproduct_id)
        dp.id = None
        dp.deal = d1
        dp.vendor_price = price
        dp.price_valid_till = expiry
        dp.save()
        
        html = "<option value='' selected>Select Purchase Price From Active Deals</option>"
        for vendorproduct in product.vendorproduct_set.all():
            html = html + "<optgroup style='font-size:109%;color:black;' label='Vendor: " +vendorproduct.vendor.contact_name +" || Payment Terms: "+ vendorproduct.vendor.payment_terms  +"|| Location: "+ vendorproduct.vendor.place_of_contact +"'>"
            
            for i,vendorproductvariation in enumerate(vendorproduct.vendorproductvariation_set.all()):

                html = html+ "<option style='color:black;' class='"
                
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html+"bg-success'"
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0:
                    html = html+ "bg-warning'" 
                else:
                    html = html+"bg-danger'"
                html = html+ "value="+str(vendorproductvariation.id)+" data-item_id = "+str(product.item_id)+" data-purchase_price="+str(vendorproductvariation.dealvendorproduct.vendor_price)+" data-customer_freight="+str(salesorder.buyer.freight_per_kg)+" data-vendor_freight="+str(vendorproduct.vendor.freight_per_kg )+"  data-vpt="+str(vendorproduct.vendor.payment_terms_no)+" data-bpt ="+str(salesorder.buyer.payment_terms_no)+">>> Variation -"+ str(i+1)+" || Specs:"+ vendorproductvariation.dealvendorproduct.specs +"| Pack-size:" +str(vendorproductvariation.dealvendorproduct.quantity ) +"|| Price:"+str(vendorproductvariation.dealvendorproduct.vendor_price )+" || ( "
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html + "Will expire in " +str(vendorproductvariation.dealvendorproduct.expiry_status)+" day(s). "
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0 :
                    html = html + "Expires Today "
                else:
                    html = html + "Expired " +str(vendorproductvariation.dealvendorproduct.expiry_status*(-1))+" day(s) ago.)"
                html = html + "</option></optgroup>"
        response_data = {}
        response_data['vendor'] = vendor_id
        response_data['product_id'] = product_id
        response_data['expiry'] = expiry
        response_data['price'] = price
        response_data['specs'] = specs
        response_data['quantity'] = quantity
        response_data['delivery_terms'] = delivery_terms
        response_data['purchase_price_html'] = html
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
def estimate_updatevendorvariation_ajax(request):
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id)
        rendered = render_to_string('deals/helper_ajax/estimate_updatevendorvariation.html', context = {'product':product},request=request)
        return JsonResponse({'estimate_updatevendorvariation_ajax_snippet': rendered})
    if request.method =="POST":
        vendor_id = request.POST.get('vendor')
        product_id = request.POST.get('product_id')
        expiry = request.POST.get('expiry')
        price = request.POST.get('price')
        specs = request.POST.get('specs')
        quantity = request.POST.get('quantity')
        delivery_terms = request.POST.get('delivery_terms')
        estimate_id = request.POST.get('estimate_id')
        label_name = request.POST.get('label_name')
        contact_id = request.POST.get('contact_id')
        dealproduct_id = request.POST.get('dealproduct_id')


        estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
        product= Product.objects.get(item_id = product_id)

        d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id=contact_id),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
        d1.save()
        dp = DealVendorProduct.objects.get(id=dealproduct_id)
        dp.id = None
        dp.deal = d1
        dp.vendor_price = price
        dp.price_valid_till = expiry
        dp.save()
        
        html = "<option value='' selected>Select Purchase Price From Active Deals</option>"
        for vendorproduct in product.vendorproduct_set.all():
            html = html + "<optgroup style='font-size:109%;color:black;' label='Vendor: " +vendorproduct.vendor.contact_name +" || Payment Terms: "+ vendorproduct.vendor.payment_terms  +"|| Location: "+ vendorproduct.vendor.place_of_contact +"'>"
            
            for i,vendorproductvariation in enumerate(vendorproduct.vendorproductvariation_set.all()):

                html = html+ "<option style='color:black;' class='"
                
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html+"bg-success'"
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0:
                    html = html+ "bg-warning'" 
                else:
                    html = html+"bg-danger'"
                html = html+ "value="+str(vendorproductvariation.id)+" data-item_id = "+str(product.item_id)+" data-purchase_price="+str(vendorproductvariation.dealvendorproduct.vendor_price)+" data-customer_freight="+str(estimate.buyer.freight_per_kg)+" data-vendor_freight="+str(vendorproduct.vendor.freight_per_kg )+"  data-vpt="+str(vendorproduct.vendor.payment_terms_no)+" data-bpt ="+str(estimate.buyer.payment_terms_no)+">>> Variation -"+ str(i+1)+" || Specs:"+ vendorproductvariation.dealvendorproduct.specs +"| Pack-size:" +str(vendorproductvariation.dealvendorproduct.quantity ) +"|| Price:"+str(vendorproductvariation.dealvendorproduct.vendor_price )+" || ( "
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html + "Will expire in " +str(vendorproductvariation.dealvendorproduct.expiry_status)+" day(s). "
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0 :
                    html = html + "Expires Today "
                else:
                    html = html + "Expired " +str(vendorproductvariation.dealvendorproduct.expiry_status*(-1))+" day(s) ago.)"
                html = html + "</option></optgroup>"
        response_data = {}
        response_data['vendor'] = vendor_id
        response_data['product_id'] = product_id
        response_data['expiry'] = expiry
        response_data['price'] = price
        response_data['specs'] = specs
        response_data['quantity'] = quantity
        response_data['delivery_terms'] = delivery_terms
        response_data['purchase_price_html'] = html
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
def salesorder_addvendorvariation_ajax(request):
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id) 
        vendorproducts = product.vendorproduct_set.all()
        vendors = []
        for vendorproduct in vendorproducts:
            vendors.append(vendorproduct.vendor)
        rendered = render_to_string('deals/helper_ajax/salesorder_addvendorvariation.html', context = {'product':product,'vendors':vendors},request=request)
        return JsonResponse({'salesorder_addvendorvariation_ajax_snippet': rendered})
def estimate_addvendorvariation_ajax(request):
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id) 
        vendorproducts = product.vendorproduct_set.all()
        vendors = []
        for vendorproduct in vendorproducts:
            vendors.append(vendorproduct.vendor)
        rendered = render_to_string('deals/helper_ajax/estimate_addvendorvariation.html', context = {'product':product,'vendors':vendors},request=request)
        return JsonResponse({'estimate_addvendorvariation_ajax_snippet': rendered})

def salesorder_addvendor_ajax(request):
    
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id)
        
        vendors = ContactVendor.objects.all().order_by("contact_name")
        vendorproducts = VendorProduct.objects.filter(product = product)

        for vendorproduct in vendorproducts:
            if vendorproduct.vendor in vendors:
                vendors = vendors.exclude(contact_id = vendorproduct.vendor.contact_id)
                
        rendered = render_to_string('deals/helper_ajax/salesorder_addvendor.html', context = {'product':product,'vendors':vendors},request=request)
        return JsonResponse({'salesorder_addvendor_ajax_snippet': rendered})
    if request.method == "POST":
        vendor_id = request.POST.get('vendor')
        product_id = request.POST.get('product_id')
        expiry = request.POST.get('expiry')
        price = request.POST.get('price')
        specs = request.POST.get('specs')
        quantity = request.POST.get('quantity')
        delivery_terms = request.POST.get('delivery_terms')
        salesorder_id = request.POST.get('salesorder_id')
        label_name = request.POST.get('label_name')



        
        salesorder = ZohoSalesOrder.objects.get(salesorder_id = salesorder_id)
        
        product= Product.objects.get(item_id = product_id)

        d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id= vendor_id ),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
        d1.save()
        dp = DealVendorProduct(
            deal = DealVendor.objects.get(id = d1.id),
            specs = specs,
            vendor_price = float(price),
            quantity = float(quantity),
            price_valid_till = expiry , 
            product = product,
            label_name = label_name,

            )
        dp.save()
        html = "<option value='' selected>Select Purchase Price From Active Deals</option>"
        for vendorproduct in product.vendorproduct_set.all():
            html = html + "<optgroup style='font-size:109%;color:black;' label='Vendor: " +vendorproduct.vendor.contact_name +" || Payment Terms: "+ vendorproduct.vendor.payment_terms  +"|| Location: "+ vendorproduct.vendor.place_of_contact +"'>"
            
            for i,vendorproductvariation in enumerate(vendorproduct.vendorproductvariation_set.all()):

                html = html+ "<option style='color:black;' class='"
                
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html+"bg-success'"
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0:
                    html = html+ "bg-warning'" 
                else:
                    html = html+"bg-danger'"
                html = html+ "value="+str(vendorproductvariation.id)+" data-item_id = "+str(product.item_id)+" data-purchase_price="+str(vendorproductvariation.dealvendorproduct.vendor_price)+" data-customer_freight="+str(salesorder.buyer.freight_per_kg)+" data-vendor_freight="+str(vendorproduct.vendor.freight_per_kg )+"  data-vpt="+str(vendorproduct.vendor.payment_terms_no)+" data-bpt ="+str(salesorder.buyer.payment_terms_no)+">>> Variation -"+ str(i+1)+" || Specs:"+ vendorproductvariation.dealvendorproduct.specs +"| Pack-size:" +str(vendorproductvariation.dealvendorproduct.quantity ) +"|| Price:"+str(vendorproductvariation.dealvendorproduct.vendor_price )+" || ( "
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html + "Will expire in " +str(vendorproductvariation.dealvendorproduct.expiry_status)+" day(s). "
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0 :
                    html = html + "Expires Today "
                else:
                    html = html + "Expired " +str(vendorproductvariation.dealvendorproduct.expiry_status*(-1))+" day(s) ago."
                html = html + ") </option></optgroup>"
        
        response_data = {}
        response_data['vendor'] = vendor_id
        response_data['product_id'] = product_id
        response_data['expiry'] = expiry
        response_data['price'] = price
        response_data['specs'] = specs
        response_data['quantity'] = quantity
        response_data['delivery_terms'] = delivery_terms
        response_data['purchase_price_html'] = html
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
def estimate_addvendor_ajax(request):
    
    if request.method == "GET":
        item_id = request.GET.get('slug',None)
        product = Product.objects.get(item_id = item_id)
        
        vendors = ContactVendor.objects.all().order_by("contact_name")
        vendorproducts = VendorProduct.objects.filter(product = product)

        for vendorproduct in vendorproducts:
            if vendorproduct.vendor in vendors:
                vendors = vendors.exclude(contact_id = vendorproduct.vendor.contact_id)
                
        rendered = render_to_string('deals/helper_ajax/estimate_addvendor.html', context = {'product':product,'vendors':vendors},request=request)
        return JsonResponse({'estimate_addvendor_ajax_snippet': rendered})
    if request.method == "POST":
        vendor_id = request.POST.get('vendor')
        product_id = request.POST.get('product_id')
        expiry = request.POST.get('expiry')
        price = request.POST.get('price')
        specs = request.POST.get('specs')
        quantity = request.POST.get('quantity')
        delivery_terms = request.POST.get('delivery_terms')
        estimate_id = request.POST.get('estimate_id')
        label_name = request.POST.get('label_name')



        estimate = ZohoEstimate.objects.get(estimate_id = estimate_id)
        product= Product.objects.get(item_id = product_id)

        d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id= vendor_id ),
                created_by = request.user,
                delivery_terms = delivery_terms

                )
        d1.save()
        dp = DealVendorProduct(
            deal = DealVendor.objects.get(id = d1.id),
            specs = specs,
            vendor_price = float(price),
            quantity = float(quantity),
            price_valid_till = expiry , 
            product = product,
            label_name = label_name,

            )
        dp.save()
        html = "<option value='' selected>Select Purchase Price From Active Deals</option>"
        for vendorproduct in product.vendorproduct_set.all():
            html = html + "<optgroup style='font-size:109%;color:black;' label='Vendor: " +vendorproduct.vendor.contact_name +" || Payment Terms: "+ vendorproduct.vendor.payment_terms  +"|| Location: "+ vendorproduct.vendor.place_of_contact +"'>"
            
            for i,vendorproductvariation in enumerate(vendorproduct.vendorproductvariation_set.all()):

                html = html+ "<option style='color:black;' class='"
                
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html+"bg-success'"
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0:
                    html = html+ "bg-warning'" 
                else:
                    html = html+"bg-danger'"
                html = html+ "value="+str(vendorproductvariation.id)+" data-item_id = "+str(product.item_id)+" data-purchase_price="+str(vendorproductvariation.dealvendorproduct.vendor_price)+" data-customer_freight="+str(estimate.buyer.freight_per_kg)+" data-vendor_freight="+str(vendorproduct.vendor.freight_per_kg )+"  data-vpt="+str(vendorproduct.vendor.payment_terms_no)+" data-bpt ="+str(estimate.buyer.payment_terms_no)+">>> Variation -"+ str(i+1)+" || Specs:"+ vendorproductvariation.dealvendorproduct.specs +"| Pack-size:" +str(vendorproductvariation.dealvendorproduct.quantity ) +"|| Price:"+str(vendorproductvariation.dealvendorproduct.vendor_price )+" || ( "
                if vendorproductvariation.dealvendorproduct.expiry_status > 0 :
                    html = html + "Will expire in " +str(vendorproductvariation.dealvendorproduct.expiry_status)+" day(s). "
                elif vendorproductvariation.dealvendorproduct.expiry_status == 0 :
                    html = html + "Expires Today "
                else:
                    html = html + "Expired " +str(vendorproductvariation.dealvendorproduct.expiry_status*(-1))+" day(s) ago."
                html = html + ") </option></optgroup>"
        
        response_data = {}
        response_data['vendor'] = vendor_id
        response_data['product_id'] = product_id
        response_data['expiry'] = expiry
        response_data['price'] = price
        response_data['specs'] = specs
        response_data['quantity'] = quantity
        response_data['delivery_terms'] = delivery_terms
        response_data['purchase_price_html'] = html
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
        


def sales_ajax(request):

    
    item_id = request.GET.get('slug',None)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    base_url = "https://books.zoho.com/api/v3"
    page_number = 1
    list_invoices = []
    parameters['item_id'] = item_id
    parameters['sort_column'] = 'date'
    for i in itertools.count():
        parameters['page'] = page_number + i
        response = requests.get(base_url + end_points['invoices'],params = parameters)
        invoices = response.json()['invoices']
        list_invoices.append(invoices)
        print(parameters)
        if(response.json()['page_context']['has_more_page'] != True):
            break
    print(list_invoices)
    for page in list_invoices:
        for invoice in page:
            date=invoice['date']
            invoice['date'] = datetime.datetime.strptime(date,'%Y-%m-%d').strftime('%B %d,%Y')
    rendered = render_to_string('deals/helper_ajax/sales_history.html', context = {'list_invoices':list_invoices})

    return JsonResponse({'product_snippet': rendered})

def purchase_ajax(request):
    
    
    item_id = request.GET.get('slug',None)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    base_url = "https://books.zoho.com/api/v3"
    page_number = 1
    list_bills = []
    parameters['item_id'] = item_id
    parameters['sort_column'] = 'date'
    for i in itertools.count():
        parameters['page'] = page_number + i
        response = requests.get(base_url + end_points['bills'],params = parameters)
        bills = response.json()['bills']
        list_bills.append(bills)
        print(parameters)
        if(response.json()['page_context']['has_more_page'] != True):
            break
    print(list_bills)
    for page in list_bills:
        for bill in page:
            date=bill['date']
            bill['date'] = datetime.datetime.strptime(date,'%Y-%m-%d').strftime('%B %d,%Y')
    rendered = render_to_string('deals/helper_ajax/purchase_history.html', context = {'list_bills':list_bills})

    return JsonResponse({'product_snippet': rendered})


def coa_view_ajax(request):
    item_id = request.GET.get('slug',None)
    product = Product.objects.get(pk=item_id)
    coa_list = CoaFile.objects.filter(product=product)
    rendered = render_to_string('deals/helper_ajax/coa_files.html', context = {'coa_files':coa_list})
    return JsonResponse({'product_snippet':rendered})

def recent_deals_ajax(request):
    item_id = request.GET.get('slug',None)
    product = Product.objects.get(pk=item_id)
    product_group = product.group
    deals = []
    for product in product_group.product_set.all():
        for deal in product.dealvendorproduct_set.all():
            deals.append(deal)
    
    
    rendered = render_to_string('deals/helper_ajax/recent_deals.html',context={'recent_deals':deals,'product_group':product_group})

    return JsonResponse({'product_snippet': rendered})
    
def coa_delete_ajax(request,pk):
    coafile = CoaFile.objects.get(id=pk)
    data = dict()
    if request.method == 'POST':
        coafile.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        coafiles = CoaFile.objects.all()
        data['html_book_list'] = render_to_string('deals/helper_ajax/partial_coafile_list.html', {
            'coafiles': coafiles
        })
    else:
        context = {'coafile': coafile}
        data['html_form'] = render_to_string('deals/helper_ajax/partial_coafile_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def graph_ajax(request):
    item_id = request.GET.get('slug',None)
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    parameters={'authtoken':auth_token,'organization_id':organization_id}
    base_url = "https://books.zoho.com/api/v3"
    page_number = 1
    list_invoices = []
    parameters['item_id'] = item_id
    parameters['sort_column'] = 'date'
    for i in itertools.count():
        parameters['page'] = page_number + i
        response = requests.get(base_url + end_points['invoices'],params = parameters)
        invoices = response.json()['invoices']
        list_invoices.append(invoices)
        print(parameters)
        if(response.json()['page_context']['has_more_page'] != True):
            break
    print(list_invoices)
    flat_list_invoices = []
    for page in list_invoices:
        for invoice in page:
            flat_list_invoices.append(invoice)
    
    list_bills = []
    
    
    for i in itertools.count():
        parameters['page'] = page_number + i
        response = requests.get(base_url + end_points['bills'],params = parameters)
        bills = response.json()['bills']
        list_bills.append(bills)
        print(parameters)
        if(response.json()['page_context']['has_more_page'] != True):
            break
    print(list_bills)

    flat_list_bills = []

    for page in list_bills:
        for bill in page:
            flat_list_bills.append(bill)

    product = Product.objects.get(pk=item_id)
    product_group = product.group
    deals = []
    for product in product_group.product_set.all():
        for deal in product.dealvendorproduct_set.all():
            deals.append(deal)
    data_invoices = []
    for invoice in flat_list_invoices:
        
        data_invoices.append({'x': invoice['date'] , 'y':invoice['item_price']})
    data_bills = []
    for bill in flat_list_bills:
        data_bills.append({'x':bill['date'],'y':bill['item_price']})

    data_deals = []
    for deal in deals:
        data_deals.append({'x':deal.deal.date,'y':deal.vendor_price})
    
    rendered = render_to_string('deals/helper_ajax/summary_graph.html',context={'item_id':item_id,'flat_list_invoices':flat_list_invoices,'data_bills':data_bills,'data_invoices':data_invoices,'product_name': product.name,'data_deals':data_deals})

    return JsonResponse({'product_snippet': rendered})

def vendor_deal_view(request):
    deal_id = request.GET.get('slug',None)
    if request.method=='GET':
        vendor_deal = DealVendor.objects.get(id=deal_id)
        
        rendered = render_to_string('deals/helper_ajax/vendor_deal_view.html',context={'vendor_deal':vendor_deal})

        return JsonResponse({'deal_snippet': rendered})

def vendor_deal_delete(request):
    deal_id = request.GET.get('slug',None)
    if request.method=='GET':
        vendor_deal = DealVendor.objects.get(id=deal_id)
        rendered = render_to_string('deals/helper_ajax/vendor_deal_delete.html',context={'vendor_deal':vendor_deal},request=request)
        return JsonResponse({'deal_snippet':rendered})
    if request.method=='POST':
        vendor_deal_id = request.POST.get('vendor-deal-id')
        vendor_deal = DealVendor.objects.get(id=vendor_deal_id)
        vendor_deal.delete()
        call_command('update_vendorproducts_from_vendordeals')
        return redirect('deal_vendor_list')

def vendor_deal_edit(request):
    deal_id = request.GET.get('slug',None)
    if request.method == 'GET':
        deal = DealVendor.objects.get(id=deal_id)
        vendors = ContactVendor.objects.all().order_by('contact_name')
        makes = Make.objects.all().order_by('name')
        units = Unit.objects.all()
        product_groups =ProductGroup.objects.all().order_by('name')
        products =Product.objects.all().order_by('name')
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        
        rendered = render_to_string('deals/helper_ajax/single_vendor_dealeditform.html',context={'deal':deal,'vendors':vendors,'makes':makes,'units':units,'product_groups':product_groups,'products':products,'today':today},request=request)

        return JsonResponse({'form_snippet': rendered})
    if request.method == 'POST':
        deal_id = request.POST.get('deal_id')
        print('DealID----------------->',deal_id)
        deal = DealVendor.objects.get(id=deal_id)
        products = request.POST.getlist('product')
        label_names = request.POST.getlist('label_name')
        specs = request.POST.getlist('spec')
        quantitys = request.POST.getlist('quantity')
        prices = request.POST.getlist('price')
        lead_times = request.POST.getlist('lead_time')
        price_valid_tills = request.POST.getlist('price_valid_till')
        for dealproduct in deal.dealvendorproduct_set.all():
            print('first----------->',products)
            for i,product in enumerate(products):
                print('second--------------->',product,dealproduct)
                if (dealproduct.product.pk == product):
                    if(price_valid_tills[i]==''):
                        price_valid_till = None
                    else:
                        price_valid_till = price_valid_tills[i]
                    if(lead_times[i]==''):
                        lead_time = None
                    else:
                        lead_time = lead_times[i]
                    if(quantitys[i]==''):
                        quantity = None
                    else:
                        quantity = quantitys[i]

                    dealproduct.label_name = label_names[i]
                    dealproduct.specs = specs[i]
                    dealproduct.quantity = quantity
                    dealproduct.vendor_price = prices[i]
                    dealproduct.lead_time = lead_time
                    dealproduct.price_valid_still = price_valid_till
                    dealproduct.save()
        return redirect('deal_vendor_list')
        
def single_vendor_dealform(request):
    if request.method=='GET':

        vendors = ContactVendor.objects.all().order_by('contact_name')
        makes = Make.objects.all().order_by('name')
        units = Unit.objects.all()
        product_groups =ProductGroup.objects.all().order_by('name')
        products =Product.objects.all().order_by('name')
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        rendered = render_to_string('deals/helper_ajax/single_vendor_dealform.html',context={'vendors':vendors,'makes':makes,'units':units,'product_groups':product_groups,'products':products,'today':today},request=request)

        return JsonResponse({'form_snippet': rendered})
    if request.method=='POST':
        date = request.POST.get('date')
        vendor = request.POST.get('vendor')
        print(date,'------------------------>',vendor)
        delivery_terms = request.POST.get('delivery_terms')

        d1 = DealVendor(
            vendor = ContactVendor.objects.get(pk=vendor),
            delivery_terms= delivery_terms,
            date = date,
            created_by=request.user,
        )
        d1.save()
        label_names = request.POST.getlist('label_name')
        makes = request.POST.getlist('make')
        productslist=request.POST.getlist('products[]')
        products=[]
        for product in productslist:
            products = [Product.objects.get(pk=product)] + products
        print(label_names,'------------------------>',makes,'------------->',products)
        product_groups =request.POST.getlist('product_group')
        specs = request.POST.getlist('spec')

        units = request.POST.getlist('unit')
        quantitys = request.POST.getlist('quantity')
        prices = request.POST.getlist('price')
        lead_times = request.POST.getlist('lead_time')
        price_valid_tills = request.POST.getlist('price_valid_till')
        product_list=[]
        for i,label_name in enumerate(label_names):
            if(makes[i]==''):
                make=None
            else:
                try:
                    make = Make.objects.filter(name=makes[i])[0]
                except:
                    make = None
            if(price_valid_tills[i]==''):
                price_valid_till = None
            else:
                price_valid_till = price_valid_tills[i]
            if(lead_times[i]==''):
                lead_time = None
            else:
                lead_time = lead_times[i]
            if(quantitys[i]==''):
                quantity = None
            else:
                quantity = quantitys[i]

            try:
                unit = Unit.objects.filter(name=units[i])[0]
            except:
                unit = None
            try: 
                product_group = ProductGroup.objects.get(id = product_groups[i])
            except:
                product_group = None
            
            p1 = DealVendorProduct(
                label_name = label_names[i],
                deal=DealVendor.objects.get(id=d1.id),
                make = make,
                product = products[i],
                
                
                specs = specs[i],
                quantity = quantity,
                vendor_price = prices[i],
                lead_time = lead_time,
                unit = unit,
                price_valid_till = price_valid_till,

                )
           
            product_list = [p1] + product_list
        DealVendorProduct.objects.bulk_create(product_list)
        return redirect('deal_vendor_list')

def googlechartsapp_ajax(request,**kwargs):
    if request.method == 'GET':

        item_id = request.GET.get('slug',None)
        print(str(item_id))
        product=Product.objects.get(pk=item_id)
        product_name = product.name
        product_pk = product.pk
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_id = '667580392'
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        base_url = "https://books.zoho.com/api/v3"
        page_number = 1
        list_invoices = []
        parameters['item_id'] = item_id
        parameters['sort_column'] = 'date'
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['invoices'],params = parameters)
            invoices = response.json()['invoices']
            list_invoices.append(invoices)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
    
        flat_list_invoices = []
        for page in list_invoices:
            for invoice in page:
                flat_list_invoices.append(invoice)
    
        list_bills = []
    
    
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['bills'],params = parameters)
            bills = response.json()['bills']
            list_bills.append(bills)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
    

        flat_list_bills = []

        for page in list_bills:
            for bill in page:
                flat_list_bills.append(bill)

        
        print('----------->',product.name)
        product_group = product.group
        deals = []
        try:
            for dealproduct in product_group.product_set.all():
                for deal in dealproduct.dealvendorproduct_set.all():
                    deals.append(deal)
        except:
            pass
        data_invoices = []
        for invoice in flat_list_invoices:
        
            y = int(invoice['date'].split('-')[0])
            m = int(invoice['date'].split('-')[1]) - 1
            d = int(invoice['date'].split('-')[2])
        
            date = (y,m,d)
            sales = invoice['item_price']
            purchase = 'null'
            vendor_deals = []
            for deal in deals:
                vendor_deals = ['null'] + vendor_deals
            contact=invoice['customer_name']
            contact_type = 'Customer'
            item = product.name
            
            if (ContactBuyer.objects.get(contact_id = invoice['customer_id']).place_of_contact):
                customer_location = ContactBuyer.objects.get(contact_id = invoice['customer_id']).place_of_contact
            else:
                customer_location = 'No Location In Zoho'

            tooltip_sales = "<div class='container'> <h4 class='btn btn-primary' style='display:block;margin-top:3%;text-align:center;'> Sales </h4><table> <tr><th>Date </th><th>"+ str(invoice['date'])+"</th></tr><tr><th> Product </th><th>"+str(item)+"</th></tr><tr> <th>Price</th><th>("+str(invoice['currency_code'])+") "+str(sales)+"</th></tr> <tr><th> Quantity </th><th>"+str(invoice['item_quantity'])+"("+str(product.unit)+") </th></tr><tr><th> Customer </th><th>"+str(invoice['customer_name'])+"</th></tr><tr><th>Customer Location</th><th>"+ str(customer_location) +"</th></tr> </table></div>"

            invoice = [date,sales,tooltip_sales,purchase,'null','null','null',customer_location,contact,'null',item]
            data_invoices.append(invoice)
        data_bills = []
        for bill in flat_list_bills:
            y = int(bill['date'].split('-')[0])
            m = int(bill['date'].split('-')[1]) - 1
            d = int(bill['date'].split('-')[2])
            date = (y,m,d)
            sales = 'null'
            purchase = bill['item_price']
            vendor_deals = []
            for deal in deals:
                vendor_deals = ['null'] + vendor_deals
            contact = bill['vendor_name']
            contact_type = 'Vendor'
            item = product.name
            if (ContactVendor.objects.get(contact_id = bill['vendor_id']).place_of_contact):
                vendor_location = ContactVendor.objects.get(contact_id = bill['vendor_id']).place_of_contact
            else:
                vendor_location ='No Location In Zoho'
            tooltip_purchase =  "<div class='container'> <h4 class='btn btn-danger' style='display:block;margin-top:3%;text-align:center;'>Purchases</h4><table> <tr><th>Date </th><th>"+ str(bill['date'])+"</th></tr><tr><th> Product </th><th>"+str(item)+"</th></tr><tr> <th>Price</th><th>("+str(bill['currency_code'])+") "+str(purchase)+"</th></tr> <tr><th> Quantity </th><th>"+str(bill['item_quantity'])+" ( "+str(product.unit)+") </th></tr><tr><th> Vendor </th><th>"+str(bill['vendor_name'])+"</th></tr> <tr><th>Vendor Location</th><th>"+ str( vendor_location ) +"</th></tr></table></div>"

            bill = [date,sales,'null',purchase,tooltip_purchase,'null','null',vendor_location,'null',contact,item]
            data_bills.append(bill)
    
        data_deals = []
        for i,deal in enumerate(deals):
            y = int(deal.deal.date.strftime('%Y-%m-%d').split('-')[0])
            m = int(deal.deal.date.strftime('%Y-%m-%d').split('-')[1])
            d = int(deal.deal.date.strftime('%Y-%m-%d').split('-')[2])
            date = (y,m,d)
            sales='null'
            purchase='null'
        
            contact = deal.deal.vendor.contact_name

            if(deal.deal.vendor.place_of_contact):
                vendor_location = deal.deal.vendor.place_of_contact
            else:
                vendor_location = "No Location In Zoho"
            try:
                unit = deal.product.unit
            except:
                unit = "None"
            try:
                name = deal.product.name
            except:
                name="None"

            tooltip_vendordeals = " <div class='container'><h4 class='btn btn-warning' style='display:block;margin-top:3%;text-align:center;'>Recent Vendor Deals</h4><table> <tr><th>Date</th><th>"+ str(deal.deal.date)+"</th></tr><tr><th>Expiry Date</th><th>"+str( deal.price_valid_till )+"</th></tr><tr><th>Price</th><th>(INR) "+str(deal.vendor_price)+" </th> </tr><tr><th> Quantity</th> <th>"+str(deal.quantity)+" ( "+str(unit)+" ) </th></tr> <tr><th>Vendor</th><th> "+str(deal.deal.vendor.contact_name )+" </th></tr> <tr><th>Vendor Location</th><th>"+ str(vendor_location) +"</th></tr><tr><th> Product </th><th> "+str(name)+"</th> </tr><tr><th> Label Name </th> <th>"+str(deal.label_name)+"</th></tr></table> </div>"

            vendor_deal= [date,sales,'null',purchase,'null',deal.vendor_price,tooltip_vendordeals,vendor_location,'null',contact,name]
            data_deals.append(vendor_deal)
        print(data_deals)
        vendors = ContactVendor.objects.all().order_by('contact_name')
        live_prices = []
        if(product_group):
            for product in product_group.product_set.all():
                live_price = {
                        'product': product,
                        'deals': [],
                        }
                for dealproduct in product.dealvendorproduct_set.all():
                    if(dealproduct.price_valid_till):
                        print(dealproduct.price_valid_till)
                        print(( dealproduct.price_valid_till - datetime.date.today()).days)
                        expires_in = (dealproduct.price_valid_till - datetime.date.today()).days
                        if (expires_in >= 0):
                            
                            deal = {
                            'vendor': dealproduct.deal.vendor,
                            'dealproduct': dealproduct,
                            'expires_in':expires_in,
                            }
                            live_price['deals'].append(deal)
                live_prices.append(live_price)
        print(live_prices)
        rendered = render_to_string('deals/helper_ajax/googlecharts_app.html',{'data_bills':data_bills,'data_invoices':data_invoices,'data':data_bills+data_invoices+data_deals,'deals':deals,'product_name':product_name,'product_pk':product_pk,'vendors':vendors,'product_group':product_group,'live_prices':live_prices},request=request)

        return JsonResponse({'product_snippet': rendered})

    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        vendor = ContactVendor.objects.get(contact_id = vendor_id)
        product_id = request.POST.get('product')
        product = Product.objects.get(pk = product_id)
        make_name = request.POST.get('make')
        unit_name = request.POST.get('unit')
        price = request.POST.get('price')
        expiry_date= request.POST.get('expiry-date')
        quantity = request.POST.get('quantity')
        delivery_terms = request.POST.get('delivery-terms')
        label_name = request.POST.get('label-name')
        specs = request.POST.get('specs')
        lead_time = request.POST.get('lead-time')

        try:
            make = Make.objects.filter(name=make_name)[0]
        except:
            make = None
        try:
            unit = Unit.objects.filter(name=unit_name)[0]
        except:
            unit = None
        print(vendor,product_id,make,unit,price,expiry_date,quantity)
        deal = DealVendor(
            
            vendor = vendor,
            delivery_terms= delivery_terms,
            date = datetime.date.today(),
            created_by=request.user,

        )
        deal.save()
        dealproduct = DealVendorProduct(
                label_name = label_name,
                deal=DealVendor.objects.get(id=deal.id),
                make = make,
                product = product,
                
                
                specs = specs,
                quantity = quantity,
                vendor_price = price,
                lead_time = lead_time,
                unit = unit,
                price_valid_till = expiry_date,

                )
        dealproduct.save()
        


        response_data = {
            'success':'toppler',
            'vendor': vendor.contact_name ,
            'product':product.name , 
            'item_id':product.pk,
            
            'price':price,
            'expiry-date':expiry_date,
            'quantity':quantity, 
            'deal_id':deal.id,

            }
        return HttpResponse(json.dumps(response_data),content_type="application/json")
   











def dealvendor_list(request):
    table = DealVendorTable(DealVendor.objects.all(),order_by='-id')
    RequestConfig(request).configure(table)
    
    return render(request, 'deals/dealvendor_list.html', {'table': table})

