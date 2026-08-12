import string

ALPHABET = string.digits + string.ascii_letters
BASE = len(ALPHABET)


def encode_id(number):
    if number == 0:
        return ALPHABET[0]
    digits = []
    while number:
        number, remainder = divmod(number, BASE)
        digits.append(ALPHABET[remainder])
    return ''.join(reversed(digits))


def decode_id(code):
    number = 0
    for char in code:
        if char not in ALPHABET:
            raise ValueError(f'Недопустимый символ короткой ссылки: {char}')
        number = number * BASE + ALPHABET.index(char)
    return number
