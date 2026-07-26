
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_headers(var_count: int) -> list[str]:
    """
    Generates a list of headers for a given number of variables.

    Args:
        var_count (int): The number of variables.
    """

    assert var_count > 0 and var_count < 27
    return [ALPHABET[i] for i in range(var_count)]


def fill_the_table(var_count: int) -> list[list[str]]:
    """
    Fills a truth table with boolean values for a given number of variables.

    Args:
        var_count (int): The number of variables.
    """

    table: list[list[str]] = generate_headers(var_count)

    row_count = 2**var_count
    for i in range(row_count):
        certain_row = []

        for j in range(var_count):
            if j == 0:
                value = i % 2
            else:
                value = (i // (2 ** j)) % 2

            certain_row.append(str(value))
        table.append(certain_row)
    return table


for row in fill_the_table(3):
    print(row)
    