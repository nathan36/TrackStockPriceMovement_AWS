import boto3

print('Loading function')

def query_dynamodb(stocks:list) -> list:
    '''
    query dynamodb with stock symbol
    :param stocks:
    :return:
    '''

    result = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks')
    for stock in stocks:
        print(stock)
        dic = {}
        response = table.get_item(
            Key={'symbol': stock['symbol']}
        )
        base_price = float(response['Item']['price'])
        price_delta = (float(stock['price']) - base_price)/base_price
        dic['price_delta'] = price_delta
        dic['datetime'] = stock['datetime']
        dic['symbol'] = stock['symbol']
        result.append(dic)
    return result

def publish_message(message):
    '''
    publish message to topic in sns
    :param message:
    :return:
    '''
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

def lambda_handler(event):
    try:
        stream_data = []
        for record in event['Records']:
            dic = {}
            symbol = record['dynamodb']['NewImage']['symbol']
            price = record['dynamodb']['NewImage']['price']
            datetime = record['dynamodb']['NewImage']['datetime']
            dic['symbol'] = list(symbol.values())[0]
            dic['price'] = list(price.values())[0]
            dic['datetime'] = list(datetime.values())[0]
            stream_data.append(dic)
            stocks = query_dynamodb(stream_data)
            message = create_message(0.02, stocks)
            publish_message(message)
        print("Success")
    except Exception as e:
        print(str(e))
        raise e

if __name__ == "__main__":
    import json
    f = open('input.txt')
    event = json.load(f)
    lambda_handler(event)