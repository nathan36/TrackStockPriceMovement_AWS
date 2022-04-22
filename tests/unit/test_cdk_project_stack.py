import aws_cdk as core
import aws_cdk.assertions as assertions

from stock_price_alert.stock_price_alert import StockPriceAlertStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_project/cdk_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StockPriceAlertStack(app, "cdk-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
