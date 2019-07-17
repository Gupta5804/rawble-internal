from django.shortcuts import render,redirect
from contacts.models import ContactVendor,ContactBuyer
from deals.models import DealVendor,DealVendorProduct,VendorProduct,VendorProductVariation,BuyerProduct
from products.models import ProductGroup,Product
import datetime
# Create your views here.
 
def vendors_listing(request):
    contacts = ContactVendor.objects.all()
    contact_type = "Vendor"
    return render(request,'contacts/contacts_listing.html',{'contacts':contacts,'contact_type':contact_type})

def buyers_listing(request):
    contacts = ContactBuyer.objects.all()
    contact_type = "Buyer"
    return render(request,'contacts/contacts_listing.html',{'contacts':contacts,'contact_type':contact_type})

def buyer_profile(request,contact_id):
    contact_id = contact_id
    if request.method == "GET":
        buyer = ContactBuyer.objects.get(contact_id = contact_id)
        buyerproducts =BuyerProduct.objects.filter(buyer = buyer).order_by('product__name')
        buyerproduct_list = []
        for buyerproduct in buyerproducts:
            buyerproduct_list.append(buyerproduct.product)
        all_product_groups = ProductGroup.objects.all().order_by('name')

        return render(request, 'contacts/buyer_profile.html', {'buyer': buyer, 'buyerproducts': buyerproducts, 'buyerproduct_list': buyerproduct_list, 'all_product_groups': all_product_groups})


def vendor_profile(request, contact_id):
    contact_id = contact_id
    if request.method == "GET":
        vendor = ContactVendor.objects.get(contact_id=contact_id)
        vendorproducts = VendorProduct.objects.filter(vendor=vendor).order_by('product__name')
        vendorproduct_list = []
        for vendorproduct in vendorproducts:
            vendorproduct_list.append(vendorproduct.product)
        all_product_groups = ProductGroup.objects.all().order_by('name')
        return render(request, 'contacts/vendor_profile_2.html', {'vendor': vendor, 'vendorproducts':vendorproducts, 'vendorproduct_list':vendorproduct_list, 'all_product_groups': all_product_groups})
    if request.method == "POST":
        if "delete_variation" in request.POST:
            id = request.POST.get("delete_variation")
            variation = VendorProductVariation.objects.get(id=id)
            vendorproduct = variation.vendorproduct
            if vendorproduct.vendorproductvariation_set.all().count() == 0:
                pass
            else:
                vendorproduct.delete()
            variation.delete()
            return redirect('vendor_profile', contact_id=contact_id)
        if "update_freight" in request.POST:
            freight = request.POST.get("freight")
            vendor = ContactVendor.objects.get(contact_id = contact_id)
            vendor.freight_per_kg = freight
            vendor.save()
            return redirect('vendor_profile',contact_id = contact_id)
        if "update_product" in request.POST:
            new_price = request.POST.get("newprice")
            dealproduct_id = request.POST.get("dealproduct_id")
            expiry = request.POST.get("expiry")
            delivery_terms = request.POST.get("delivery_terms")
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

            print(d1)
            return redirect('vendor_profile',contact_id = contact_id)
        if "delete_product" in request.POST:
            product_id = request.POST.get('product_id')
            vendor_id = request.POST.get('vendor_id')
            vendorproduct_id = request.POST.get('vendorproduct_id')
            dealproducts = DealVendorProduct.objects.filter(product = Product.objects.get(item_id = product_id),deal__vendor=ContactVendor.objects.get(contact_id = vendor_id))
            dealproducts.delete() 
            vendorproduct = VendorProduct.objects.get(id = vendorproduct_id)
            vendorproduct.delete()
            return redirect('vendor_profile',contact_id = contact_id)
        if "add_product_variation" in request.POST:
            delivery_terms = request.POST.get('delivery_terms')
            specs = request.POST.get('specs')
            vendor_price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            expiry = request.POST.get('expiry')
            product_id = request.POST.get('product_id')
            label_name = request.POST.get('label_name')
            d1 = DealVendor(
                date = datetime.date.today(),
                vendor = ContactVendor.objects.get(contact_id= contact_id),
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
            return redirect('vendor_profile',contact_id=contact_id)
        if "add_product" in request.POST:
            print("ADD_PRODUCT")
            delivery_terms = request.POST.get('delivery_terms')
            specs = request.POST.get('specs')
            vendor_price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            expiry = request.POST.get('expiry')
            product_id = request.POST.get('productid')
            label_name = request.POST.get('label_name')
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
            return redirect('vendor_profile',contact_id = contact_id)

def vendor_profile_priceupdate(request,dealproduct_id):
    if request.method == "GET":
        pass    