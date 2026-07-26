
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"



def generate_headers(var_count: int) -> list[list[str]]:
    """
    Generates a list of headers for a given number of variables.

    Args:
        var_count (int): The number of variables."""

    assert var_count > 0 and var_count < 27

    headers = []

    for i in range(var_count):
        certain_letter = []
        certain_letter.append(ALPHABET[i])
        headers.append(certain_letter)
    return headers

print(generate_headers(5))

    