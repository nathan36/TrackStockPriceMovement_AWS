import boto3
import json

print('Loading function')

def get_input_fromS3(file_fullname) -> float:
    '''
    retrieve input from s3 bucket
    :param file_fullname:
    :return:
    '''
    s3 = boto3.resource('s3')
    content_object = s3.Object('stock-ticker-script-bucket', file_fullname)
    file_content = json.load(content_object.get()['Body'])
    return float(file_content['AlartCond'])

def publish_message(message):
    '''
    publish message to topic in sns
    :param message:
    :return:
    '''
    if message != '':
        sns = boto3.client('sns')
        topicArn = 'arn:aws:sns:us-west-2:071144461289:StockPriceAlart'
        response = sns.publish(TopicArn=topicArn,
                               Message=message,
                               Subject='Stock Price Alart')
        message_id = response['MessageId']
        return message_id

def create_message(cond:float, stocks:list) -> str:
    '''
    compile message from stock list based on price delta larger
    then set condition
    :param cond:
    :param stocks:
    :return:
    '''
    payload = ''
    for stock in stocks:
        if abs(stock['price_delta']) >= cond:
            message = '{} has a stock price change of {:.1%} on {} \n'.format(
                stock['symbol'], stock['price_delta'], stock['datetime']
            )
            payload += message
    return  payload

def lambda_handler(event, context):
    try:
        stocks = []
        for record in event['Records']:
            if record['eventName'] != "INSERT":
                dic = {}
                symbol = record['dynamodb']['NewImage']['symbol']
                price = record['dynamodb']['NewImage']['price']
                datetime = record['dynamodb']['NewImage']['datetime']
                base_price = record['dynamodb']['OldImage']['price']

                price = float(list(price.values())[0])
                base_price = float(list(base_price.values())[0])

                dic['symbol'] = list(symbol.values())[0]
                dic['datetime'] = list(datetime.values())[0]
                dic['price_delta'] = (price-base_price)/base_price
                stocks.append(dic)
            cond = get_input_fromS3("input.txt")
            message = create_message(cond, stocks)
            publish_message(message)
        print("Success")
    except Exception as e:
        print(str(e))
        raise e

# for local testing
def lambda_handler1(event):
    try:
        stocks = []
        for record in event['Records']:
            if record['eventName'] != "INSERT":
                dic = {}
                symbol = record['dynamodb']['NewImage']['symbol']
                price = record['dynamodb']['NewImage']['price']
                datetime = record['dynamodb']['NewImage']['datetime']
                base_price = record['dynamodb']['OldImage']['price']

                price = float(list(price.values())[0])
                base_price = float(list(base_price.values())[0])

                dic['symbol'] = list(symbol.values())[0]
                dic['datetime'] = list(datetime.values())[0]
                dic['price_delta'] = (price - base_price) / base_price
                stocks.append(dic)
            cond = get_input_fromS3("input.txt")
            message = create_message(cond, stocks)
            publish_message(message)
        print("Success")
    except Exception as e:
        print(str(e))
        raise e

if __name__ == "__main__":
    import json
    f = open('input.txt')
    event = json.load(f)
    lambda_handler1(event)