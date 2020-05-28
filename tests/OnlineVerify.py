import time
import requests
import json
import unittest

class OnlineVerifyTest(unittest.TestCase):
    def testCommunicateWithServer(self):
        url = "https://www.qicai21.ml/autoplay"
        response = requests.get(url)

        self.assertEqual(response.status_code, 200)

    def testCookieExpirated24h(self):
        raise NotImplementedError

    def testWithoutLogonOnlyBuffModeAvailable(self):
        raise NotImplementedError

