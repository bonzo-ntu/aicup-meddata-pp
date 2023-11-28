from dateutil import parser
from datetime import datetime
# type list
typeList = ["PATIENT", "DOCTOR", "USERNAME", "PROFESSION", "ROOM", "DEPARTMENT", "HOSPITAL", "ORGANIZATION", "STREET", "CITY", "STATE", "COUNTRY", "ZIP", "LOCATION-OTHER", "AGE", "DATE", "TIME", "DURATION", "SET","PHONE", "FAX", "EMAIL", "URL", "IPADDR", "SSN", "MEDICALRECORD", "HEALTHPLAN", "ACCOUNT", "LICENSE", "VECHICLE", "DEVICE", "BIOID", "IDNUM" ]

input_file_path = "answer.txt"
write_file_path = "answer_out.txt"
    
def convert_date(date_str):
    try:
        # year only
        if len(date_str) == 4:
            return date_str
        else:
            # all date
            date_obj = parser.parse(date_str, dayfirst=True, yearfirst=False)
            return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        try:
            # ignore useless symbol
            date_obj = parser.parse(date_str, dayfirst=True, yearfirst=False, fuzzy=True)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return date_str

def convert_datetime(datetime_str):
    formats = [
        "%d/%m/%Y at %H:%M",
        "%d/%m/%y at %H:%M",
        "%d.%m.%Y at %H:%M",
        "%d.%m.%y at %H:%M",

        "%I:%M%p on %d/%m/%Y",
        "%I:%M%p on %d/%m/%y",
        "%I:%M%p on %d.%m.%Y",
        "%I:%M%p on %d.%m.%y",

        "%I:%M on %d/%m/%Y",
        "%I:%M on %d/%m/%y",
        "%I:%M on %d.%m.%Y",
        "%I:%M on %d.%m.%y",
        
        "%I.%M%p on %d/%m/%Y",
        "%I.%M%p on %d/%m/%y",
        "%I.%M%p on %d.%m.%Y",
        "%I.%M%p on %d.%m.%y",

        "%I.%M on %d/%m/%Y",
        "%I.%M on %d/%m/%y",
        "%I.%M on %d.%m.%Y",
        "%I.%M on %d.%m.%y",
    ]

    for fmt in formats:
        try:
            datetime_obj = datetime.strptime(datetime_str, fmt)
            formatted_date = datetime_obj.strftime("%Y-%m-%d")
            formatted_time = datetime_obj.strftime("%H:%M")
            formatted_datetime = f"{formatted_date}T{formatted_time}"
            return formatted_datetime
        except ValueError:
            pass

    return datetime_str

def convert_duration(duration_str):
    duration_mapping = {
        "yr": "Y",
        "yrs": "Y",
        "year": "Y",
        "years": "Y",
        "month": "M",
        "months": "M",
        "wk": "W",
        "wks": "W",
        "week": "W",
        "weeks": "W",
        "d": "D",
        "ds": "D",
        "day": "D",
        "days": "D",
    }

    duration_parts = duration_str.split()
    if len(duration_parts) == 2:
        num = duration_parts[0]
        unit = duration_parts[1].lower()
        if unit in duration_mapping:
            return f"P{num}{duration_mapping[unit]}"
    
    return duration_str

# read write file
with open(input_file_path, 'r') as input_file, open(write_file_path, 'w') as output_file:
    line = input_file.readline()
    while line:
        # filter useless type
        lineSplit = line.strip().split("\t")
        if lineSplit[1] not in typeList:
            print(line)
        else:
            #  datetime normalization
            if lineSplit[1] == "DATE":
                converted = convert_date(lineSplit[4])
                lineSplit[5] = converted
                output_file.write('\t'.join(lineSplit) + '\n')
            elif lineSplit[1] == "TIME":
                converted = convert_datetime(lineSplit[4])
                lineSplit[5] = converted
                output_file.write('\t'.join(lineSplit) + '\n')
            elif lineSplit[1] == "DURATION":
                converted = convert_duration(lineSplit[4])
                lineSplit[5] = converted
                output_file.write('\t'.join(lineSplit) + '\n')
            else:
                output_file.write(line)
        # next line
        line = input_file.readline()
        

