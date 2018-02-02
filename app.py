# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases

install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

import requests
from bs4 import BeautifulSoup

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)
    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    print(req.get("result").get("action"))
    if req.get("result").get("action") == "covert":
        res = makeWebhookResult(req)
    else:
        return {}
    return res


def makeWebhookResult(data):
    value = data.get['result'].get['parameters'].get['number']
    fro = data.get['result'].get['parameters'].get['Monedas']
    to = data.get['result'].get['parameters'].get['Monedas1']
    speech = convert(fro, to, value)
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


def convert(from_, to_, value_):
    try:
        url = "http://www.xe.com/currencyconverter/convert/?Amount=" + str(value_) + "&From=" + str(
            from_) + "&To=" + str(to_)
        response = requests.get(url)
        page_source = response.content
        source_code = page_source
        soup = BeautifulSoup(source_code, "html.parser")
        res = str(soup.find_all("span", class_="uccResultAmount")[0]).split('>')
        res1 = res[1].split('<')
        return (res1[0] + " " + to_).upper()
    except Exception as e:
        print(e.message)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
