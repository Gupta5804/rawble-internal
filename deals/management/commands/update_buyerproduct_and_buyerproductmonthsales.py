from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import DealVendor,DealVendorProduct,VendorProduct,VendorProductVariation,EstimateProduct,BuyerProduct
import pandas as pd

class Command(BaseCommand):
    help = 'Updates Buyer Products And Buyer Product Month Sales'
    def handle(self,*args,**kwargs):
        df_so = pd.read_excel("Sales_Order.xls",sheet_name="Sales Order")
        print(df_so.columns)
        #['Order Date', 'Shipment Date', 'SalesOrder Number', 'Status','Customer Name', 'Place of Supply', 'Place of Supply(With State Code)','GST Treatment', 'GST Identification Number (GSTIN)','Is Inclusive Tax', 'PurchaseOrder','Template Name', 'Currency Code','Exchange Rate', 'Discount Type', 'Is Discount Before Tax','Entity Discount Amount', 'Entity Discount Percent', 'Item Name','Product ID', 'SKU', 'UPC', 'MPN', 'EAN', 'ISBN', 'Account','Item Desc', 'QuantityOrdered', 'QuantityInvoiced', 'QuantityCancelled','Usage unit', 'Warehouse Name', 'Item Price', 'Discount','Discount Amount', 'HSN/SAC', 'Supply Type', 'Tax ID', 'Item Tax','Item Tax %', 'Item Tax Amount', 'Item Tax Type', 'CGST Rate %','SGST Rate %', 'IGST Rate %', 'CESS Rate %', 'CGST(FCY)', 'SGST(FCY)','IGST(FCY)', 'CESS(FCY)', 'CGST', 'SGST', 'IGST', 'CESS','Item Tax Exemption Reason', 'Item Type', 'Pack Size', 'Project ID','Project Name', 'Item Total', 'SubTotal', 'Total', 'Shipping Charge','Adjustment', 'Adjustment Description', 'Sales person','Notes','Terms & Conditions','Delivery Method', 'Source','Billing Address','Billing City', 'Billing State', 'Billing Country', 'Billing Code','Billing Fax', 'Billing Phone', 'Shipping Address', 'Shipping City','Shipping State', 'Shipping Country', 'Shipping Code', 'Shipping Fax','Shipping Phone', 'Item.CF.Make', 'Item.CF.Pack Size','Item.CF.Unit Of Measurement', 'Item.CF.Pack Size Detail','CF.Delivery type', 'CF.Payment Terms', 'CF.Salesperson','CF.Shipment date', 'CF.Payment Term']
        buyers = []
        for index, rows in df_so.iterrows():
            print(rows['Order Date'])
