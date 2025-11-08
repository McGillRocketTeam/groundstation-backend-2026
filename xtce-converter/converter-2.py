from typing import Any, Sequence
import re
import csv
import io
import requests
import yamcs.pymdb as Y


def _fetch_sheet_data(sheet_id: str, gid: str) -> list[list[str]]:
    """
    Internal helper: download and parse a Google Sheet as CSV.

    Returns:
        A list of lists (2D array) representing rows of the sheet.
    """
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    )
    print(f"Fetching sheet data from {url} ...")

    response = requests.get(url)
    response.raise_for_status()
    csv_content = response.content.decode("utf-8")
    reader = csv.reader(io.StringIO(csv_content))
    data = list(reader)

    print(f"Fetched {len(data)} rows (raw) from sheet.")
    return data


def load_sheet_rows(sheet_id: str, gid: str) -> list[dict[str, Any]]:
    """
    Load a Google Sheet (as CSV) into a list of rows (dicts).

    Interprets the sheet with *columns as headers* and each data row as an entry.
    """
    data = _fetch_sheet_data(sheet_id, gid)
    if len(data) < 2:
        raise ValueError("Expected at least two header rows")

    # Your sheet format seems to have a label row then real headers
    headers = data[1]
    rows = [dict(zip(headers, row)) for row in data[2:]]
    print(f"Loaded {len(rows)} data rows.")
    return rows


def load_sheet_columns(sheet_id: str, gid: str) -> dict[str, list[Any]]:
    """
    Load a Google Sheet (as CSV) organized *by columns*.
    """
    data = _fetch_sheet_data(sheet_id, gid)
    if len(data) < 2:
        raise ValueError("Expected header and at least one data row")

    # Skip the *first* row ("Name:", "Parameters:", etc.)
    headers = data[0][1:]  # the real column names start at index 1 (B1..F1)
    rows = [r[1:] for r in data[1:]]  # skip that first column of labels ("Parameters:")

    columns = {h: [] for h in headers if h}

    for row in rows:
        for h, value in zip(headers, row):
            if h:
                columns[h].append(value.strip())

    print(f"Loaded {len(columns)} columns: {', '.join(columns)}")
    return columns


def extract_enum_choices(s: str) -> Sequence[tuple[int, str]]:
    result = []
    for line in s.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue  # Skip blank or malformed lines
        num_str, desc = line.split("=", 1)
        try:
            num = int(num_str.strip())
            result.append((num, desc.strip()))
        except ValueError:
            # Skip lines where the number part isn't a valid integer
            continue
    return result


def extract_number(s: str) -> int | None:
    """
    Extracts the numeric part from a given string (e.g., 'float32' → 32).

    Args:
        s (str): Input string (e.g., 'float32', 'int16', 'uint8').

    Returns:
        int | None: The extracted number as an integer, or None if no digits found.
    """
    match = re.search(r"\d+", s)
    return int(match.group()) if match else None


def make_param(system: Y.System, row: dict[str, Any]) -> Y.Parameter:
    gui_type = str(row["GUI Type"])

    variable_name = str(row["Variable Name"])
    ui_name = str(row["UI Name"])
    description = str(row["Description (optional)"])
    units = str(row["Units"])

    match gui_type:
        case "AbsoluteTime":
            raise NotImplementedError(
                "AbsoluteTime parameters have not been implemented yet."
            )
        case "Binary":
            raise NotImplementedError(
                "Binary parameters have not been implemented yet."
            )
        case "Boolean":
            size = 1
            param = Y.BooleanParameter(
                system=system,
                name=variable_name,
                short_description=ui_name,
                long_description=description,
                units=units,
                encoding=Y.IntegerEncoding(bits=size),
            )
            return param
        case "Enumerated":
            encoded_type = str(row["Encoding"])
            size = extract_number(encoded_type)
            if size == None:
                raise ValueError(
                    f"Input Error: Tried to create enumerated parameter '{variable_name}', but could not find a size in the type '{encoded_type}'"
                )

            enum_metadata = str(row["Metadata/Notes"])
            param = Y.EnumeratedParameter(
                system=system,
                name=variable_name,
                short_description=ui_name,
                long_description=description,
                units=units,
                encoding=Y.IntegerEncoding(bits=size),
                choices=extract_enum_choices(enum_metadata),
            )
            return param
        case "Float":
            encoded_type = str(row["Encoding"])
            size = extract_number(encoded_type)
            if size == None:
                raise ValueError(
                    f"Input Error: Tried to create float parameter '{variable_name}', but could not find a size in the type '{encoded_type}'"
                )

            if "float" in encoded_type:
                param = Y.FloatParameter(
                    system=system,
                    name=variable_name,
                    short_description=ui_name,
                    long_description=description,
                    units=units,
                    encoding=Y.FloatEncoding(bits=size),
                )
                return param
            elif "int" in encoded_type:
                scheme = (
                    Y.IntegerEncodingScheme.UNSIGNED
                    if "u" in encoded_type
                    else Y.IntegerEncodingScheme.TWOS_COMPLEMENT
                )
                param = Y.IntegerParameter(
                    system=system,
                    name=variable_name,
                    short_description=ui_name,
                    long_description=description,
                    units=units,
                    encoding=Y.IntegerEncoding(bits=size, scheme=scheme),
                )
                return param
        case "Integer":
            encoded_type = str(row["Encoding"])
            size = extract_number(encoded_type)
            if size == None:
                raise ValueError(
                    f"Input Error: Tried to create integer parameter '{variable_name}', but could not find a size in the type '{encoded_type}'"
                )
            scheme = (
                Y.IntegerEncodingScheme.UNSIGNED
                if "u" in encoded_type
                else Y.IntegerEncodingScheme.TWOS_COMPLEMENT
            )
            param = Y.IntegerParameter(
                system=system,
                name=variable_name,
                short_description=ui_name,
                long_description=description,
                units=units,
                encoding=Y.IntegerEncoding(bits=size, scheme=scheme),
            )
            return param
        case "String":
            raise NotImplementedError(
                "String parameters have not been implemented yet."
            )

    raise ValueError(f"Unhandled GUI Type '{gui_type}' in make_param().")


def write_system(system: Y.System):
    with open("../src/main/yamcs/mdb/FlightComputer.xml", "w") as f:
        system.dump(f, indent=" " * 2)
        print("done")


def main() -> None:
    sheet_id = "1Ukaums3NfbJdVOQL7E1QMyPNoQ7gD5Zxciiz4ucRUrk"
    parameter_gid = "2042306306"
    atomic_gid = "2140536820"

    param_data = load_sheet_rows(sheet_id, parameter_gid)

    fc = Y.System("FlightComputer")

    param_dict: dict[str, Y.Parameter] = {}

    for row in param_data:
        param = make_param(fc, row)
        param_dict[param.name] = param

    print("Creating Atomics...")
    atomic_data = load_sheet_columns(sheet_id, atomic_gid)

    frame_container = Y.Container(system=fc, name="FCFrame")
    (header_container, atomic_header_params) = make_header(
        system=fc, atomic_names=list(atomic_data.keys())
    )
    frame_container.entries.append(Y.ContainerEntry(header_container))

    atomic_containers = make_atomic_containers(
        system=fc,
        atomic_Data=atomic_data,
        param_dict=param_dict,
        atomic_header_params=atomic_header_params,
    )

    for container_entry in atomic_containers:
        frame_container.entries.append(container_entry)

    write_system(fc)


def make_atomic_containers(
    system: Y.System,
    atomic_Data: dict[str, list[Any]],
    param_dict: dict[str, Y.Parameter],
    atomic_header_params: dict[str, Y.BooleanParameter],
):
    containers: list[Y.ContainerEntry] = []
    for name, param_list in atomic_Data.items():
        condition = Y.EqExpression(ref=atomic_header_params[name], value="True")
        container = Y.Container(
            system=system,
            name=name,
            condition=condition,
        )

        for param_name in param_list:
            if param_name == "":
                break
            param = param_dict[param_name]
            container.entries.append(Y.ParameterEntry(parameter=param, offset=0))

        containers.append(Y.ContainerEntry(container=container, condition=condition))

    return containers


def make_header(system: Y.System, atomic_names: list[str]):
    container = Y.Container(system=system, name="header")
    atomic_params: dict[str, Y.BooleanParameter] = {}

    for name in atomic_names:
        param = Y.BooleanParameter(
            system=system,
            name=f"{name}_flag",
            encoding=Y.IntegerEncoding(bits=1),
        )
        atomic_params[name] = param

    # The following hard-coded header parameters come from
    # the A.S.T.R.A. specification
    #
    # The header looks like:
    # ┌───────────┬────────────┬──────────┬─────────────────────┐
    # │ seq (16b) │ flags (8b) │ pad (8b) │ atomic_bitmap (32b) │
    # └───────────┴────────────┴──────────┴─────────────────────┘
    #                                           ▲        ▲   ▲ ▲
    #                                   padding ┘        │   │ │
    #                                                    │   │ │
    #                                    nth atomic flag ┘   │ │
    #                                             ⋮          │ │
    #                                        2nd atomic flag ┘ │
    #                                          1st atomic flag ┘
    #
    # The atomic bitmap is packed from the right.
    # Which means if there are less than 32 atomics, we will need
    # to extend the padding by the amount 32-(num of atomics)
    seq = Y.IntegerParameter(
        system=system,
        name="seq",
        short_description="Sequence Number",
        long_description="A.S.T.R.A. Packet Identifider",
        signed=False,
        encoding=Y.IntegerEncoding(bits=16),
    )
    container.entries.append(Y.ParameterEntry(seq, offset=0))

    flags = Y.IntegerParameter(
        system=system,
        name="flags",
        short_description="Packet Flags",
        long_description="A.S.T.R.A. Packet Flags",
        signed=False,
        encoding=Y.IntegerEncoding(bits=8),
    )
    container.entries.append(Y.ParameterEntry(flags, offset=0))

    num_empty_atomic_flags = 32 - len(atomic_params)
    padding_size = 8 + num_empty_atomic_flags
    pad = Y.IntegerParameter(
        system=system,
        name="padding",
        short_description="Padding",
        long_description="A.S.T.R.A. Packet Padding",
        signed=False,
        encoding=Y.IntegerEncoding(bits=padding_size),
    )
    container.entries.append(Y.ParameterEntry(pad, offset=0))

    for atomic_flag_parm in reversed(atomic_params.values()):
        entry = Y.ParameterEntry(parameter=atomic_flag_parm, offset=0)
        container.entries.append(entry)

    return (container, atomic_params)


if __name__ == "__main__":
    main()
