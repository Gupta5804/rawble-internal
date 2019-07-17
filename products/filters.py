from django_filters import FilterSet

from products.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {"name": ["exact", "icontains"], "make": ["exact","icontains"],"status":["exact"],"group":["exact"]}