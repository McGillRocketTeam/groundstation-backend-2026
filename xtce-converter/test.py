import yamcs.pymdb as Y
import csv

fc = Y.System("FlightComputer")

with open("test.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    # Skip the first row (slop)
    next(reader)

    # Use the second row as the header
    header = next(reader)

    # Read the rest as data
    data = [dict(zip(header, row)) for row in reader]

 #{'Variable Name': 'cc_pressure', 'UI Name': 'Combustion Chamber Pressure', 'Description (optional)': 'Calculated from sensor voltage.', 'Units': 'psi', 'GUI Type': 'Float', 'Encoding': 'uint16_t', 'Calibration Function f(x)': '', 'Metadata/Notes': ''}


for row in data[:5]:
    # print(row)
    match row["GUI Type"]:
        case "AbsoluteTime":
            Y.AbsoluteTimeParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
                reference=Y.Epoch("")
            )
        case "Binary":
            Y.BinaryParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
            )
        case "Boolean":
            Y.BooleanParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
            )
        case "Enumerated":
            Y.EnumeratedParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
                choices=[(0, "PAD"), (1, "FLIGHT")]
            )
        case "Float":
            Y.FloatParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
                encoding=extractEncoding("dsf")
            )
        case "Integer":
            Y.FloatParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
            )
        case "String":
            Y.FloatParameter(
                system=fc,
                name=row["Variable Name"],
                short_description=row["UI Name"],
                long_description=row["Description (optional)"],
            )

# == Output the XTCE ==
print(fc.dumps())
