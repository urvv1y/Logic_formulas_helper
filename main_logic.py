
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_headers(var_count: int) -> list[str]:
    """Create a list of letters for the table headers."""
    assert var_count > 0 and var_count < 27

    headers = []
    for i in range(var_count):
        headers.append(ALPHABET[i])

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

    return table


def print_table(table: list[list[str]]):
    """Print the table row by row."""
    for row in table:
        print(" | ".join(row))



