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
from payments.models import PaymentPayable,ChequePayable
 # Create your views here.
def inwarddetail(request):
    if request.method == "GET":
        pp_id = request.GET.get("pp_id")
        pp = PaymentPayable.objects.get(id = pp_id)
        
        rendered = render_to_string('payments/helper_ajax/inwarddetail.html',context = {'pp':pp},request=request)
        return JsonResponse({'snippet': rendered})

def payable_cheque_unapproved(request):
    if request.method == "GET":
        vendor_ids = PaymentPayable.objects.values_list("vendor__contact_id",flat=True).distinct().order_by()
        vendors = []
        for vendor_id in vendor_ids:
                vendor= ContactVendor.objects.get(contact_id = vendor_id)
                vendors.append(vendor)
        #pps = PaymentPayable.objects.all().order_by("-id")
        return render(request,'payments/payable_cheque_unapproved.html',{'vendors':vendors})
    
def payable_cheque_unsigned(request):
    return render(request,'payments/payable_cheque_unsigned.html')
def payable_cheque_uncleared(request):
    return render(request,'payments/payable_cheque_uncleared.html')

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
    vendor_ids = PaymentPayable.objects.values_list("vendor__contact_id",flat=True).distinct().order_by()
    vendors = []
    for vendor_id in vendor_ids:
            vendor= ContactVendor.objects.get(contact_id = vendor_id)
            vendors.append(vendor)
    #pps = PaymentPayable.objects.all().order_by("-id")
    return render(request,'payments/payable_chequeapproval.html',{'vendors':vendors})
def payments_payable_pending(request):
    if request.method == "GET":
        vendor_ids = PurchaseOrderProductPlan.objects.values_list("purchaseorderproduct__purchaseorder__vendor__contact_id",flat=True).distinct().order_by()
        print(vendor_ids)
        vendors = []
        for vendor_id in vendor_ids:
            vendor= ContactVendor.objects.get(contact_id = vendor_id)
            vendors.append(vendor)
        print(vendors)
        return render(request,'payments/payable_pending.html',{'vendors':vendors})
    if request.method == "POST":
        if "schedule-cheque" in request.POST:
            popp_ids = request.POST.getlist("popp_id")
            total_amount = request.POST.get("total_amount")
            vendor_id = request.POST.get("vendor_id")
            cheque_nos = request.POST.getlist("cheque_no")
            cheque_dates = request.POST.getlist("cheque_date")
            each_cheque_amount = float(total_amount) / len(cheque_nos)

            pp = PaymentPayable(
                mode="cheque",
                vendor = ContactVendor.objects.get(contact_id = vendor_id)

            )
            pp.save()
            for popp_id in popp_ids:
                popp = PurchaseOrderProductPlan.objects.get(id=popp_id)
                popp.paymentpayable = pp
                popp.save()
            for i,cheque_no in enumerate(cheque_nos):

                cp = ChequePayable(
                    cheque_no = cheque_no,
                    paymentpayable = pp,
                    date = cheque_dates[i],
                    amount = each_cheque_amount,

                )
                cp.save()
        return redirect("payments_payable_pending")
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
