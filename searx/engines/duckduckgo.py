# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 DuckDuckGo (Web)
"""

from json import loads
from urllib.parse import urlencode
from searx.utils import match_language, extract_text
import re
from searx.network import get
from lxml.html import fromstring

about = {
    "website": "https://duckduckgo.com/",
    "wikidata_id": "Q12805",
    "official_api_documentation": "https://duckduckgo.com/api",
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
}

send_accept_language_header = True
"""DuckDuckGo-Lite tries to guess user's prefered language from the HTTP
``Accept-Language``.  Optional the user can select a region filter (but not a
language).
"""

# engine dependent config
categories = ["general"]
paging = True
supported_languages_url = "https://duckduckgo.com/util/u172.js"
number_of_results = 10
time_range_support = True
safesearch = True
VQD_REGEX = r"vqd='(\d+-\d+)'"
language_aliases = {
    "ca-ES": "ct-ca",
    "de-AT": "de-de",
    "de-CH": "de-de",
    "es-AR": "es-es",
    "es-CL": "es-es",
    "es-MX": "es-es",
    "fr-BE": "be-fr",
    "fr-CA": "ca-fr",
    "fr-CH": "ch-fr",
    "ar-SA": "ar-XA",
    "es-419": "es-XL",
    "ja": "jp-JP",
    "ko": "kr-KR",
    "sl-SI": "sl-SL",
    "zh-TW": "tzh-TW",
    "zh-HK": "tzh-HK",
}

# search-url
url = "https://links.duckduckgo.com/d.js?"
url_ping = "https://duckduckgo.com/t/sl_h"
time_range_dict = {"day": "d", "week": "w", "month": "m", "year": "y"}


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    if lang == "all":
        return None

    lang_code = match_language(lang, lang_list or [], language_aliases, "wt-WT")
    lang_parts = lang_code.split("-")

    # country code goes first
    return lang_parts[1].lower() + "-" + lang_parts[0].lower()


def get_vqd(query, headers):
    resp = get(f"https://duckduckgo.com/?q={query}&ia=web", headers=headers)
    resp = re.findall(VQD_REGEX, resp.text)
    return resp[0]


def request(query, params):

    params["method"] = "GET"

    vqd = get_vqd(query, params["headers"])
    dl, ct = match_language(params["language"], supported_languages, language_aliases, "wt-WT").split("-")
    query_dict = {
        "q": query,
        "t": "D",
        "l": f"{dl}-{ct}",
        "kl": f"{ct}-{dl}",
        "s": (params["pageno"] - 1) * number_of_results,
        "dl": dl,
        "ct": ct,
        "ss_mkt": get_region_code(params["language"], supported_languages),
        "df": params["time_range"],
        "vqd": vqd,
        "ex": -2,
        "sp": "1",
        "bpa": "1",
        "biaexp": "b",
        "msvrtexp": "b",
    }
    if params["safesearch"] == 2:  # STRICT
        del query_dict["t"]
        query_dict["p"] = 1
        query_dict.update(
            {
                "videxp": "a",
                "nadse": "b",
                "eclsexp": "a",
                "stiaexp": "a",
                "tjsexp": "b",
                "related": "b",
                "msnexp": "a",
            }
        )
    elif params["safesearch"] == 1:  # MODERATE
        query_dict["ex"] = -1
        query_dict.update({"nadse": "b", "eclsexp": "b", "tjsexp": "b"})
    else:  # OFF
        query_dict["ex"] = -2
        query_dict.update({"nadse": "b", "eclsexp": "b", "tjsexp": "b"})

    params["allow_redirects"] = False
    params["data"] = query_dict
    params["cookies"]["kl"] = params["data"]["kl"]
    if params["time_range"] in time_range_dict:
        params["data"]["df"] = time_range_dict[params["time_range"]]
        params["cookies"]["df"] = time_range_dict[params["time_range"]]
    params["url"] = url + urlencode(params["data"])
    return params


def response(resp):
    if resp.status_code == 303:
        return []

    # parse the response
    results = []

    data = re.findall(
        r"DDG\.pageLayout\.load\('d',(\[.+\])\);DDG\.duckbar\.load\('images'",
        str(resp.text),
    )
    try:
        search_data = loads(data[0].replace("/\t/g", "    "))
    except IndexError:
        return

    if len(search_data) == 1 and ("n" not in search_data[0]):
        only_result = search_data[0]
        if (
            (only_result.get("da") is not None and only_result.get("t") == "EOF")
            or only_result.get("a") is not None
            or only_result.get("d") == "google.com search"
        ):
            return

    for search_result in search_data:
        if "n" in search_result:
            continue

        title = extract_text(fromstring(search_result.get("t")))

        content = extract_text(fromstring(search_result.get("a")))

        results.append({"title": title, "content": content, "url": search_result.get("u")})
    return results


def fetch_traits(engine_traits: EngineTraits):
    """Fetch languages & regions from DuckDuckGo.

    # response is a js file with regions as an embedded object
    response_page = resp.text
    response_page = response_page[response_page.find("regions:{") + 8 :]
    response_page = response_page[: response_page.find("}") + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + "-" + x[:2].upper()), regions_json.keys())

    - en_US
    - en_AU
    - en_CA
    - en_GB

    The function :py:obj:`get_ddg_lang` evaluates DuckDuckGo's language from
    SearXNG's locale.

    """
    # pylint: disable=too-many-branches, too-many-statements
    # fetch regions

    engine_traits.all_locale = 'wt-wt'

    # updated from u588 to u661 / should be updated automatically?
    resp = network.get('https://duckduckgo.com/util/u661.js')

    if not resp.ok:
        print("ERROR: response from DuckDuckGo is not OK.")

    pos = resp.text.find('regions:{') + 8
    js_code = resp.text[pos:]
    pos = js_code.find('}') + 1
    regions = json.loads(js_code[:pos])

    for eng_tag, name in regions.items():

        if eng_tag == 'wt-wt':
            engine_traits.all_locale = 'wt-wt'
            continue

        region = ddg_reg_map.get(eng_tag)
        if region == 'skip':
            continue

        if not region:
            eng_territory, eng_lang = eng_tag.split('-')
            region = eng_lang + '_' + eng_territory.upper()

        try:
            sxng_tag = locales.region_tag(babel.Locale.parse(region))
        except babel.UnknownLocaleError:
            print("ERROR: %s (%s) -> %s is unknown by babel" % (name, eng_tag, region))
            continue

        conflict = engine_traits.regions.get(sxng_tag)
        if conflict:
            if conflict != eng_tag:
                print("CONFLICT: babel %s --> %s, %s" % (sxng_tag, conflict, eng_tag))
            continue
        engine_traits.regions[sxng_tag] = eng_tag

    # fetch languages

    engine_traits.custom['lang_region'] = {}

    pos = resp.text.find('languages:{') + 10
    js_code = resp.text[pos:]
    pos = js_code.find('}') + 1
    js_code = '{"' + js_code[1:pos].replace(':', '":').replace(',', ',"')
    languages = json.loads(js_code)

    for eng_lang, name in languages.items():

        if eng_lang == 'wt_WT':
            continue

        babel_tag = ddg_lang_map.get(eng_lang, eng_lang)
        if babel_tag == 'skip':
            continue

        try:

            if babel_tag == 'lang_region':
                sxng_tag = locales.region_tag(babel.Locale.parse(eng_lang))
                engine_traits.custom['lang_region'][sxng_tag] = eng_lang
                continue

            sxng_tag = locales.language_tag(babel.Locale.parse(babel_tag))

        except babel.UnknownLocaleError:
            print("ERROR: language %s (%s) is unknown by babel" % (name, eng_lang))
            continue

        conflict = engine_traits.languages.get(sxng_tag)
        if conflict:
            if conflict != eng_lang:
                print("CONFLICT: babel %s --> %s, %s" % (sxng_tag, conflict, eng_lang))
            continue
        engine_traits.languages[sxng_tag] = eng_lang
