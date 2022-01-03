# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 DuckDuckGo (Web)
"""

from lxml.html import fromstring
from json import loads
from searx.utils import extract_text, match_language, eval_xpath

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
paging = False
supported_languages_url = 'https://duckduckgo.com/util/u172.js'
time_range_support = True
safesearch = True

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
url = 'https://duckduckgo.com/?q={}'
url_ping = 'https://duckduckgo.com/t/sl_h'
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm',
                   'year': 'y'}

# specific xpath variables
result_xpath = '//div[@class="links_main links_deep result__body"]'  # noqa
url_xpath = '//a[@class="result__snippet"]/@href'
title_xpath = '//a[@class="result__a"]'
content_xpath = '//a[@class="result__snippet"]'
correction_xpath = '//a[@id="js-spelling-recourse-link"]'


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    if lang == 'all':
        return None

    lang_code = match_language(lang, lang_list or [], language_aliases, 'wt-WT')
    lang_parts = lang_code.split('-')

    # country code goes first
    return lang_parts[1].lower() + '-' + lang_parts[0].lower()


def request(query, params):
    if params['time_range'] is not None and params['time_range'] not in time_range_dict:
        return params

    params['url'] = url.format(query)
    params['method'] = 'GET'
    params['data']['q'] = query
    params['data']['b'] = ''

    safesearch_ddg_value = None
    if params['safesearch'] == 0:
        safesearch_ddg_value = -2  # OFF
    if params['safesearch'] == 2:
        safesearch_ddg_value = 1  # STRICT

    if safesearch_ddg_value is not None:
        params['cookies']['p'] = str(safesearch_ddg_value)

    region_code = get_region_code(params['language'], supported_languages)
    if region_code:
        params['data']['kl'] = region_code
        params['cookies']['kl'] = region_code

    if params['time_range'] in time_range_dict:
        params['data']['df'] = time_range_dict[params['time_range']]

    params['allow_redirects'] = False
    return params


# get response from search-request
def response(resp):
    if resp.status_code == 303:
        return []

    # parse the response
    results = []

    doc = fromstring(resp.text)

    titles = eval_xpath(doc, title_xpath)
    contents = eval_xpath(doc, content_xpath)
    urls = eval_xpath(doc, url_xpath)

    for title, content, url in zip(titles, contents, urls):
        results.append({'title': extract_text(title),
                        'content': extract_text(content),
                        'url': url})

    # parse correction
    for correction in eval_xpath(doc, correction_xpath):
        # append correction
        results.append({'correction': extract_text(correction)})

    # return results
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
