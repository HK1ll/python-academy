"""Playground example gallery. `python build.py` validates this and writes public/data/examples.json.

Every example must run to completion in the app's harness and print something (tests enforce it).
An example may provide `stdin`: the lines its input() calls will read.
"""

CATEGORIES = ["Basics", "Text & Data", "Files", "Classes", "Security"]

EXAMPLES = [
    {
        "id": "hello-variables",
        "title": "Hello & variables",
        "category": "Basics",
        "description": "Store values in variables and mix them into text with f-strings.",
        "code": '''\
# Variables hold values. An f-string puts them into text.
name = "Ada"
language = "Python"
year = 2026

print(f"Hello, {name}!")
print(f"{language} is fun in {year}.")
print(f"{name!r} has {len(name)} letters")
''',
    },
    {
        "id": "guessing-game",
        "title": "Number guessing game",
        "category": "Basics",
        "description": "A while loop with input(). The answers are in the Input box below the editor.",
        "code": '''\
# The secret is fixed so the example is repeatable.
# Type your own guesses (one per line) in the Input box and run again!
secret = 75
guess = 0
tries = 0

while guess != secret:
    guess = int(input("Guess a number from 1 to 100: "))
    tries += 1
    if guess < secret:
        print("Too low!")
    elif guess > secret:
        print("Too high!")

print(f"You got it in {tries} tries!")
''',
        "stdin": "50\n80\n70\n75",
    },
    {
        "id": "fizzbuzz",
        "title": "FizzBuzz",
        "category": "Basics",
        "description": "The classic loop-and-condition puzzle.",
        "code": '''\
for number in range(1, 21):
    if number % 15 == 0:
        print("FizzBuzz")
    elif number % 3 == 0:
        print("Fizz")
    elif number % 5 == 0:
        print("Buzz")
    else:
        print(number)
''',
    },
    {
        "id": "primes",
        "title": "Prime numbers (sieve)",
        "category": "Basics",
        "description": "Find every prime up to 60 with the Sieve of Eratosthenes.",
        "code": '''\
limit = 60
is_prime = [True] * (limit + 1)
is_prime[0] = is_prime[1] = False

for n in range(2, int(limit ** 0.5) + 1):
    if is_prime[n]:
        for multiple in range(n * n, limit + 1, n):
            is_prime[multiple] = False

primes = [n for n, prime in enumerate(is_prime) if prime]
print(primes)
print(f"{len(primes)} primes up to {limit}")
''',
    },
    {
        "id": "temperature-table",
        "title": "Temperature table",
        "category": "Basics",
        "description": "Loop over a range and format neat columns.",
        "code": '''\
# {value:>6.1f} means: right-align in 6 characters, 1 decimal place
print(" Celsius | Fahrenheit")
print("---------+-----------")
for celsius in range(-10, 41, 10):
    fahrenheit = celsius * 9 / 5 + 32
    print(f"{celsius:>8} | {fahrenheit:>9.1f}")
''',
    },
    {
        "id": "fibonacci",
        "title": "Fibonacci generator",
        "category": "Basics",
        "description": "An endless generator, safely sliced with islice.",
        "code": '''\
from itertools import islice


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


print(list(islice(fibonacci(), 12)))
''',
    },
    {
        "id": "word-count",
        "title": "Word counter",
        "category": "Text & Data",
        "description": "Count words with a Counter and show the most common ones.",
        "code": '''\
from collections import Counter

text = """
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune
"""

words = [word.strip(",.:;'").lower() for word in text.split()]
counts = Counter(words)

for word, count in counts.most_common(5):
    print(f"{word:<10} {count}")
''',
    },
    {
        "id": "json-file",
        "title": "Save and load JSON",
        "category": "Files",
        "description": "Write a dictionary to a file and read it back. Files exist only while the program runs.",
        "code": '''\
import json

settings = {"theme": "dark", "font_size": 14, "recent": ["a.py", "b.py"]}

with open("settings.json", "w") as file:
    json.dump(settings, file, indent=2)

with open("settings.json") as file:
    print(file.read())

with open("settings.json") as file:
    loaded = json.load(file)

print("Round trip identical:", loaded == settings)
''',
    },
    {
        "id": "bank-account",
        "title": "Bank account class",
        "category": "Classes",
        "description": "A class with state, methods and a custom error.",
        "code": '''\
class InsufficientFunds(Exception):
    pass


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds(f"balance is only {self.balance}")
        self.balance -= amount

    def __str__(self):
        return f"{self.owner}: {self.balance}"


account = BankAccount("Ada", 100)
account.deposit(50)
account.withdraw(30)
print(account)

try:
    account.withdraw(500)
except InsufficientFunds as error:
    print("Refused:", error)
''',
    },
    {
        "id": "password-strength",
        "title": "Password strength checker",
        "category": "Security",
        "description": "Score passwords with simple rules and explain what is missing.",
        "code": '''\
import re

COMMON = {"password", "123456", "qwerty", "letmein", "admin"}


def check(password):
    problems = []
    if password.lower() in COMMON:
        return ["is one of the most common passwords"]
    if len(password) < 12:
        problems.append("is shorter than 12 characters")
    if not re.search(r"[a-z]", password):
        problems.append("has no lowercase letter")
    if not re.search(r"[A-Z]", password):
        problems.append("has no uppercase letter")
    if not re.search(r"\\d", password):
        problems.append("has no digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        problems.append("has no symbol")
    return problems


for candidate in ["password", "Tr0ub4dor", "correct-Horse-battery-9"]:
    problems = check(candidate)
    verdict = "OK" if not problems else "weak: " + ", ".join(problems)
    print(f"{candidate!r:28} {verdict}")

# Length matters most. A long passphrase beats a short "clever" password.
''',
    },
    {
        "id": "salted-hash",
        "title": "Salted password hashing",
        "category": "Security",
        "description": "Why the same password gets different hashes, and how to compare them safely.",
        "code": '''\
import hashlib
import hmac
import secrets


def stretch(password, salt, rounds=5000):
    # A teaching model of what PBKDF2 / scrypt / Argon2 do.
    # In real projects use a vetted library, never your own.
    digest = salt + password.encode()
    for _ in range(rounds):
        digest = hashlib.sha256(digest).digest()
    return digest


salt_a, salt_b = secrets.token_bytes(16), secrets.token_bytes(16)
stored = stretch("hunter2", salt_a)

print("same password, different salt -> different hash:", stretch("hunter2", salt_b) != stored)
print("right password accepted:", hmac.compare_digest(stretch("hunter2", salt_a), stored))
print("wrong password rejected:", not hmac.compare_digest(stretch("Hunter2", salt_a), stored))
''',
    },
    {
        "id": "log-scan",
        "title": "Log scanner",
        "category": "Security",
        "description": "Parse failed logins from a log with a regex and flag noisy addresses.",
        "code": '''\
import re
from collections import Counter

LOG = """
10:15:01 Failed password for admin from 203.0.113.5
10:15:04 Failed password for root from 203.0.113.5
10:15:07 Accepted password for ada from 198.51.100.7
10:15:09 Failed password for oracle from 203.0.113.5
10:16:30 Failed password for ada from 198.51.100.7
"""

failures = re.findall(r"Failed password for (\\w+) from ([\\d.]+)", LOG)
per_ip = Counter(ip for user, ip in failures)

for ip, count in per_ip.most_common():
    flag = "  <-- suspicious" if count >= 3 else ""
    print(f"{ip:<15} {count} failures{flag}")
''',
    },
    {
        "id": "caesar",
        "title": "Caesar cipher (a toy)",
        "category": "Security",
        "description": "Encrypt and crack a classic cipher. It shows why home-made crypto is weak.",
        "code": '''\
# A toy cipher for learning. NEVER use it to protect real secrets.
def shift(text, amount):
    result = []
    for char in text:
        if char.isascii() and char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            result.append(chr((ord(char) - base + amount) % 26 + base))
        else:
            result.append(char)
    return "".join(result)


secret = shift("Meet at the old bridge", 3)
print("encrypted:", secret)
print("decrypted:", shift(secret, -3))

# Only 25 possible keys, so an attacker just tries them all:
for key in range(1, 26):
    if "bridge" in shift(secret, -key):
        print("cracked with key", key, "->", shift(secret, -key))
''',
    },
    {
        "id": "ip-check",
        "title": "IP address checker",
        "category": "Security",
        "description": "Classify addresses as private, loopback or public with the ipaddress module.",
        "code": '''\
import ipaddress

for text in ["192.168.1.20", "10.0.0.5", "127.0.0.1", "8.8.8.8", "203.0.113.7", "999.1.1.1"]:
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        print(f"{text:<14} not a valid address")
        continue
    kind = "loopback" if ip.is_loopback else "private" if ip.is_private else "public"
    print(f"{text:<14} {kind}")
''',
    },
    {
        "id": "encoding-demo",
        "title": "Base64, hex and bytes",
        "category": "Security",
        "description": "Encoding is reversible by anyone. It is not encryption.",
        "code": '''\
import base64

message = "admin:secret"
data = message.encode("utf-8")

print("bytes :", data)
print("hex   :", data.hex())
print("base64:", base64.b64encode(data).decode())

# Anyone can undo it, so encoding is not encryption:
print("decoded:", base64.b64decode("YWRtaW46c2VjcmV0").decode())
''',
    },
    {
        "id": "secure-token",
        "title": "Secure random tokens",
        "category": "Security",
        "description": "Use the secrets module (not random) for anything security-related.",
        "code": '''\
import secrets

token = secrets.token_urlsafe(16)
print("token length:", len(token))
print("looks random:", token != secrets.token_urlsafe(16))

print("hex token   :", len(secrets.token_hex(16)), "characters")

# random.random() is predictable. Never use it for tokens, keys or passwords.
''',
    },
]
