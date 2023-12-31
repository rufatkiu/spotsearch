# SPDX-License-Identifier: AGPL-3.0-or-later
"""
currency convert (DuckDuckGo)
"""

import json

# about
about = {
    "website": "https://duckduckgo.com/",
    "wikidata_id": "Q12805",
    "official_api_documentation": "https://duckduckgo.com/api",
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSONP",
    "description": "Service from DuckDuckGo.",
}

engine_type = "online_currency"
categories = []
base_url = "https://duckduckgo.com/js/spice/currency/1/{0}/{1}"
weight = 100

https_support = True


def request(_query, params):
    params["url"] = base_url.format(params["from"], params["to"])
    return params


def response(resp):
    """remove first and last lines to get only json"""
    json_resp = resp.text[resp.text.find("\n") + 1 : resp.text.rfind("\n") - 2]
    results = []
    try:
        conversion_rate = float(json.loads(json_resp)["conversion"]["converted-amount"])
    except ValueError:
        return results

    url = "https://duckduckgo.com/js/spice/currency/1/{0}/{1}".format(
        resp.search_params["from"].upper(), resp.search_params["to"]
    )

    source_url = "https://www.xe.com/currencyconverter/convert/?Amount=1&From={0}&To={1}".format(
        resp.search_params["from"], resp.search_params["to"]
    )

    results.append(
        {
            "template": "currency.html",
            "amount": resp.search_params["amount"],
            "from": resp.search_params["from"],
            "to": resp.search_params["to"],
            "value": round(resp.search_params["amount"] * conversion_rate, 2),
            "conversion_rate": round(conversion_rate, 2),
            "source_url": source_url,
            "url": url,
            "content": "",
        }
    )
    return results
