'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

from ism import settings
from django.contrib.auth.models import Group

try:
    DIRECTOR_GROUP_ID = Group.objects.get(name=settings.DIRECTOR_GROUP_NAME)
except:
    g = Group(name=settings.DIRECTOR_GROUP_NAME).save()
    if g: DIRECTOR_GROUP_ID = g.id
    else: DIRECTOR_GROUP_ID = 1

#------------------------------------------------------------------------------
def print_time(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

#------------------------------------------------------------------------------
def print_time_min(date):
    return date.strftime("%Y %b %d - %H:%M")

#------------------------------------------------------------------------------
def print_date(date):
    return date.strftime("%Y-%m-%d")

#------------------------------------------------------------------------------
def limit_text_size(text, max_size):
    if len(text) < max_size:
        return text
    else:
        return text[:(max_size - 3)] + "..."

#------------------------------------------------------------------------------
def print_integer(number, thousand_separator=" "):
    if type(number) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if number < 0:
        return '-' + print_integer(-number)
    result = ''
    while number >= 1000:
        number, r = divmod(number, 1000)
        result = "%s%03d%s" % (thousand_separator, r, result)
    return "%d%s" % (number, result)

#------------------------------------------------------------------------------
def print_float(number, thousand_separator=" ", decimal_separator=","):
    if type(number) != type(0.0):
        raise TypeError("Parameter must be a float.")
    decimal_part = ("%.2f" % abs(number - int(number)))[2:]
    return print_integer(int(number), thousand_separator) + decimal_separator + decimal_part

#------------------------------------------------------------------------------
def isDirector(user):
    try:
        g = user.groups.get(name=settings.DIRECTOR_GROUP_NAME)
        if g:
            return True
        else:
            return False
    except:
        return False

#------------------------------------------------------------------------------
def getAccessColor(accessLvl, colorThresholds):
    for t in colorThresholds:
        if accessLvl <= t.threshold:
            return t.color
    return colorThresholds[0]
