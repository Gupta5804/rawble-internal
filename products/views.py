from django.shortcuts import render,redirect
from deals.models import DealVendor,DealVendorProduct,VendorProductVariation,VendorProduct
from contacts.models import ContactVendor
from products.models import Product,ProductGroup,Make,CoaFile
from django.views.generic import ListView,DetailView
from django.views.generic.edit import CreateView,DeleteView
from django.urls import reverse_lazy
import requests
import json
import itertools
from django.http import HttpResponse
import xlwt
from django.views import View
from products.forms import CoaFileForm, ProductGroupForm
from django.http import JsonResponse
from products.tables import ProductTable
from django_tables2 import RequestConfig
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from products.filters import ProductFilter
import datetime
class CoaFileUploadView(View):
    def get(self, request , pk):
        
        product = Product.objects.get(pk=pk)
        coa_list = CoaFile.objects.filter(product=product)
        return render(self.request, 'products/product_coa_files.html', {'coa_files': coa_list,'product_pk':pk,'product':product})

    def post(self, request , pk):
        form = CoaFileForm(self.request.POST, self.request.FILES)
        
        
        if form.is_valid():
            print('1')
            file = form.save(commit=False)
            #product = form.cleaned_data['product']
            #uploaded_by = form.cleaned_data['uploaded_by']
            file.product = Product.objects.get(pk=pk)
            file.uploaded_by = request.user
            #print(file)
            file.save()
            data = {'is_valid': True, 'name': file.file.name, 'url': file.file.url , 'date':file.uploaded_at,'uploaded_by': file.uploaded_by.first_name}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    
    
def recent_deals(request,pk):
    product = Product.objects.get(pk=pk)
    product_group = product.group
    try:
        deals = product_group.dealvendorproduct_set.all().order_by('-deal')
    except:
        deals=[]
    print(deals)
    return render(request,'deals/recent_deals.html',{'product':product,'product_group':product_group,'deals':deals})
# Create your views here.
def product_sales_history(request,pk):
    p1 = Product.objects.get(pk=pk)
    base_url = "https://books.zoho.com/api/v3"
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'

    parameters={'authtoken':auth_token,'organization_id':organization_id}
    parameters['item_id'] = pk
    page_number = 1
    list_invoices = []
    
    for i in itertools.count():
        parameters['page'] = page_number + i
        response = requests.get(base_url + end_points['invoices'],params = parameters)
        invoices = response.json()['invoices']
        list_invoices.append(invoices)
        print(parameters)
        if(response.json()['page_context']['has_more_page'] != True):
            break
    
    
    print(list_invoices)
    
    return render(request,'products/product_sales_history.html',{'invoices':list_invoices,'product':p1})

def product_purchase_history(request,pk):
    p1 = Product.objects.get(pk=pk)
    base_url = "https://books.zoho.com/api/v3"
    end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
    auth_token = 'd56b2f2501f266739e12b86b706d0078'
    organization_id = '667580392'

    parameters={'authtoken':auth_token,'organization_id':organization_id}
    parameters['item_id'] = pk
    page_number = 1
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
    return render(request,'products/product_purchase_history.html', {'bills': list_bills, 'product': p1})
def products_listing(request):
    if request.method == "GET":
        table = ProductTable(Product.objects.all(),order_by='group')
        filter = ProductFilter
        form = ProductGroupForm()
        RequestConfig(request, paginate={'per_page': 2}).configure(table)
        return render(request, 'products/products_list.html', {'table': table, 'filter': filter, 'form': form})
    if request.method == "POST":
        if "delete_coafile" in request.POST:
            coafile_pk = request.POST.get('delete_coafile')
            coafile = CoaFile.objects.get(id=coafile_pk)
            coafile.delete()
        if "delete_vendorproduct" in request.POST:
            vendorproduct_pk = request.POST.get('delete_vendorproduct')
            vendorproduct = VendorProduct.objects.get(id=vendorproduct_pk)
            vendorproduct.delete()

        if "delete_variation" in request.POST:
            variation_pk = request.POST.get('delete_variation')
            variation = VendorProductVariation.objects.get(id=variation_pk)
            vendorproduct = variation.vendorproduct
            if vendorproduct.vendorproductvariation_set.all().count() == 0:
                pass
            else:
                vendorproduct.delete()
            variation.delete()
        if "groupselected" in request.POST:
            product_group_pk = request.POST.get('product_group')
            product_group_pk = int(product_group_pk)
            product_group = ProductGroup.objects.get(pk=product_group_pk)
            primary_key = request.POST.get('pk')
            primary_key = int(primary_key)
            product = Product.objects.get(pk=primary_key)
            product.group =product_group
            product.save()
        if "groupmade" in request.POST:
            name = request.POST.get('groupmade')
            product_group = ProductGroup(name=name)
            product_group.save()
            primary_key = request.POST.get('pk')
            primary_key = int(primary_key)
            product = Product.objects.get(pk=primary_key)
            product.group = product_group
            product.save()
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
                date=datetime.date.today(),
                vendor=ContactVendor.objects.get(contact_id= contact_id ),
                created_by=request.user,
                delivery_terms=delivery_terms

                )
            d1.save()
            dp = DealVendorProduct(
                deal=DealVendor.objects.get(id=d1.id),
                specs=specs,
                vendor_price=vendor_price,
                quantity=quantity,
                price_valid_till=expiry,
                product=Product.objects.get(item_id=product_id),
                label_name=label_name,

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
        
        if "add_product_variation" in request.POST:
            
            contact_id = request.POST.get('contact_id')
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
            
        
            
        return redirect('products_listing')

class FilteredProductListView(SingleTableMixin, FilterView):
    table_class = ProductTable
    model = Product
    template_name = "products/products_list.html"

    filterset_class = ProductFilter

    def get_queryset(self):
        return super(FilteredProductListView, self).get_queryset()

    def get_table_kwargs(self):
        return {"template_name": "django_tables2/semantic.html","order_by":"group"}


# class ProductGroupListView(ListView):
#     model = ProductGroup
#     form_class = ProductGroupForm()
def ProductGroupList(request):
    productgroup_list = ProductGroup.objects.all()
    form = ProductGroupForm()
    return render(request, 'products/productgroup_list.html', {"productgroup_list":productgroup_list,"form":form})
    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #
    #    context["total_products"] = ProductGroup.objects.product_set.count()
    #    return context

class ProductGroupDetailView(DetailView):
    model = ProductGroup

# class ProductGroupCreateView(CreateView):
#     model = ProductGroup
#     fields = ['name']
#     success_url = reverse_lazy('product_group_list')
def ProductGroupCreate(request):
    if request.method == 'POST':
        response_data = dict()
        post_text=request.POST.get('the_post')

        product_group = ProductGroup()
        product_group.name = post_text
        product_group.save()
        response_data['result'] = 'created group successfully'
        response_data['pk'] = product_group.pk
        response_data['name'] = product_group.name

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

class ProductGroupDeleteView(DeleteView):
    model = ProductGroup
    success_url = reverse_lazy('product_group_list')


def product_group_product_remove(request,pk1,pk2):

    product = Product.objects.get(pk = pk2)
    product.group = None
    product.save()
    return redirect('product_group_detail',pk = pk1)

def product_group_add_products(request,pk1):
    if request.method=='GET':
        products = Product.objects.all()
        group = ProductGroup.objects.get(pk=pk1)
        return render(request,'products/product_group_add_product.html',{'products':products,'group':group})
    if request.method=='POST':
        new_products = request.POST.getlist('products')
        group = ProductGroup.objects.get(pk=pk1)
        for new_product in new_products:
            product = Product.objects.get(pk = new_product)
            product.group = group
            product.save()
        print(new_products)
        return redirect('product_group_detail',pk=pk1)

class MakeListView(ListView):
    model = Make

class MakeCreateView(CreateView):
    model = Make
    fields =['name']
    success_url = reverse_lazy('make_list')

class MakeDeleteView(DeleteView):
    model= Make
    success_url = reverse_lazy('make_list')


def filtering_query(request):
    if request.method == 'POST':
        name = request.POST.get('name_field')
        make = request.POST.get('make_field')
        status = request.POST.get('status_field')
        name = str(name)
        make = str(make)
        status = str(status)
        queryset = Product.objects.all()
        if name is not (None or ''):
            queryset = queryset.filter(name__icontains=name)
        print (queryset)
        if make is not (None or ''):
            queryset = queryset.filter(make__icontains=make)
        print (queryset)
        if status is not 'both':
            queryset = queryset.filter(status=status)

        response = export_users_xls(queryset)

    return response


def export_users_xls(query_set):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Products')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = [ 'Group', 'Item Id', 'hsn_or_sac', 'Name', 'Description', 'Unit', 'Status', 'Product Type', 'Sku', 'Make', 'Stock on Hand' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    objects = query_set
    for obj in objects:
        row_num += 1
        row = [str(obj.group), str(obj.item_id), str(obj.hsn_or_sac), str(obj.name), str(obj.description), str(obj.unit), str(obj.status), str(obj.product_type), str(obj.sku), str(obj.make), str(obj.stock_on_hand)]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
