import unittest

class Test_ProcessDynamoDBSteam(unittest.TestCase):

    def setUp(self) -> None:
        self.sample = [{'price':176, 'symbol':"GME",
                        'datetime':"2021-10-05T16:00:00-04:00"},
                       {'price':3300, 'symbol':"AMZN",
                        'datetime':"2021-10-05T16:00:00-04:00"}]

    def test_query_dynamodb(self):
        pass

