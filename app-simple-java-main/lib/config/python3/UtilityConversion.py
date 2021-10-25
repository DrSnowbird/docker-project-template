
import logging

log = logging.getLogger('UtilityConversion')

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isInt(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b
