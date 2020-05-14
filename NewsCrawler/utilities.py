import unicodedata
import re
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

#function to make date ready for database
def formatdate(date):
    all_small_date = remove_accents(date.lower())
    fulldate = re.search(r'(\d+).(\w+).(\d+)',all_small_date)
    
    if fulldate == None:
        clean_date = " ".join(re.findall(r"[0-9]+.[α-ωΑ-Ω]+\..[0-9]+",all_small_date))
        remove_dot = clean_date.replace(".","")
        fulldate = re.search(r'(\d+).(\w+).(\d+)',remove_dot)

    days = fulldate.group(1)
    month = fulldate.group(2)
    year = fulldate.group(3)

    if re.match(r"ιαν",month) != None: 
        month = "1"
    elif re.match(r"φεβ",month) != None: 
        month = '2'
    elif re.match(r"μαρ",month) != None: 
        month  = '3'
    elif re.match(r"απρ",month) != None: 
        month = '4'
    elif re.match(r"μαι",month) != None: 
        month = '5'
    elif re.match(r"ιουν",month) != None: 
        month = '6'
    elif re.match(r"ιουλ",month) != None: 
        month = '7'
    elif re.match(r"αυγ",month) != None: 
        month = '8'
    elif re.match(r"σεπ",month) != None: 
        month = '9'
    elif re.match(r"οκτ",month) != None: 
        month = '10'
    elif re.match(r"νοε",month) != None: 
        month = '11'
    elif re.match(r"δεκ",month) != None: 
        month = '12'
    return "-".join([year,month,days])