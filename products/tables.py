import django_tables2 as tables
from products.models import Product,ProductGroup
from contacts.models import ContactVendor


class ProductTable(tables.Table):
    vendors = tables.TemplateColumn(template_name='products/vendor_column.html', extra_context={'vendors': ContactVendor.objects.all().order_by("contact_name")})
    info = tables.TemplateColumn(template_name='products/info.html', extra_context={'product_group': ProductGroup.objects.all().order_by("name")})
    coa_files = tables.TemplateColumn(template_name='products/coa_file.html')

    class Meta:
        model = Product
        sequence = ('group','name','hsn_or_sac','make','vendors','status','info')
        exclude = ('description','item_id','sku','stock_on_hand','unit','product_type')
        template_name = 'django_tables2/semantic.html'
        widgets = {
            'id': 'example',
        }