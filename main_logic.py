
LETTERS = "XYZABCDEFGHIJKLMNOPQRSTUVW"


def generate_headers(var_count: int) -> list[str]:
    """Create a list of letters for the table headers."""
    assert var_count > 0 and var_count < 27

    headers = []
    for i in range(var_count):
        headers.append(LETTERS[i])


    for i in range(var_count):
        headers.append("!" + LETTERS[i])

    # generates variable + NOT of the variables

    return headers


def fill_the_table(var_count: int) -> list[list[str]]:
    """Create a truth table for the given number of variables."""
    table = [generate_headers(var_count)]

    row_count = 2 ** var_count

    for row_index in range(row_count):
        row = []

        for col_index in range(var_count):
            if col_index == 0:
                value = row_index % 2
            else:
                value = (row_index // (2 ** col_index)) % 2

            row.append(str(value))

        table.append(row)

        for col_index in range(var_count):
            original_value = row[col_index]
            negated_value = "1" if original_value == "0" else "0"
            row.append(negated_value)

    return table


def print_table(table: list[list[str]]):
    """Print the table row by row."""
    for row in table:
        print(" | ".join(row))


def expand_table_by_new_variable(table: list[list[str]], new_variable_letter: str) -> list[list[str]]:
    """Expand the existing truth table by adding a new variable column."""
    
    current_var_count = len(table[0])
    next_var_letter = LETTERS[current_var_count]
    
    new_header = table[0] + [new_variable_letter]
    new_table = [new_header]
    
    data_rows = table[1:]
    
    for row in data_rows:
        new_table.append(row + ["0"])
        
    for row in data_rows:
        new_table.append(row + ["1"])
        
    return new_table

def expand_table_by_logical_formula(table: list[list[str]], formula: str) -> list[list[str]]:
    """Add a new column for a logical formula and leave the values empty for now."""
    if not table:
        return [[formula]]

    new_header = table[0] + [formula]
    new_table = [new_header]

    for row in table[1:]:
        new_table.append(row + [""])

    return new_table
