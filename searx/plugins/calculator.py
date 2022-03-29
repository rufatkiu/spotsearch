from searx import logger
import math

name = "Calculator"
description = 'This plugin extends the suggestions with the word "example"'
default_on = False 
logger = logger.getChild("calculator")
ALLOWED_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}

def check_if_loaded():
    logger.debug("initializing calculator plugin")
    
def post_search(request, search):
    if search.search_query.pageno > 1:
        return True
    try:
        code = compile(search.search_query.query, "<string>", "eval")
        for name in code.co_names:
            if name not in ALLOWED_NAMES:
                return False
        code = eval(code, {"__builtins__": {}}, ALLOWED_NAMES)
        if type(code) != str:
            search.result_container.answers.clear()
            search.result_container.answers['Result'] = {'answer': code}
    except Exception:
        return False
    return True


check_if_loaded()