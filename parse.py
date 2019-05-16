# Copyright Robert Geil 2019
import re
import logging

logger = logging.getLogger(__name__)

    
# Regex for various dining halls
reg_covel = re.compile(r"[Cc]ovel")
reg_deneve = re.compile(r"[Dd]e ?[Nn]eve")
reg_bplate = re.compile(r"([Bb] ?[Pp]late)|[Bb]ruin [Pp]late")
reg_feast = re.compile(r"[Ff]east|FEAST")
reg_rende = re.compile(r"[Rr]ende|[Rr]endezvous")
reg_bcafe = re.compile(r"[Bb]caf[eé]|[Bb]ruin [Cc]af[eé]")
reg_1919 = re.compile(r"[Cc]af[eé] 1919")
reg_study = re.compile(r"[Tt]he [Ss]tudy( at [Hh]edrick)?")

saucebot_regex = re.compile(r'![Ss]auce ?[Bb]ot')
hours_regex = re.compile(r'[Ww]hat [Tt]ime|[Hh]ours|[Oo]pen')
list_regex = re.compile(r'[Ll]ist|[Tt]racked|[Tt]racking')
add_regex = re.compile(r'[Aa]dd|[Tt]rack')
remove_regex = re.compile(r'[Rr]emove')
today_regex = re.compile(r'[Mm]enu|[Tt]oday')
info_regex = re.compile(r'[Aa]bout|[Ii]nfo')

def parse_intent(raw):
    matches = saucebot_regex.findall(raw)
    if len(matches) == 0:
        return {'tag': None}
    # Generate the remaining string to be detected
    raw = raw[raw.find(matches[0])+len(matches[0]):]

    # Check for the hours
    if hours_regex.search(raw):
        hall = match_hours(raw)
        if hall is not None:
            return {'tag': 'hours', 'value': hall}

    if list_regex.search(raw):
        return {'tag': 'list'}

    if add_regex.search(raw):
        matches = add_regex.findall(raw)
        substring = raw[raw.find(matches[0])+len(matches[0]):]
        tokens = _tokenize_string(substring)
        return {'tag': 'add', 'value': tokens}

    if remove_regex.search(raw):
        matches = remove_regex.findall(raw)
        substring = raw[raw.find(matches[0])+len(matches[0]):]
        tokens = _tokenize_string(substring)
        return {'tag': 'remove', 'value': tokens}

    if today_regex.search(raw):
        return {'tag': 'today'}

    if info_regex.search(raw):
        return {'tag': 'info'}

    return {'tag': 'unknown'}


def _tokenize_string(string):
    tokens = string.strip('\n\t').split(' ')
    tokens = list(filter(lambda x: x != '', tokens))
    return tokens


def match_hours(msg):
    if reg_covel.search(msg):
        return "Covel"
    if reg_deneve.search(msg):
        return "De Neve"
    if reg_bplate.search(msg):
        return "Bruin Plate"
    if reg_feast.search(msg):
        return "FEAST"
    if reg_rende.search(msg):
        return "Rendezvous"
    if reg_1919.search(msg):
        return "Café 1919"
    if reg_study.search(msg):
        return "The Study at Hedrick"
    if reg_bcafe.search(msg):
        return "Bruin Café"
    return None