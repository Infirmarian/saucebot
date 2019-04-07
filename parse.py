# Copyright Robert Geil 2019
import re
import logging

logger = logging.getLogger(__name__)


def parse_message(msg):
    lower = msg.strip(" \n\t\r").lower()
    temp = lower.find("!sauce bot")
    temp2 = lower.find("!saucebot")
    if temp != -1:
        lower = lower[temp+len("!sauce bot"):].strip(" \n\t\r")
    elif temp2 != -1:
        lower = lower[temp2+len("!saucebot"):].strip(" \n\t\r")
    else:
        return {"tag":None, "value":None} # I wasn't mentioned! :(
    if lower == "info":
        return {"tag":"info", "value":"Hi, I'm Sauce Bot, a totally useless bot originally built "+
        "to track White Sauce Pasta at Covel. I've since grown and you can have me "+
        "check for other food items in the UCLA dining halls as well!\n" +
        "You can get my attention by saying !Sauce Bot and I can do things like "+ 
        "'!Sauce Bot list foods' to get a list of all the items I'm tracking "+
        "or '!Sauce Bot add [food item here]' to give me another item to track"}
    if lower.find("list") != -1:
        return {"tag":"list", "value":None}
    if lower.find("track") != -1:
        item = lower[lower.find("track ")+6:]
        return {"tag":"add", "value":item}
    if lower.find("add") != -1:
        item = lower[lower.find("add ")+4:]
        return {"tag":"add", "value":item}
    if lower.find("remove") != -1:
        item = lower[lower.find("remove ")+7:]
        return {"tag":"remove", "value":item}
    if lower.find("hours") != -1:
        hrs = match_hours(lower)
        if hrs is None:
            return {"tag":"unknown", "value":None}
        else:
            return {"tag":"hours", "value":hrs}
    if lower.find("today") != -1:
        return {"tag":"today", "value":None}
    if lower.find("play despacito") != -1:
        return {"tag":"despacito", "value":None}
    return {"tag":"unknown", "value":None}

    
# Regex for various dining halls
reg_covel = re.compile(r"[Cc]ovel")
reg_deneve = re.compile(r"[Dd]e ?[Nn]eve")
reg_bplate = re.compile(r"([Bb] ?[Pp]late)|[Bb]ruin [Pp]late")
reg_feast = re.compile(r"[Ff]east")
reg_rende = re.compile(r"([Rr]end)|([Rr]endezvous)")
reg_bcafe = re.compile(r"([Bb]caf[eé])|([Bb]ruin [Cc]af[eé])")
reg_1919 = re.compile(r"([Cc]af[eé] 1919)")
reg_study = re.compile(r"([Tt]he [Ss]tudy)")


def match_hours(msg):
    if reg_covel.search(msg):
        return "Covel"
    if reg_deneve.search(msg):
        return "De Neve"
    if reg_bplate.search(msg):
        return "Bruin Plate"
    if reg_feast.search(msg):
        return "FEAST at Rieber"
    if reg_rende.search(msg):
        return "Rendezvous"
    if reg_1919.search(msg):
        return "Café 1919"
    if reg_study.search(msg):
        return "The Study"
    if reg_bcafe.search(msg):
        return "Bruin Café"
    return None