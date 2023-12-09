from dateutil import parser
from datetime import datetime
# type list
typeList = ["PATIENT", "DOCTOR", "USERNAME", "PROFESSION", "ROOM", "DEPARTMENT", "HOSPITAL", "ORGANIZATION", "STREET", "CITY", "STATE", "COUNTRY", "ZIP", "LOCATION-OTHER", "AGE", "DATE", "TIME", "DURATION", "SET","PHONE", "FAX", "EMAIL", "URL", "IPADDR", "SSN", "MEDICALRECORD", "HEALTHPLAN", "ACCOUNT", "LICENSE", "VECHICLE", "DEVICE", "BIOID", "IDNUM" ]

input_file_path = "mj2-neglo-500-ep10_test.out"
write_file_path = "answer.txt"
    
def convert_date(date_str):
    try:
        # year only
        # not completed year
        if "/" in date_str:
            date_parts = date_str.split("/")
            if len(date_parts) < 3:
                return "FAIL"
            for element in date_parts:
                if element == '':
                    return "FAIL"
        elif "." in date_str:
            date_parts = date_str.split(".")
            if len(date_parts) < 3:
                return "FAIL"
            for element in date_parts:
                if element == '':
                    return "FAIL"
        if date_str.count("/") < 2 and date_str.count("-") < 2 and date_str.count(".") < 2:
            return "FAIL"
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

    return "FAIL"

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
    
    return "FAIL"

# read write file
with open(input_file_path, 'r') as input_file, open(write_file_path, 'w') as output_file:
    line = input_file.readline()
    while line:
        # filter useless type
        lineSplit = line.strip().split("\t")

        # filter wrong time related format
        if (lineSplit[1] == "DATE" or lineSplit[1] == "TIME" or lineSplit[1] == "DURATION" or lineSplit[1] == "SET") and (len(lineSplit) < 6): # if time info < 6
            print(line)
        elif lineSplit[1] not in typeList: # if type not exist
            print(line)
        elif lineSplit [1] == "DOCTOR" or lineSplit [1] == "PATIENT" or lineSplit [1] == "STREET" or lineSplit [1] == "STATE":
            if len(lineSplit[4]) < 2:
                print(line)
            else:
                output_file.write(line)
        elif lineSplit [1] == "IDNUM" or lineSplit [1] == "DEPARTMENT":
            if len(lineSplit[4]) < 3:
                print(line)
            else:
                output_file.write(line)
        elif lineSplit [1] == "CITY" or lineSplit [1] == "ZIP":
            if len(lineSplit[4]) < 4:
                print(line)
            else:
                output_file.write(line)
        elif lineSplit [1] == "COUNTRY" or lineSplit [1] == "ORGANIZATION":
            if len(lineSplit[4]) < 5:
                print(line)
            else:
                output_file.write(line)
        elif lineSplit [1] == "MEDICALRECORD":
            if len(lineSplit[4]) < 6:
                print(line)
            else:
                output_file.write(line)
        elif lineSplit [1] == "HOSPITAL":
            if len(lineSplit[4]) < 7:
                print(line)
            else:
                output_file.write(line)   
        else:
            #  datetime normalization
            converted = ""
            if lineSplit[1] == "DATE":
                converted = convert_date(lineSplit[4])
            elif lineSplit[1] == "TIME":
                converted = convert_datetime(lineSplit[4])
                if "T" in lineSplit[5]:
                    converted = "FAIL"
            elif lineSplit[1] == "DURATION":
                converted = convert_duration(lineSplit[4])
            elif lineSplit[1] == "SET":
                converted = "FAIL"

            # if cannot convert
            if converted != "FAIL":
                # change/append the answer
                if len(lineSplit) == 6:
                    lineSplit[5] = converted
            # write
            output_file.write(('\t'.join(lineSplit)).strip() + '\n')

        # next line
        line = input_file.readline()
        

