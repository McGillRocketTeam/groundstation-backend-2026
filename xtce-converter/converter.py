import yamcs.pymdb as Y
import requests
import csv

sheet_id = "1Ukaums3NfbJdVOQL7E1QMyPNoQ7gD5Zxciiz4ucRUrk"
gid = "2042306306"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

response = requests.get(url)

if response.status_code == 200:
    with open("data.csv", "wb") as f:
        f.write(response.content)

fc = Y.System("FlightComputer")



with open("data.csv", newline="") as f:
    reader = csv.reader(f)
    next(reader)
    headers = next(reader)
    data = [dict(zip(headers, row)) for row in reader]

param_array = []
bit_pos = 0

for row in data:
    GUI_type = row["GUI Type"]
    kwargs = dict(
        system=fc,
        name=row["Variable Name"],
        short_description=row["UI Name"],
        long_description=row["Description (optional)"],
    )


    match GUI_type:
        case "AbsoluteTime":
            param = Y.AbsoluteTimeParameter(**kwargs, reference=Y.Epoch(""))
            entry = Y.ParameterEntry(param)
            param_array.append(entry)
        case "Binary":
            param = Y.BinaryParameter(**kwargs)
            entry = Y.ParameterEntry(param)
            param_array.append(entry)
        case "Boolean":
            param = Y.BooleanParameter(**kwargs, encoding=Y.IntegerEncoding(bits=1))
            entry = Y.ParameterEntry(param, bitpos=bit_pos)
            bit_pos += 1
            param_array.append(entry)
        case "Enumerated":
            choices = []
            meta = row["Metadata/Notes"]
            enc = row["Encoding"]
            number = int("".join(filter(str.isdigit, enc)))

            if meta:
                for token in meta.splitlines():
                    if "=" in token:
                        k, v = token.split("=", 1)
                        choices.append((int(k.strip()), v.strip()))
            param = Y.EnumeratedParameter(**kwargs, choices=choices, encoding=Y.IntegerEncoding(bits=number))
            entry = Y.ParameterEntry(param, bitpos=bit_pos)
            bit_pos += number
            param_array.append(entry)
        case "Float":
            enc = row["Encoding"]
            number = int("".join(filter(str.isdigit, enc)))
            if "uint" in enc:
                param = Y.FloatParameter(**kwargs, encoding=Y.IntegerEncoding(bits=number))
            elif "float" in enc:
                param = Y.FloatParameter(**kwargs, encoding=Y.FloatEncoding(bits=number))
            entry = Y.ParameterEntry(param, bitpos=bit_pos)
            bit_pos += number
            param_array.append(entry)
        case "Integer":
            enc = row["Encoding"]
            number = int("".join(filter(str.isdigit, enc)))
            scheme =  Y.IntegerEncodingScheme.UNSIGNED if "u" in enc else Y.IntegerEncodingScheme.ONES_COMPLEMENT
            param = Y.FloatParameter(**kwargs, encoding=Y.IntegerEncoding(bits=number, scheme=scheme))

            entry = Y.ParameterEntry(param, bitpos=bit_pos)
            bit_pos += number
            param_array.append(entry)
        case "String":
            param = Y.StringParameter(**kwargs)
            entry = Y.ParameterEntry(param)
            param_array.append(entry)

    # cal = row.get("Calibration Function f(x)", "").strip()
    # if cal:
    #     tokens = cal.split(" ")
    #     operator = tokens[-1]
    #     if len(tokens) != 3:
    #         print("Unsupported function")
    #
    #     else:
    #         match operator:
    #             case "+":
    #                 pass
    #             case "-":
    #                 pass
    #             case "*":
    #                 pass
    #             case "/":
    #                 pass
    #             case _:
    #                 print("Unsupported function")

container = Y.Container(name="cont", system=fc, entries=param_array)

with open("output.xml", "w") as f:
    fc.dump(f, indent = " " * 2)
    print("done")


