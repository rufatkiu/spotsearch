from searx import logger
import math

name = "Calculator"
# TODO: translate the following line
description = 'This plugin extends the suggestions with the word "example"'
default_on = True
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
        if type(code) in (int, float):
            search.result_container.answers.clear()
            # TODO: translate the following line
            answer = "The value of {} is {}".format(search.search_query.query, code)
            search.result_container.answers[answer] = {'answer': str(answer)}
    except (ZeroDivisionError, OverflowError, ValueError, FloatingPointError, MemoryError) as e:
        logger.debug(e)
        # TODO: translate the following line
        search.result_container.answers[f'Please recheck the above query: {e}'] = {'answer': None}
        return False
    except (SyntaxError, NameError, TypeError) as e:
        logger.debug(e)
        # TODO: translate the following line
        search.result_container.answers[f'Please recheck syntax of above query'] = {'answer': None}
        return False
    except Exception as e:
        logger.debug(e)
        return False
    return True


check_if_loaded()
