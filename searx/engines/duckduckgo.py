# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 DuckDuckGo (Web)
"""

from json import loads
from searx.utils import extract_text, match_language
from searx import logger
import re
import httpx

logger = logger.getChild('ddg engine')
# about
about = {
    "website": 'https://duckduckgo.com/',
    "wikidata_id": 'Q12805',
    "official_api_documentation": 'https://duckduckgo.com/api',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general']
paging = True
supported_languages_url = 'https://duckduckgo.com/util/u172.js'
number_of_results = 10
time_range_support = True
safesearch = True
VQD_REGEX = r"vqd='(\d+-\d+-\d+)'"
language_aliases = {
    'ar-SA': 'ar-XA',
    'es-419': 'es-XL',
    'ja': 'jp-JP',
    'ko': 'kr-KR',
    'sl-SI': 'sl-SL',
    'zh-TW': 'tzh-TW',
    'zh-HK': 'tzh-HK'
}

# search-url
url = 'https://links.duckduckgo.com/d.js?'

url_ping = 'https://duckduckgo.com/t/sl_h'
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm',
                   'year': 'y'}

url_ping = 'https://duckduckgo.com/t/sl_h'
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm',
                   'year': 'y'}

# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    if lang == 'all':
        return None

    lang_code = match_language(lang, lang_list or [], language_aliases, 'wt-WT')
    lang_parts = lang_code.split('-')

    # country code goes first
    return lang_parts[1].lower() + '-' + lang_parts[0].lower()

def get_vqd(query):
    resp = httpx.get(f"https://duckduckgo.com/?q={query}&ia=web")
    resp = re.findall(VQD_REGEX, resp.text)
    return resp[0]

def get_vqd(query):
    resp = httpx.get(f"https://duckduckgo.com/?q={query}&ia=web")
    resp = re.findall(VQD_REGEX, resp.text)
    return resp[0]


def request(query, params):
    if params['time_range'] is not None and params['time_range'] not in time_range_dict:
        return params

    params['method'] = 'GET'

    vqd = get_vqd(query)
    query_dict = {
        "q": query,
        't': 'D',
        'l': params["language"],
        'kl': get_region_code(params["language"]),
        's': (params['pageno'] - 1) * number_of_results,
        'dl': 'en',
        'ct': 'US',
        'ss_mkt': get_region_code(params["language"]),
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
    params["url"] = url
    return params


# get response from search-request
def response(resp):
    if resp.status_code == 303:
        return []

    # parse the response
    results = []

    data = re.findall(r"DDG\.pageLayout\.load\('d',(\[.+\])\);DDG\.duckbar\.load\('images'", str(resp.text))
    search_data = loads(data[0].replace('/\t/g', '    '))

    if len(search_data) == 1 and ('n' not in search_data[0]):
        only_result = search_data[0]
        if ((only_result.get("da") is not None and only_result.get("t") == 'EOF') or
                only_result.get('a') is not None or only_result.get('d') == 'google.com search'):
            return

    for search_result in search_data:
        if 'n' in search_result:
            continue
        results.append({'title': search_result.get("t"),
                        'content': extract_text(search_result.get('a')),
                        'url': search_result.get('u')})
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):

    # response is a js file with regions as an embedded object
    response_page = resp.text
    response_page = response_page[response_page.find('regions:{') + 8:]
    response_page = response_page[:response_page.find('}') + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + '-' + x[:2].upper()), regions_json.keys())

    return list(supported_languages)
