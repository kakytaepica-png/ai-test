import random
import string

def generate_password(length=12, character_sets=None):
    """Generates a random password with customizable length and character sets.

    Args:
        length: The desired length of the password (default: 12).
        character_sets: A string containing the character sets to use.
                       If None, uses lowercase letters, uppercase letters, digits, and punctuation.

    Returns:
        A string representing the generated password.
    """

    if character_sets is None:
        character_sets = string.ascii_letters + string.digits + string.punctuation

    if length <= 0:
        return ""

    password = ''.join(random.choice(character_sets) for _ in range(length))
    return password

if __name__ == "__main__":
    password = generate_password()
    print(password)
