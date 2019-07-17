from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from deals.models import DealVendor,DealVendorProduct,VendorProduct,VendorProductVariation,EstimateProduct,BuyerProduct


logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="update_buyerproduct_from_estimateproducts",
    ignore_result=True
)
def update_buyerproduct_from_estimateproducts():
    estimateproducts = EstimateProduct.objects.all()
    for estimateproduct in estimateproducts:
        buyer = estimateproduct.estimate.buyer
        product = estimateproduct.product

        try:
            buyerproduct = BuyerProduct.objects.get(buyer=buyer, product=product)

        except:
            buyerproduct = BuyerProduct(buyer=buyer, product=product)

            buyerproduct.save()