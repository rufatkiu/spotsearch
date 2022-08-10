# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 DuckDuckGo (Web)
"""

from json import loads
from urllib.parse import urlencode
from searx.utils import match_language, HTMLTextExtractor
from searx import logger
import re
from searx.network import get

logger = logger.getChild('ddg engine')
# about
about = {
    "website": 'https://lite.duckduckgo.com/lite',
    "wikidata_id": 'Q12805',
    "official_api_documentation": 'https://duckduckgo.com/api',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general', 'web']
paging = True
supported_languages_url = 'https://duckduckgo.com/util/u588.js'
time_range_support = True

language_aliases = {
    'ca-ES': 'ct-ca',
    'de-AT': 'de-de',
    'de-CH': 'de-de',
    'es-AR': 'es-es',
    'es-CL': 'es-es',
    'es-MX': 'es-es',
    'fr-BE': 'be-fr',
    'fr-CA': 'ca-fr',
    'fr-CH': 'ch-fr',
    'ar-SA': 'ar-XA',
    'es-419': 'es-XL',
    'ja': 'jp-JP',
    'ko': 'kr-KR',
    'sl-SI': 'sl-SL',
    'zh-TW': 'tzh-TW',
    'zh-HK': 'tzh-HK',
}

time_range_dict = {'day': 'd', 'week': 'w', 'month': 'm', 'year': 'y'}

# search-url
url = 'https://lite.duckduckgo.com/lite'
url_ping = 'https://duckduckgo.com/t/sl_l'


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    if lang == 'all':
        return None

    lang_code = match_language(lang, lang_list or [], language_aliases, 'wt-WT')
    lang_parts = lang_code.split('-')

    # country code goes first
    return lang_parts[1].lower() + '-' + lang_parts[0].lower()


def request(query, params):

    params['url'] = url
    params['method'] = 'POST'

    params['data']['q'] = query

    # The API is not documented, so we do some reverse engineering and emulate
    # what https://lite.duckduckgo.com/lite/ does when you press "next Page"
    # link again and again ..

    vqd = get_vqd(query, params["headers"])
    dl, ct = match_language(params["language"], supported_languages, language_aliases, 'wt-WT').split("-")
    query_dict = {
        "q": query,
        't': 'D',
        'l': f"{dl}-{ct}",
        'kl': f"{ct}-{dl}",
        's': (params['pageno'] - 1) * number_of_results,
        'dl': dl,
        'ct': ct,
        'ss_mkt': get_region_code(params["language"], supported_languages),
        'df': params['time_range'],
        'vqd': vqd,
        'ex': -2,
        'sp': '1',
        'bpa': '1',
        'biaexp': 'b',
        'msvrtexp': 'b'
    }
    if params['safesearch'] == 2:  # STRICT
        del query_dict['t']
        query_dict['p'] = 1
        query_dict.update({
            'videxp': 'a',
            'nadse': 'b',
            'eclsexp': 'a',
            'stiaexp': 'a',
            'tjsexp': 'b',
            'related': 'b',
            'msnexp': 'a'
        })
    elif params['safesearch'] == 1:  # MODERATE
        query_dict['ex'] = -1
        query_dict.update({
            'nadse': 'b',
            'eclsexp': 'b',
            'tjsexp': 'b'
        })
    else:  # OFF
        query_dict['ex'] = -2
        query_dict.update({
            'nadse': 'b',
            'eclsexp': 'b',
            'tjsexp': 'b'
        })

    params['allow_redirects'] = False
    params["data"] = query_dict
    params['cookies']['kl'] = params["data"]["kl"]
    if params['time_range'] in time_range_dict:
        params['data']['df'] = time_range_dict[params['time_range']]
        params['cookies']['df'] = time_range_dict[params['time_range']]
    params["url"] = url + urlencode(params["data"])
    return params


# get response from search-request
def response(resp):

    headers_ping = dict_subset(resp.request.headers, ['User-Agent', 'Accept-Encoding', 'Accept', 'Cookie'])
    get(url_ping, headers=headers_ping)

    if resp.status_code == 303:
        return []

    results = []
    doc = fromstring(resp.text)

    result_table = eval_xpath(doc, '//html/body/form/div[@class="filters"]/table')
    if not len(result_table) >= 3:
        # no more results
        return []
    result_table = result_table[2]

    tr_rows = eval_xpath(result_table, './/tr')

    # In the last <tr> is the form of the 'previous/next page' links
    tr_rows = tr_rows[:-1]

    len_tr_rows = len(tr_rows)
    offset = 0

    while len_tr_rows >= offset + 4:

        # assemble table rows we need to scrap
        tr_title = tr_rows[offset]
        tr_content = tr_rows[offset + 1]
        offset += 4

        # ignore sponsored Adds <tr class="result-sponsored">
        if tr_content.get('class') == 'result-sponsored':
            continue

    if len(search_data) == 1 and ('n' not in search_data[0]):
        only_result = search_data[0]
        if ((only_result.get("da") is not None and only_result.get("t") == 'EOF') or
                only_result.get('a') is not None or only_result.get('d') == 'google.com search'):
            return

        td_content = eval_xpath_getindex(tr_content, './/td[@class="result-snippet"]', 0, None)
        if td_content is None:
            continue

        title = HTMLTextExtractor()
        title.feed(search_result.get('t'))

        content = HTMLTextExtractor()
        content.feed(search_result.get('a'))

        results.append({'title': title.get_text(),
                        'content': content.get_text(),
                        'url': search_result.get('u')})
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):

    # response is a js file with regions as an embedded object
    response_page = resp.text
    response_page = response_page[response_page.find('regions:{') + 8:]
    response_page = response_page[: response_page.find('}') + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + '-' + x[:2].upper()), regions_json.keys())

    return list(supported_languages)
