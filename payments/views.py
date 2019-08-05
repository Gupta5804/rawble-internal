from django.shortcuts import render,redirect

from django.views.generic import DeleteView,CreateView
from django.urls import reverse_lazy
from django.core.management import call_command
from servicedelivery.models import PurchaseOrderProductPlan
from contacts.models import ContactVendor
from deals.models import ZohoPurchaseOrder
from django.http import JsonResponse
from django.template.loader import render_to_string
import datetime
 # Create your views here.
def schedule_payment(request):
    vendor_id = request.GET.get('vendor_id')
    selected_popp_ids = request.GET.getlist('selected_popp_ids[]')
    vendor = ContactVendor.objects.get(contact_id = vendor_id)
    popps = []
    pos = []
    total_amount = 0
    schedule_dates = []
    for selected_popp_id in selected_popp_ids:
        popp = PurchaseOrderProductPlan.objects.get(id = selected_popp_id)
        popps.append(popp)
        total_amount = total_amount + popp.total_amount_with_tax
        
        if(popp.purchaseorderproduct.purchaseorder.purchaseorder_number in pos):
            pass
        else:
            pos.append(popp.purchaseorderproduct.purchaseorder.purchaseorder_number)
        schedule_date = popp.planned_receive_date_time.date() + datetime.timedelta(days=popp.purchaseorderproduct.purchaseorder.vendor.payment_terms_no)
        if(schedule_date in schedule_dates):
            pass

        else:
            schedule_dates.append(schedule_date)

    rendered = render_to_string(
        'payments/helper_ajax/schedule_payment.html', 
        context = {
            'vendor':vendor,
            'selected_popp_ids':selected_popp_ids,
            'popps':popps,
            'pos':pos,
            'total_amount':total_amount,
            'schedule_dates':schedule_dates
            },
        request=request
        )
    
    return JsonResponse({'snippet': rendered})
def payable_pending_get_purchaseorders(request):
    vendor_id = request.GET.get('vendor_id')
    vendor = ContactVendor.objects.get(contact_id = vendor_id)
    pos_all = vendor.zohopurchaseorder_set.all()
    pos = []
    for po in pos_all:
        if(po.status == "billed" or po.status == "cancelled" ):
            pass
        else:
            pos.append(po)
    rendered = render_to_string('payments/helper_ajax/get_purchaseorders.html', context = {'pos':pos},request=request)
    
    return JsonResponse({'snippet': rendered})

def payments_payable_nextpayment(request):
    return render(request,'payments/payable_nextpayment.html')
def payments_payable_chequeapproval(request):
    return render(request,'payments/payable_chequeapproval.html')
def payments_payable_pending(request):
    
    vendor_ids = PurchaseOrderProductPlan.objects.values_list("purchaseorderproduct__purchaseorder__vendor__contact_id",flat=True).distinct().order_by()
    print(vendor_ids)
    vendors = []
    for vendor_id in vendor_ids:
        vendor= ContactVendor.objects.get(contact_id = vendor_id)
        vendors.append(vendor)
    print(vendors)
    return render(request,'payments/payable_pending.html',{'vendors':vendors})


#def advancepayment_reorder(request):
#    payments = Payment.objects.all()
#    return render(request,'payments/advance_payment_reorder.html',{'payments':payments})
#
#def payment_reorder_moveup(request,pk):
#    payment = Payment.objects.get(id=pk)
#    payment.up()
#    return redirect('advance_payment_reorder')
#def payment_reorder_movedown(request,pk):
#    payment = Payment.objects.get(id=pk)
#    payment.down()
#    return redirect('advance_payment_reorder')
