import boto3
import yfinance as yf
from decimal import Decimal
import json

print('Loading function')

def get_input_fromS3(file_fullname) -> list:
    # retrieve input from s3 bucket

    s3 = boto3.resource('s3')
    content_object = s3.Object('stock-ticker-script-bucket', file_fullname)
    file_content = json.load(content_object.get()['Body'])
    tickers_lst = file_content['StockTicker']
    return [ticker.strip() for ticker in tickers_lst]

def get_stock_price(tickers:list) -> list:
    # parse stock price from yahoo finance

    result_list = []
    for ticker in tickers:
        dic = {}
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='1m')
        realtime_data = data[data.index.isin([data.index.max()])]
        close_price = realtime_data.Close
        dic['price'] = round(Decimal(close_price[0]),2)
        dic['datetime'] = close_price.index[0]
        dic['symbol'] = ticker
        result_list.append(dic)

    return result_list

def write_to_dynamodb(stocks:list) -> None:
    # write data to dynamodb

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks')
    for stock in stocks:
        print(stock)
        table.put_item(
            Item={'datetime': stock['datetime'].isoformat(),
                  'price': stock['price'],
                  'symbol': stock['symbol']}
        )

def lambda_handler(event, context):
    try:
        input = get_input_fromS3("input.txt")
        data = get_stock_price(input)
        write_to_dynamodb(data)
        print("Success")
    except Exception as e:
        print(str(e))
        raise e
