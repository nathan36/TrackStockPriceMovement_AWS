#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stock_price_alert.stock_price_alert import StockPriceAlertStack


app = cdk.App()
StockPriceAlertStack(app, "StockPriceAlertStack")

app.synth()
