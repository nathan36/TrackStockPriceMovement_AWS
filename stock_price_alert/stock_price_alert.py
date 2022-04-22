from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_events as events,
    aws_lambda_event_sources as lambda_event_source,
    aws_events_targets as targets
)
from constructs import Construct

class StockPriceAlertStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # create EventBridge cron job
        event_rule = events.Rule(
            self,
            "ScheduleRule",
            schedule=events.Schedule.cron(minute="30")
        )

        # create SQS queue
        event_queue = sqs.Queue(
            self,
            id="parse_stock_price_event_queue",
            visibility_timeout=Duration.seconds(30)
        )
        
        # add SQS queue to cron job target
        event_rule.add_target(targets.SqsQueue(event_queue))
        
        # create SNS topic
        event_topic = sns.Topic(
            self,
            id="stock_price_alert"
        )

        # create DynamoDB table
        stocks_table = dynamodb.Table(
            self, "stocks",
            partition_key=dynamodb.Attribute(
                name="symbol",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # scrape stock price lambda
        process_event_lambda = _lambda.Function(self, "ScrapeStockPrice",
                                                            runtime = _lambda.Runtime.PYTHON_3_7,
                                                            handler = "ScrapeStockPrice.lambda_handler",
                                                            code = _lambda.Code.from_asset("lambda")
                                                            )
        
        # grant table write access to lambda
        stocks_table.grant_write_data(process_event_lambda)

        # create SQS event source
        sqs_event_source = lambda_event_source.SqsEventSource(event_queue)
        
        # add SQS event source to lambda
        process_event_lambda.add_event_source(sqs_event_source)

        # trigger alert lambda
        trigger_event_lambda = _lambda.Function(self, "ProcessDynamoDBStream",
                                                            runtime = _lambda.Runtime.PYTHON_3_7,
                                                            handler = "ProcessDynamoDBStream.lambda_handler",
                                                            code = _lambda.Code.from_asset("lambda")
                                                            )
        
        # add DynamoDB steam as trigger
        dynamo_stream_event_source = lambda_event_source.DynamoEventSource(stocks_table, 
                                                                            starting_position=_lambda.StartingPosition.TRIM_HORIZON)
        trigger_event_lambda.add_event_source(dynamo_stream_event_source)
        
        # grant table read access to lambda
        stocks_table.grant_read_data(trigger_event_lambda)
        
        




