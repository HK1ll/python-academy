"""Lesson source. `python build.py` validates this and writes public/data/lessons.json.

Block types: p, h, list, tip, warn, code, output.
Inline markup in text: `code` and **bold** (rendered with DOM nodes, never as HTML).

Exercise checks are Python snippets executed after the learner's program. They can use:
  * every name the learner's program defined
  * _output   - what the program printed
  * _code     - the learner's source
  * run_again(stdin_text) - run the program again with other input, returns what it printed
and signal failure with `assert cond, "friendly message"`.
"""


def p(text):
    return {"type": "p", "text": text}


def h(text):
    return {"type": "h", "text": text}


def items(*entries):
    return {"type": "list", "items": list(entries)}


def tip(text):
    return {"type": "tip", "text": text}


def warn(text):
    return {"type": "warn", "text": text}


def sec(text):
    """A 'Security lens' callout: the defensive takeaway of the current topic."""
    return {"type": "sec", "text": text}


def code(text):
    return {"type": "code", "text": text}


def example(text):
    """Display-only code (no Run button), for things that can't run in the browser."""
    return {"type": "codeonly", "text": text}


def out(text):
    return {"type": "output", "text": text}


LESSONS = [
    # ------------------------------------------------------------------ 1
    {
        "id": "hello-world",
        "title": "Hello, World!",
        "summary": "Write your first program and meet print().",
        "blocks": [
            p("Every programmer starts by making the computer say something. In Python that takes one line."),
            code('print("Hello, World!")'),
            out("Hello, World!"),
            p(
                "`print()` is a **function**: you hand it something inside the parentheses and it "
                "shows it on the screen. Text wrapped in quotes is called a **string**. Single `'` "
                "and double `\"` quotes both work."
            ),
            code(
                """\
print("Learning Python is fun")
print('Single quotes work too')
print("Numbers need no quotes:", 42)"""
            ),
            out(
                """\
Learning Python is fun
Single quotes work too
Numbers need no quotes: 42"""
            ),
            h("Comments"),
            p("Anything after a `#` is a **comment**. Python ignores it, so use comments to leave notes for humans."),
            code(
                """\
# This whole line is a comment
print("Comments are ignored")  # even at the end of a line"""
            ),
            out("Comments are ignored"),
            warn("Python is case-sensitive: `Print` and `print` are different names, and only `print` exists."),
        ],
        "exercise": {
            "prompt": "Print exactly `Hello, Python!` on the screen.",
            "starter": "# Write your code below\n",
            "hint": "Use `print()` with the text inside quotes. Watch the comma, the capital letters and the exclamation mark.",
            "solution": 'print("Hello, Python!")\n',
            "check": """\
got = _output.strip()
assert got == "Hello, Python!", f"Your program printed {got!r}, but we expected 'Hello, Python!'."
""",
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "id": "variables",
        "title": "Variables & Types",
        "summary": "Give values names and learn the basic data types.",
        "blocks": [
            p("A **variable** is a name that points to a value. You create one with `=`."),
            code(
                """\
name = "Ada"
age = 36
print(name)
print(age)"""
            ),
            out(
                """\
Ada
36"""
            ),
            p(
                "Names can contain letters, digits and underscores, but cannot start with a digit. "
                "Python style is `snake_case`, like `total_price`."
            ),
            h("Types"),
            p("Every value has a **type**. Use `type()` to see it."),
            code(
                """\
city = "Paris"      # str    (text)
year = 2024         # int    (whole number)
height = 1.75       # float  (decimal number)
is_open = True      # bool   (True or False)
print(type(city))
print(type(year))
print(type(height))
print(type(is_open))"""
            ),
            out(
                """\
<class 'str'>
<class 'int'>
<class 'float'>
<class 'bool'>"""
            ),
            h("f-strings"),
            p("Put an `f` before the opening quote and write variables inside `{ }` to build text."),
            code(
                """\
name = "Ada"
age = 36
print(f"{name} is {age} years old")"""
            ),
            out("Ada is 36 years old"),
            tip("Variables can be reassigned any time: `age = age + 1` makes `age` one bigger."),
        ],
        "exercise": {
            "prompt": (
                "Create a variable `language` holding the string `\"Python\"` and a variable `year` "
                "holding the integer `1991`. Then use an f-string to print `Python was released in 1991`."
            ),
            "starter": "# Create the variables here\n\n# Print the sentence here\n",
            "hint": 'Write `language = "Python"` and `year = 1991`, then `print(f"{language} was released in {year}")`.',
            "solution": 'language = "Python"\nyear = 1991\nprint(f"{language} was released in {year}")\n',
            "check": """\
assert "language" in globals(), "Create a variable called language."
assert language == "Python", "language should be the string 'Python'."
assert "year" in globals(), "Create a variable called year."
assert year == 1991 and isinstance(year, int), "year should be the whole number 1991 (no quotes)."
got = _output.strip()
assert got == "Python was released in 1991", f"Expected the output 'Python was released in 1991' but got {got!r}."
""",
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "id": "numbers",
        "title": "Numbers & Math",
        "summary": "Use Python as a powerful calculator.",
        "blocks": [
            p("Python understands the usual arithmetic operators, plus a few extras."),
            code(
                """\
print(7 + 3)     # addition
print(7 - 3)     # subtraction
print(7 * 3)     # multiplication
print(7 / 2)     # division (always gives a float)
print(7 // 2)    # floor division (drops the decimals)
print(7 % 2)     # remainder (modulo)
print(2 ** 10)   # power"""
            ),
            out(
                """\
10
4
21
3.5
3
1
1024"""
            ),
            p("Python follows the normal order of operations. Use parentheses to make your intent clear."),
            code(
                """\
print(2 + 3 * 4)
print((2 + 3) * 4)"""
            ),
            out(
                """\
14
20"""
            ),
            h("Handy functions"),
            code(
                """\
print(round(3.14159, 2))
print(abs(-5))
print(int("42") + 1)
print(float("2.5") * 2)"""
            ),
            out(
                """\
3.14
5
43
5.0"""
            ),
            tip("Shortcuts like `score += 5` mean `score = score + 5`. There are also `-=`, `*=` and `/=`."),
            code(
                """\
score = 10
score += 5
print(score)"""
            ),
            out("15"),
        ],
        "exercise": {
            "prompt": (
                "A pizza costs `12.5`. Store that in `price`. Work out `total`: the cost of **4** pizzas "
                "plus a delivery fee of `3`. Print `total`."
            ),
            "starter": "price = \n\n# Calculate total here\n\n# Print it here\n",
            "hint": "`total = price * 4 + 3` — multiplication happens before addition.",
            "solution": "price = 12.5\ntotal = price * 4 + 3\nprint(total)\n",
            "check": """\
assert price == 12.5, "price should be 12.5."
assert total == 53.0, f"total should be 53.0 (4 pizzas plus delivery) but it is {total}."
assert _output.strip() in ("53.0", "53"), f"Print the total: expected 53.0 but the output was {_output.strip()!r}."
""",
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "id": "strings",
        "title": "Working with Strings",
        "summary": "Slice, transform and combine text.",
        "blocks": [
            p("Strings can be joined with `+`, repeated with `*`, and measured with `len()`."),
            code(
                """\
first = "Grace"
last = "Hopper"
full = first + " " + last
print(full)
print(len(full))
print("ha" * 3)"""
            ),
            out(
                """\
Grace Hopper
12
hahaha"""
            ),
            h("Indexing and slicing"),
            p(
                "Each character has a position, starting at **0**. Negative numbers count from the end. "
                "A slice `[start:stop]` includes `start` but stops *before* `stop`."
            ),
            code(
                """\
word = "Python"
print(word[0])
print(word[-1])
print(word[0:2])
print(word[2:])"""
            ),
            out(
                """\
P
n
Py
thon"""
            ),
            h("String methods"),
            code(
                """\
text = "  Hello, World  "
print(text.strip())
print(text.strip().upper())
print(text.strip().replace("World", "Python"))
print("a,b,c".split(","))
print("-".join(["x", "y", "z"]))"""
            ),
            out(
                """\
Hello, World
HELLO, WORLD
Hello, Python
['a', 'b', 'c']
x-y-z"""
            ),
            p("Methods can be **chained**: `text.strip().upper()` strips first, then upper-cases the result."),
            warn("Strings are **immutable**: methods like `upper()` return a new string; they never change the original."),
        ],
        "exercise": {
            "prompt": (
                "`sentence` is given below with messy spaces and lowercase letters. Create `clean` by removing the "
                "spaces around it and capitalising each word (`Python Is Awesome`). Print `clean`."
            ),
            "starter": 'sentence = "  python is awesome  "\n\n# Create clean here\n\n# Print it here\n',
            "hint": "Chain two string methods: `.strip()` removes surrounding spaces and `.title()` capitalises every word.",
            "solution": 'sentence = "  python is awesome  "\nclean = sentence.strip().title()\nprint(clean)\n',
            "check": """\
assert "clean" in globals(), "Create a variable called clean."
assert clean == "Python Is Awesome", f"clean is {clean!r} but should be 'Python Is Awesome'."
assert _output.strip() == "Python Is Awesome", "Print clean so it shows on the screen."
""",
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "id": "conditionals",
        "title": "Making Decisions",
        "summary": "Compare values and choose what runs with if / elif / else.",
        "blocks": [
            p("Comparisons produce **booleans** (`True` or `False`): `==`, `!=`, `<`, `>`, `<=`, `>=`."),
            code(
                """\
print(5 > 3)
print(5 == 6)
print("a" != "b")"""
            ),
            out(
                """\
True
False
True"""
            ),
            p(
                "An `if` statement runs its block only when the condition is true. The block is "
                "**indented** (4 spaces) and the line before it ends with a colon."
            ),
            code(
                """\
temperature = 25

if temperature > 30:
    print("It's hot")
elif temperature > 15:
    print("It's nice")
else:
    print("It's cold")"""
            ),
            out("It's nice"),
            h("Combining conditions"),
            p("Use `and`, `or` and `not` to combine tests."),
            code(
                """\
age = 20
has_ticket = True

if age >= 18 and has_ticket:
    print("Welcome in!")"""
            ),
            out("Welcome in!"),
            warn("`=` **assigns** a value, `==` **compares** two values. Mixing them up is a classic bug."),
            h("Reading input"),
            p(
                "`input()` reads a line typed by the user and returns it as a string. Wrap it in `int()` "
                "to get a number. In this app, type the answers into the **Input** box below the editor."
            ),
        ],
        "exercise": {
            "prompt": (
                "The program reads a score. Print a grade letter: `A` for 90 or more, `B` for 80–89, "
                "`C` for 70–79, otherwise `F`. (Sample input `85` is already in the Input box; the checker "
                "will try several other scores.)"
            ),
            "starter": "score = int(input())\n\n# Print A, B, C or F\n",
            "stdin": "85",
            "hint": "Test from the highest grade down: `if score >= 90:` then `elif score >= 80:` and so on, ending with `else:`.",
            "solution": (
                "score = int(input())\n\n"
                "if score >= 90:\n    print(\"A\")\n"
                "elif score >= 80:\n    print(\"B\")\n"
                "elif score >= 70:\n    print(\"C\")\n"
                "else:\n    print(\"F\")\n"
            ),
            "check": """\
cases = [("95", "A"), ("90", "A"), ("89", "B"), ("85", "B"), ("80", "B"), ("72", "C"), ("70", "C"), ("69", "F"), ("40", "F")]
for score_text, expected in cases:
    got = run_again(score_text).strip()
    assert got == expected, f"For a score of {score_text} we expected {expected!r} but your program printed {got!r}."
""",
        },
    },
    # ------------------------------------------------------------------ 6
    {
        "id": "lists",
        "title": "Lists",
        "summary": "Store and manage collections of items.",
        "blocks": [
            p("A **list** holds many values in order. Create one with square brackets."),
            code(
                """\
fruits = ["apple", "banana", "cherry"]
print(fruits)
print(fruits[0])
print(len(fruits))"""
            ),
            out(
                """\
['apple', 'banana', 'cherry']
apple
3"""
            ),
            h("Changing a list"),
            p("Lists are **mutable**: you can add, replace and remove items."),
            code(
                """\
fruits = ["apple", "banana", "cherry"]
fruits.append("mango")
fruits[1] = "blueberry"
fruits.remove("apple")
print(fruits)"""
            ),
            out("['blueberry', 'cherry', 'mango']"),
            h("Useful helpers"),
            code(
                """\
numbers = [5, 2, 9, 1]
print(sorted(numbers))
print(max(numbers), min(numbers))
print(sum(numbers))
print(9 in numbers)"""
            ),
            out(
                """\
[1, 2, 5, 9]
9 1
17
True"""
            ),
            tip("Slicing works just like strings: `numbers[1:3]` gives the items at positions 1 and 2."),
        ],
        "exercise": {
            "prompt": "Start with `colors = [\"red\", \"green\"]`. Add `\"blue\"` to the end, remove `\"red\"`, then print the list.",
            "starter": 'colors = ["red", "green"]\n\n# Change the list here\n\nprint(colors)\n',
            "hint": "`colors.append(...)` adds to the end and `colors.remove(...)` deletes the first match.",
            "solution": 'colors = ["red", "green"]\ncolors.append("blue")\ncolors.remove("red")\nprint(colors)\n',
            "check": """\
assert colors == ["green", "blue"], f"colors is {colors} but should be ['green', 'blue']."
assert _output.strip() == "['green', 'blue']", "Print the list at the end."
""",
        },
    },
    # ------------------------------------------------------------------ 7
    {
        "id": "loops",
        "title": "Loops",
        "summary": "Repeat work with for and while.",
        "blocks": [
            p("A `for` loop runs its block once for every item in a collection."),
            code(
                """\
for fruit in ["apple", "banana"]:
    print(fruit)

for i in range(3):
    print(i)"""
            ),
            out(
                """\
apple
banana
0
1
2"""
            ),
            p("`range(start, stop, step)` produces numbers; `stop` is not included."),
            code(
                """\
for n in range(2, 11, 4):
    print(n)"""
            ),
            out(
                """\
2
6
10"""
            ),
            h("while loops"),
            p("A `while` loop repeats as long as its condition stays true."),
            code(
                """\
count = 3
while count > 0:
    print(count)
    count -= 1
print("Liftoff!")"""
            ),
            out(
                """\
3
2
1
Liftoff!"""
            ),
            h("break and continue"),
            p("`continue` skips to the next round; `break` leaves the loop entirely."),
            code(
                """\
for n in range(1, 10):
    if n % 2 == 0:
        continue
    if n > 7:
        break
    print(n)"""
            ),
            out(
                """\
1
3
5
7"""
            ),
            warn(
                "A loop whose condition never becomes false runs forever. Don't worry: this app "
                "automatically stops any program that runs longer than 10 seconds."
            ),
        ],
        "exercise": {
            "prompt": (
                "**FizzBuzz**: print the numbers from 1 to 15, one per line. But print `Fizz` for multiples of 3, "
                "`Buzz` for multiples of 5, and `FizzBuzz` for multiples of both."
            ),
            "starter": "for number in range(1, 16):\n    # Decide what to print\n    pass\n",
            "hint": "Test the multiple-of-both case first: `if number % 15 == 0:`, then `elif number % 3 == 0:`, then `elif number % 5 == 0:`, else print the number.",
            "solution": (
                "for number in range(1, 16):\n"
                "    if number % 15 == 0:\n        print(\"FizzBuzz\")\n"
                "    elif number % 3 == 0:\n        print(\"Fizz\")\n"
                "    elif number % 5 == 0:\n        print(\"Buzz\")\n"
                "    else:\n        print(number)\n"
            ),
            "check": """\
expected = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
got = _output.split()
for position, (want, have) in enumerate(zip(expected, got), start=1):
    assert want == have, f"Line {position} should be {want!r} but your program printed {have!r}."
assert len(got) == len(expected), f"Expected {len(expected)} lines of output but got {len(got)}."
""",
        },
    },
    # ------------------------------------------------------------------ 8
    {
        "id": "dictionaries",
        "title": "Dictionaries",
        "summary": "Look things up by key.",
        "blocks": [
            p("A **dictionary** stores **key: value** pairs, like a real dictionary maps a word to its meaning."),
            code(
                """\
person = {"name": "Ada", "age": 36}
print(person["name"])
person["city"] = "London"
print(person)
print(person.get("email", "unknown"))"""
            ),
            out(
                """\
Ada
{'name': 'Ada', 'age': 36, 'city': 'London'}
unknown"""
            ),
            p("`.get(key, default)` is the safe way to look something up: it returns the default instead of an error when the key is missing."),
            h("Looping over a dictionary"),
            code(
                """\
person = {"name": "Ada", "age": 36}
for key, value in person.items():
    print(key, "->", value)
print("age" in person)"""
            ),
            out(
                """\
name -> Ada
age -> 36
True"""
            ),
            h("Example: counting words"),
            code(
                """\
text = "to be or not to be"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)"""
            ),
            out("{'to': 2, 'be': 2, 'or': 1, 'not': 1}"),
            tip("Keys must be unchangeable values such as strings, numbers or tuples. Values can be anything."),
        ],
        "exercise": {
            "prompt": "Build a dictionary `counts` that maps each word in `text` to how many times it appears. Then print how many times `\"the\"` appears.",
            "starter": 'text = "the cat and the hat and the bat"\n\n# Build counts here\n\n# Print how many times "the" appears\n',
            "hint": "Loop over `text.split()` and use `counts[word] = counts.get(word, 0) + 1`.",
            "solution": (
                'text = "the cat and the hat and the bat"\n'
                "counts = {}\n"
                "for word in text.split():\n    counts[word] = counts.get(word, 0) + 1\n"
                'print(counts["the"])\n'
            ),
            "check": """\
expected = {"the": 3, "cat": 1, "and": 2, "hat": 1, "bat": 1}
assert counts == expected, f"counts is {counts} but should be {expected}."
assert _output.strip() == "3", f"Print how many times 'the' appears (3). Your output was {_output.strip()!r}."
""",
        },
    },
    # ------------------------------------------------------------------ 9
    {
        "id": "functions",
        "title": "Functions",
        "summary": "Package code you can reuse.",
        "blocks": [
            p("A **function** is a named, reusable block of code. Define it with `def`, and send a result back with `return`."),
            code(
                """\
def greet(name):
    return f"Hello, {name}!"

message = greet("Ada")
print(message)"""
            ),
            out("Hello, Ada!"),
            h("Default values"),
            code(
                """\
def power(base, exponent=2):
    return base ** exponent

print(power(5))
print(power(2, 10))"""
            ),
            out(
                """\
25
1024"""
            ),
            h("Returning several values"),
            code(
                """\
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([3, 9, 1])
print(low, high)"""
            ),
            out("1 9"),
            warn(
                "`print()` only *shows* a value. `return` *hands it back* so other code can use it. "
                "A function without `return` gives back `None`."
            ),
            tip("Put a short description in triple quotes on the first line of a function (a **docstring**) to document what it does."),
        ],
        "exercise": {
            "prompt": (
                "Write two functions. `is_even(n)` returns `True` when `n` is even and `False` otherwise. "
                "`average(numbers)` returns the mean of a list of numbers."
            ),
            "starter": "def is_even(n):\n    pass\n\n\ndef average(numbers):\n    pass\n",
            "hint": "A number is even when `n % 2 == 0`. The average is `sum(numbers) / len(numbers)`.",
            "solution": (
                "def is_even(n):\n    return n % 2 == 0\n\n\n"
                "def average(numbers):\n    return sum(numbers) / len(numbers)\n"
            ),
            "check": """\
assert is_even(4) is True, "is_even(4) should return True."
assert is_even(7) is False, "is_even(7) should return False."
assert is_even(0) is True, "is_even(0) should return True."
assert average([1, 2, 3, 4]) == 2.5, f"average([1, 2, 3, 4]) should be 2.5 but returned {average([1, 2, 3, 4])!r}."
assert average([10]) == 10, "average([10]) should be 10."
""",
        },
    },
    # ------------------------------------------------------------------ 10
    {
        "id": "comprehensions",
        "title": "Tuples, Sets & Comprehensions",
        "summary": "More collection types and a compact way to build lists.",
        "blocks": [
            p("A **tuple** is like a list that can't be changed. A **set** keeps only unique items."),
            code(
                """\
point = (3, 4)
x, y = point
print(x, y)

unique = set([1, 2, 2, 3, 3, 3])
print(unique)"""
            ),
            out(
                """\
3 4
{1, 2, 3}"""
            ),
            h("List comprehensions"),
            p("A **list comprehension** builds a new list from another collection in a single line: `[expression for item in collection if condition]`."),
            code(
                """\
squares = [n * n for n in range(1, 6)]
print(squares)

evens = [n for n in range(10) if n % 2 == 0]
print(evens)

words = ["hi", "python", "code"]
print([len(w) for w in words])"""
            ),
            out(
                """\
[1, 4, 9, 16, 25]
[0, 2, 4, 6, 8]
[2, 6, 4]"""
            ),
            p("Dictionaries have comprehensions too."),
            code(
                """\
words = ["hi", "python", "code"]
print({w: len(w) for w in words})"""
            ),
            out("{'hi': 2, 'python': 6, 'code': 4}"),
            tip("If a comprehension gets hard to read, use a normal `for` loop. Clear code beats clever code."),
        ],
        "exercise": {
            "prompt": (
                "Using list comprehensions, create `cubes` (the cubes of 1 to 5) and `long_words` (the words from "
                "`words` that have more than 4 letters). Print both lists."
            ),
            "starter": 'words = ["sky", "python", "code", "language", "fun"]\n\n# cubes = ...\n# long_words = ...\n\nprint(cubes)\nprint(long_words)\n',
            "hint": "`[n ** 3 for n in range(1, 6)]` and `[w for w in words if len(w) > 4]`.",
            "solution": (
                'words = ["sky", "python", "code", "language", "fun"]\n'
                "cubes = [n ** 3 for n in range(1, 6)]\n"
                "long_words = [w for w in words if len(w) > 4]\n"
                "print(cubes)\nprint(long_words)\n"
            ),
            "check": """\
assert cubes == [1, 8, 27, 64, 125], f"cubes is {cubes} but should be [1, 8, 27, 64, 125]."
assert long_words == ["python", "language"], f"long_words is {long_words} but should be ['python', 'language']."
""",
        },
    },
    # ------------------------------------------------------------------ 11
    {
        "id": "errors",
        "title": "Handling Errors",
        "summary": "Read error messages and recover gracefully with try/except.",
        "blocks": [
            p(
                "Errors are a normal part of programming. When something goes wrong Python prints a "
                "**traceback**. Read it from the bottom: the last line names the problem, the lines above show where it happened."
            ),
            code("print(10 / 0)"),
            out(
                """\
Traceback (most recent call last):
  File "<your code>", line 1, in <module>
    print(10 / 0)
           ~~~^~~
ZeroDivisionError: division by zero"""
            ),
            h("try / except"),
            p("Wrap risky code in `try`. If it raises the named error, the `except` block runs instead of crashing."),
            code(
                """\
try:
    number = int("abc")
except ValueError:
    print("That's not a number")"""
            ),
            out("That's not a number"),
            h("Raising your own errors"),
            code(
                """\
def divide(a, b):
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b

try:
    divide(1, 0)
except ValueError as error:
    print("Oops:", error)"""
            ),
            out("Oops: b must not be zero"),
            h("Errors you will meet often"),
            items(
                "`SyntaxError` — the code isn't valid Python (missing colon or bracket).",
                "`NameError` — you used a name that doesn't exist (often a typo).",
                "`TypeError` — a value has the wrong type, like `\"a\" + 1`.",
                "`ValueError` — right type, unsuitable value, like `int(\"abc\")`.",
                "`IndexError` / `KeyError` — a list position or dictionary key doesn't exist.",
            ),
            tip("Catch the **specific** error you expect. A bare `except:` hides real bugs."),
        ],
        "exercise": {
            "prompt": (
                "Write `parse_age(text)`. It returns the age as an `int` if `text` is a whole number that isn't negative. "
                "For anything else (`\"abc\"`, `\"\"`, `\"3.5\"`, `\"-5\"`) it returns `None`."
            ),
            "starter": "def parse_age(text):\n    pass\n",
            "hint": "Wrap `int(text)` in `try` / `except ValueError`, then check whether the result is below zero.",
            "solution": (
                "def parse_age(text):\n"
                "    try:\n        age = int(text)\n"
                "    except ValueError:\n        return None\n"
                "    if age < 0:\n        return None\n"
                "    return age\n"
            ),
            "check": """\
assert parse_age("42") == 42, f"parse_age('42') should be 42 but returned {parse_age('42')!r}."
assert parse_age("0") == 0, "parse_age('0') should be 0."
for bad in ["abc", "", "3.5", "-5"]:
    assert parse_age(bad) is None, f"parse_age({bad!r}) should return None but returned {parse_age(bad)!r}."
""",
        },
    },
    # ------------------------------------------------------------------ modules
    {
        "id": "modules",
        "title": "Using Modules",
        "summary": "Import ready-made tools from Python's standard library.",
        "blocks": [
            p(
                "A **module** is a file of ready-made Python code you can reuse. Python ships with a huge "
                "collection of them called the **standard library**: maths, dates, random numbers, JSON and much "
                "more. Use `import` to bring a module in."
            ),
            code(
                """\
import math

print(math.sqrt(16))
print(math.pi)
print(math.ceil(4.2), math.floor(4.8))"""
            ),
            out(
                """\
4.0
3.141592653589793
5 4"""
            ),
            p("After `import math`, everything inside it is reached with a dot: `math.sqrt` means \"the `sqrt` function inside `math`\"."),
            h("Three ways to import"),
            code(
                """\
import math                  # use it as math.factorial(...)
from math import sqrt, pi    # use the names directly
import statistics as stats   # give the module a nickname

print(math.factorial(5))
print(sqrt(25))
print(stats.mean([1, 2, 3, 4]))"""
            ),
            out(
                """\
120
5.0
2.5"""
            ),
            tip(
                "Prefer `import module` or `from module import name`. Avoid `from module import *`: it dumps "
                "every name into your program and makes it hard to tell where things came from."
            ),
            h("Dates"),
            code(
                """\
from datetime import date

launch = date(2024, 3, 15)
print(launch.year)
print(launch.strftime("%d %B %Y"))
print((date(2024, 12, 25) - launch).days)"""
            ),
            out(
                """\
2024
15 March 2024
285"""
            ),
            h("Random numbers"),
            p("`random` gives different results on every run, so this example prints checks that are always true."),
            code(
                """\
import random

dice = random.randint(1, 6)
print(1 <= dice <= 6)

colors = ["red", "green", "blue"]
print(random.choice(colors) in colors)

random.shuffle(colors)
print(sorted(colors))"""
            ),
            out(
                """\
True
True
['blue', 'green', 'red']"""
            ),
            h("Exploring a module"),
            p("`dir(module)` lists every name a module offers, which is handy when you can't remember a function's name."),
            code(
                """\
import math

print("sqrt" in dir(math))
print(type(math))"""
            ),
            out(
                """\
True
<class 'module'>"""
            ),
            warn(
                "Never name your own file after a module you want to use (for example `random.py`): "
                "Python would import your file instead of the real one."
            ),
        ],
        "exercise": {
            "prompt": (
                "Use the `math` module. Write `circle_area(radius)` (area = π × radius²) and "
                "`distance(x1, y1, x2, y2)`, the straight-line distance between two points."
            ),
            "starter": "# Import what you need here\n\n\ndef circle_area(radius):\n    pass\n\n\ndef distance(x1, y1, x2, y2):\n    pass\n",
            "hint": "`math.pi` is π and `math.sqrt(...)` is the square root. The distance is `sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)`.",
            "solution": (
                "import math\n\n\n"
                "def circle_area(radius):\n    return math.pi * radius ** 2\n\n\n"
                "def distance(x1, y1, x2, y2):\n    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)\n"
            ),
            "check": """\
import math as real_math
assert abs(circle_area(1) - real_math.pi) < 1e-9, f"circle_area(1) should be {real_math.pi} but returned {circle_area(1)!r}."
assert abs(circle_area(2) - 12.566370614359172) < 1e-9, f"circle_area(2) should be about 12.566 but returned {circle_area(2)!r}."
assert distance(0, 0, 3, 4) == 5.0, f"distance(0, 0, 3, 4) should be 5.0 but returned {distance(0, 0, 3, 4)!r}."
assert distance(1, 1, 4, 5) == 5.0, f"distance(1, 1, 4, 5) should be 5.0 but returned {distance(1, 1, 4, 5)!r}."
""",
        },
    },
    # ------------------------------------------------------------------ files
    {
        "id": "files",
        "title": "Reading & Writing Files",
        "summary": "Save text to files and read it back.",
        "blocks": [
            p(
                "Programs often need to save or load data. In Python you do that with `open()`. Always open a "
                "file inside a `with` block: it **closes the file for you**, even if an error happens."
            ),
            tip(
                "In this app, files live in a private, temporary folder in your browser's memory. They disappear "
                "when your program ends and never touch your computer's disk. That's why each example creates a "
                "file first and then reads it back."
            ),
            code(
                """\
with open("notes.txt", "w") as file:
    file.write("First line\\n")
    file.write("Second line\\n")

with open("notes.txt") as file:
    text = file.read()

print(repr(text))"""
            ),
            out("'First line\\nSecond line\\n'"),
            p(
                "`\\n` is the invisible **newline** character that ends a line. `file.read()` returns the whole "
                "file as one string, and `repr()` shows the hidden characters."
            ),
            h("File modes"),
            p("The second argument to `open()` says what you want to do:"),
            items(
                "`\"r\"` — **read** (the default). The file must already exist.",
                "`\"w\"` — **write**. Creates the file, or *erases* it if it already exists.",
                "`\"a\"` — **append**. Adds to the end without erasing anything.",
            ),
            code(
                """\
with open("log.txt", "w") as file:
    file.write("start\\n")

with open("log.txt", "a") as file:
    file.write("middle\\n")
    file.write("end\\n")

with open("log.txt") as file:
    for line in file:
        print(line.strip())"""
            ),
            out(
                """\
start
middle
end"""
            ),
            p("Looping over a file gives you one line at a time. `strip()` removes the newline at the end of each."),
            h("Getting a list of lines"),
            code(
                """\
with open("names.txt", "w") as file:
    file.write("Ada\\nGrace\\nLinus\\n")

with open("names.txt") as file:
    names = file.read().splitlines()

print(names)
print(len(names))"""
            ),
            out(
                """\
['Ada', 'Grace', 'Linus']
3"""
            ),
            h("When the file isn't there"),
            p("Opening a file that doesn't exist raises `FileNotFoundError`. You already know how to handle that."),
            code(
                """\
try:
    with open("missing.txt") as file:
        print(file.read())
except FileNotFoundError:
    print("That file does not exist yet")"""
            ),
            out("That file does not exist yet"),
            warn("Opening a file with `\"w\"` wipes out whatever was in it. Use `\"a\"` when you want to add to a file."),
        ],
        "exercise": {
            "prompt": (
                "The file `scores.txt` has one score per line (it's provided below). Read it and store the sum "
                "in `total`. Then write the text `Total: 300` to a new file called `report.txt`."
            ),
            "files": {"scores.txt": "90\n85\n70\n55\n"},
            "starter": '# scores.txt already exists: one number per line\n\n# 1. Read the scores and store their sum in total\n\n# 2. Write "Total: <total>" to report.txt\n',
            "hint": "Use `int(line)` on each line (it ignores the newline) and `sum(...)`. Then `open(\"report.txt\", \"w\")` and `file.write(f\"Total: {total}\")`.",
            "solution": (
                'with open("scores.txt") as file:\n    scores = [int(line) for line in file]\n'
                "total = sum(scores)\n\n"
                'with open("report.txt", "w") as file:\n    file.write(f"Total: {total}\\n")\n'
            ),
            "check": """\
assert "total" in globals(), "Create a variable called total."
assert total == 300, f"total should be 300 but it is {total!r}."
try:
    with open("report.txt") as report_file:
        report = report_file.read()
except FileNotFoundError:
    raise AssertionError("report.txt doesn't exist yet. Create it with open('report.txt', 'w').") from None
assert report.strip() == "Total: 300", f"report.txt should contain 'Total: 300' but contains {report.strip()!r}."
""",
        },
    },
    # ------------------------------------------------------------------ data-files
    {
        "id": "data-files",
        "title": "Saving Data: JSON & CSV",
        "summary": "Store structured data in the two most common file formats.",
        "blocks": [
            p(
                "Text files are fine for simple lists, but real data has structure. **JSON** stores nested "
                "dictionaries and lists. **CSV** stores tables (like a spreadsheet). Python has a module for each."
            ),
            h("JSON"),
            code(
                """\
import json

person = {"name": "Ada", "languages": ["Python", "C"], "age": 36}

text = json.dumps(person)
print(text)
print(json.loads(text)["languages"][0])"""
            ),
            out(
                """\
{"name": "Ada", "languages": ["Python", "C"], "age": 36}
Python"""
            ),
            p("`dumps` turns Python data into a JSON **s**tring, and `loads` turns a string back into Python data. Add `indent=2` to make it easy to read."),
            code(
                """\
import json

print(json.dumps({"name": "Ada", "languages": ["Python", "C"]}, indent=2))"""
            ),
            out(
                """\
{
  "name": "Ada",
  "languages": [
    "Python",
    "C"
  ]
}"""
            ),
            h("JSON and files"),
            p("`json.dump(data, file)` and `json.load(file)` (no **s**) work directly with open files."),
            code(
                """\
import json

settings = {"theme": "dark", "font_size": 14}

with open("settings.json", "w") as file:
    json.dump(settings, file)

with open("settings.json") as file:
    loaded = json.load(file)

print(loaded == settings)
print(loaded["font_size"])"""
            ),
            out(
                """\
True
14"""
            ),
            tip("JSON only understands text, numbers, `True`/`False`/`None`, lists and dictionaries. A tuple comes back as a list, and dictionary keys always come back as strings."),
            h("CSV"),
            code(
                """\
import csv

rows = [["name", "score"], ["Ada", 95], ["Grace", 88]]

with open("scores.csv", "w", newline="") as file:
    csv.writer(file).writerows(rows)

with open("scores.csv", newline="") as file:
    for row in csv.DictReader(file):
        print(row["name"], "scored", row["score"])"""
            ),
            out(
                """\
Ada scored 95
Grace scored 88"""
            ),
            p("`DictReader` uses the first row as column names and gives you each later row as a dictionary. Everything read from a CSV is text, so convert numbers with `int()` or `float()`."),
            warn("Always pass `newline=\"\"` when opening CSV files. Without it you can get blank lines between rows on some systems."),
        ],
        "exercise": {
            "prompt": (
                "`students.json` (provided below) holds a list of students with scores. Load it, then make a list "
                "`passed` of the **names** of students who scored 70 or more, and save that list to a new file "
                "called `passed.json`."
            ),
            "files": {
                "students.json": '[\n  {"name": "Ada", "score": 95},\n  {"name": "Grace", "score": 88},\n  {"name": "Linus", "score": 61}\n]\n'
            },
            "starter": "import json\n\n# 1. Load students.json\n\n# 2. Build the list passed\n\n# 3. Save it to passed.json\n",
            "hint": "`students = json.load(file)`, then `passed = [s[\"name\"] for s in students if s[\"score\"] >= 70]`, then `json.dump(passed, file)` into a file opened with `\"w\"`.",
            "solution": (
                "import json\n\n"
                'with open("students.json") as file:\n    students = json.load(file)\n\n'
                'passed = [s["name"] for s in students if s["score"] >= 70]\n\n'
                'with open("passed.json", "w") as file:\n    json.dump(passed, file)\n'
            ),
            "check": """\
import json as real_json
assert "passed" in globals(), "Create a list called passed."
assert passed == ["Ada", "Grace"], f"passed is {passed} but should be ['Ada', 'Grace']."
try:
    with open("passed.json") as saved_file:
        saved = real_json.load(saved_file)
except FileNotFoundError:
    raise AssertionError("passed.json doesn't exist yet. Save your list with json.dump().") from None
except ValueError:
    raise AssertionError("passed.json doesn't contain valid JSON. Use json.dump(passed, file).") from None
assert saved == ["Ada", "Grace"], f"passed.json contains {saved} but should contain ['Ada', 'Grace']."
""",
        },
    },
    # ------------------------------------------------------------------ own-modules
    {
        "id": "own-modules",
        "title": "Your Own Modules",
        "summary": "Split code into files and import it like any other module.",
        "blocks": [
            p(
                "Any file ending in `.py` is a module. Real programs are split across several files so each one "
                "stays small and focused. To import one, it has to be in the same folder as your program."
            ),
            tip(
                "This app gives you one editor, so the examples **write** the module file first and then import it. "
                "On your own computer you would simply create a second file next to your program."
            ),
            code(
                """\
with open("greetings.py", "w") as file:
    file.write('''
def hello(name):
    return f"Hello, {name}!"

FAVORITE = "Python"
''')

import greetings

print(greetings.hello("Ada"))
print(greetings.FAVORITE)"""
            ),
            out(
                """\
Hello, Ada!
Python"""
            ),
            h("Modules run once"),
            p("The first `import` runs the module's code. Python remembers it, so importing again does nothing."),
            code(
                """\
with open("hello_mod.py", "w") as file:
    file.write('print("loading hello_mod")\\n')

import hello_mod
import hello_mod
print("done")"""
            ),
            out(
                """\
loading hello_mod
done"""
            ),
            h("The __name__ idiom"),
            p(
                "Inside a module, `__name__` is the module's own name when it's imported, but `\"__main__\"` when "
                "the file is run directly. Wrapping code in `if __name__ == \"__main__\":` lets one file work both as a "
                "module and as a program."
            ),
            code(
                """\
with open("calc.py", "w") as file:
    file.write('''
def add(a, b):
    return a + b

if __name__ == "__main__":
    print("calc.py was run directly")
''')

import calc

print(calc.add(2, 3))
print(calc.__name__)"""
            ),
            out(
                """\
5
calc"""
            ),
            p("The line inside the `if` did **not** run, because `calc.py` was imported rather than run directly."),
            tip(
                "Beyond the standard library there are hundreds of thousands of community packages you can add "
                "with `pip install` on your own computer. Importing them works exactly the same way."
            ),
        ],
        "exercise": {
            "prompt": (
                "Create a module file `shapes.py` that defines `square_area(side)` (returns side × side). Then "
                "import it and print `shapes.square_area(5)`."
            ),
            "starter": '''# 1. Write shapes.py: put the module's code between the triple quotes
with open("shapes.py", "w") as file:
    file.write("""
# define square_area here
""")

# 2. Import it and print shapes.square_area(5)
''',
            "hint": "Inside the triple quotes write `def square_area(side):` and `return side * side` (indented). Then `import shapes` and `print(shapes.square_area(5))`.",
            "solution": '''with open("shapes.py", "w") as file:
    file.write("""
def square_area(side):
    return side * side
""")

import shapes

print(shapes.square_area(5))
''',
            "check": """\
assert "shapes" in globals(), "Import your module with: import shapes"
assert hasattr(shapes, "square_area"), "shapes.py must define a function called square_area."
assert shapes.square_area(4) == 16, f"square_area(4) should be 16 but returned {shapes.square_area(4)!r}."
assert _output.strip() == "25", f"Print shapes.square_area(5): expected 25 but the output was {_output.strip()!r}."
""",
        },
    },
    # ------------------------------------------------------------------ 12
    {
        "id": "classes",
        "title": "Classes & Objects",
        "summary": "Bundle data and behaviour together.",
        "blocks": [
            p(
                "A **class** is a blueprint; an **object** is one thing built from it. `__init__` runs when "
                "an object is created, and `self` refers to that particular object."
            ),
            code(
                """\
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says Woof!"

rex = Dog("Rex", 3)
print(rex.name)
print(rex.bark())"""
            ),
            out(
                """\
Rex
Rex says Woof!"""
            ),
            h("Objects remember their state"),
            code(
                """\
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def __str__(self):
        return f"Counter at {self.count}"

c = Counter()
c.increment()
c.increment()
print(c)"""
            ),
            out("Counter at 2"),
            p("`__str__` controls what `print()` shows for your object."),
            h("Inheritance"),
            p("A class can extend another and override its behaviour."),
            code(
                """\
class Animal:
    def speak(self):
        return "..."

class Cat(Animal):
    def speak(self):
        return "Meow"

print(Animal().speak())
print(Cat().speak())"""
            ),
            out(
                """\
...
Meow"""
            ),
            tip(
                "You've covered the core of Python. The next lessons use classes to model real defensive "
                "security tools: login trackers, IP blocklists, detection rules and safe password storage."
            ),
        ],
        "exercise": {
            "prompt": (
                "Create a class `BankAccount`. `BankAccount(owner)` starts with `balance` 0. It has `deposit(amount)` "
                "and `withdraw(amount)`. Withdrawing more than the balance must raise a `ValueError` and leave the balance unchanged."
            ),
            "starter": "class BankAccount:\n    def __init__(self, owner):\n        pass\n",
            "hint": "Store `self.owner` and `self.balance = 0` in `__init__`. In `withdraw`, check `amount > self.balance` first and `raise ValueError(...)`.",
            "solution": (
                "class BankAccount:\n"
                "    def __init__(self, owner):\n        self.owner = owner\n        self.balance = 0\n\n"
                "    def deposit(self, amount):\n        self.balance += amount\n\n"
                "    def withdraw(self, amount):\n"
                "        if amount > self.balance:\n            raise ValueError(\"Insufficient funds\")\n"
                "        self.balance -= amount\n"
            ),
            "check": """\
account = BankAccount("Ada")
assert account.owner == "Ada", "account.owner should be 'Ada'."
assert account.balance == 0, "A new account should start with balance 0."
account.deposit(50)
assert account.balance == 50, "After deposit(50) the balance should be 50."
account.withdraw(20)
assert account.balance == 30, "After withdraw(20) the balance should be 30."
try:
    account.withdraw(100)
except ValueError:
    pass
else:
    raise AssertionError("withdraw(100) should raise ValueError when funds are insufficient.")
assert account.balance == 30, "A failed withdrawal must not change the balance."
""",
        },
    },
    # ------------------------------------------------------------------ class-design
    {
        "id": "class-design",
        "title": "Encapsulation & Properties",
        "summary": "Protect an object's data behind safe, validated methods.",
        "blocks": [
            sec(
                "These lessons use **defensive** security examples: validating input, tracking failed logins, "
                "watching logs and storing passwords safely. They are the tools defenders build, and each one "
                "teaches an object-oriented idea along the way."
            ),
            p(
                "Objects hold two kinds of attributes. **Instance attributes** belong to one object. "
                "**Class attributes** are shared by every object of the class."
            ),
            code(
                """\
class Session:
    timeout_minutes = 15         # class attribute: shared

    def __init__(self, user):
        self.user = user         # instance attribute: one per object
        self.active = True

a = Session("ada")
b = Session("grace")
print(a.timeout_minutes, b.timeout_minutes)

Session.timeout_minutes = 5
print(a.timeout_minutes)"""
            ),
            out(
                """\
15 15
5"""
            ),
            h("Encapsulation"),
            p(
                "**Encapsulation** means keeping an object's internal data behind methods, so it can only change "
                "in safe, controlled ways. By convention a name starting with an underscore, like `_secret`, "
                "means \"internal: don't touch\"."
            ),
            code(
                """\
class Vault:
    def __init__(self, secret, pin):
        self._secret = secret
        self._pin = pin
        self._attempts = 0

    def unlock(self, pin):
        self._attempts += 1
        if pin == self._pin:
            return self._secret
        return None

vault = Vault("launch-code", "4321")
print(vault.unlock("0000"))
print(vault.unlock("4321"))"""
            ),
            out(
                """\
None
launch-code"""
            ),
            warn(
                "An underscore is a **convention**, not a lock: anyone can still read `vault._secret`. "
                "Encapsulation prevents accidents and bugs; it is not secrecy. (And keeping a PIN in plain text "
                "is bad practice. The last lesson fixes that with hashing.)"
            ),
            h("Properties: validation at the door"),
            p(
                "A `@property` looks like a plain attribute from the outside, but runs your code when it is read or "
                "assigned. That lets you reject bad values **every time**, no matter who sets them."
            ),
            code(
                """\
class Server:
    def __init__(self, port):
        self.port = port          # goes through the setter below

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, int) or not 1 <= value <= 65535:
            raise ValueError(f"invalid port: {value!r}")
        self._port = value

server = Server(8080)
print(server.port)
try:
    server.port = 99999
except ValueError as error:
    print("Rejected:", error)"""
            ),
            out(
                """\
8080
Rejected: invalid port: 99999"""
            ),
            sec("**Validate data at the boundary.** If every write passes through one checked door, invalid or hostile input can't sneak in through a forgotten code path."),
            p("A property with no setter is **read-only**. This one exposes a *masked* version of a secret, safe to show in logs."),
            code(
                """\
class Token:
    def __init__(self, value):
        self._value = value

    @property
    def masked(self):
        return "*" * (len(self._value) - 4) + self._value[-4:]

token = Token("abcd1234efgh5678")
print(token.masked)
try:
    token.masked = "hacked"
except AttributeError:
    print("read-only!")"""
            ),
            out(
                """\
************5678
read-only!"""
            ),
            sec(
                "Real systems also slow attackers with rate limiting or growing delays, because a hard lockout "
                "lets an attacker deliberately lock real users out. The exercise below builds the simple lockout idea."
            ),
        ],
        "exercise": {
            "prompt": (
                "Build `LoginTracker(max_failures=3)`. `record_failure(user)` counts a failed login. `is_locked(user)` "
                "is `True` once that user has `max_failures` failures. `reset(user)` clears the count (as after a "
                "successful login). Keep the counts in a **private** attribute. `locked_users` is a **read-only "
                "property** returning a sorted list of locked usernames."
            ),
            "starter": "class LoginTracker:\n    def __init__(self, max_failures=3):\n        pass  # store the limit and the failure counts privately\n\n    # add record_failure, is_locked, reset and the locked_users property\n",
            "hint": "Keep `self._failures = {}` mapping user to count. `is_locked` compares `self._failures.get(user, 0)` with the limit. `reset` can use `self._failures.pop(user, None)`. Decorate `locked_users` with `@property`.",
            "solution": (
                "class LoginTracker:\n"
                "    def __init__(self, max_failures=3):\n        self._max_failures = max_failures\n        self._failures = {}\n\n"
                "    def record_failure(self, user):\n        self._failures[user] = self._failures.get(user, 0) + 1\n\n"
                "    def is_locked(self, user):\n        return self._failures.get(user, 0) >= self._max_failures\n\n"
                "    def reset(self, user):\n        self._failures.pop(user, None)\n\n"
                "    @property\n    def locked_users(self):\n        return sorted(user for user in self._failures if self.is_locked(user))\n"
            ),
            "check": """\
tracker = LoginTracker()
assert tracker.is_locked("ada") is False, "A user with no failures must not be locked."
tracker.record_failure("ada")
tracker.record_failure("ada")
assert tracker.is_locked("ada") is False, "After 2 failures (limit 3) the account should not be locked yet."
tracker.record_failure("ada")
assert tracker.is_locked("ada") is True, "After 3 failures the account should be locked."
assert tracker.is_locked("grace") is False, "Other users must not be affected."
tracker.reset("ada")
assert tracker.is_locked("ada") is False, "reset() should clear the failures."
tracker.reset("nobody")  # must not raise

strict = LoginTracker(max_failures=1)
strict.record_failure("eve")
assert strict.is_locked("eve") is True, "max_failures=1 should lock after a single failure."

many = LoginTracker()
for name in ["bob", "ada", "bob", "ada", "bob", "ada", "zed"]:
    many.record_failure(name)
assert many.locked_users == ["ada", "bob"], f"locked_users should be ['ada', 'bob'] but is {many.locked_users!r}."
try:
    many.locked_users = []
except AttributeError:
    pass
else:
    raise AssertionError("locked_users must be read-only (a property without a setter).")
""",
        },
    },
    # ------------------------------------------------------------------ special-methods
    {
        "id": "special-methods",
        "title": "Special Methods",
        "summary": "Make your objects work with print, ==, len(), in and sets.",
        "blocks": [
            p(
                "Methods with double underscores on both sides, called **dunder** methods, let your objects plug into "
                "Python's built-in features: printing, comparing, `len()`, `in` and more. You never call them "
                "directly; Python calls them for you."
            ),
            h("__str__ and __repr__"),
            code(
                """\
class LogEntry:
    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __repr__(self):
        return f"LogEntry(user={self.user!r}, action={self.action!r})"

    def __str__(self):
        return f"{self.user} did {self.action}"

entry = LogEntry("ada", "login")
print(entry)
print(repr(entry))
print([entry])"""
            ),
            out(
                """\
ada did login
LogEntry(user='ada', action='login')
[LogEntry(user='ada', action='login')]"""
            ),
            p("`__str__` is the friendly text for people. `__repr__` is the precise text for developers, and it's what lists and error messages show."),
            sec(
                "**Never put secrets in `__repr__` or `__str__`.** They end up in logs, tracebacks and debug output. "
                "Show a username, not a password or token."
            ),
            h("Equality and hashing"),
            p(
                "By default two objects are equal only if they are the very same object. Define `__eq__` to compare "
                "by value. If you define `__eq__`, also define `__hash__` (equal objects must hash equally) so the "
                "objects can live in sets and be dictionary keys."
            ),
            code(
                """\
class IPAddress:
    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        return isinstance(other, IPAddress) and self.text == other.text

    def __hash__(self):
        return hash(self.text)

a = IPAddress("10.0.0.1")
b = IPAddress("10.0.0.1")
print(a == b)
print(a is b)

blocked = {a}
print(b in blocked)"""
            ),
            out(
                """\
True
False
True"""
            ),
            h("Behaving like a container"),
            p("`__len__` powers `len()`, `__contains__` powers `in`, and `__iter__` powers `for` loops."),
            code(
                """\
class Blocklist:
    def __init__(self):
        self._ips = set()

    def add(self, ip):
        self._ips.add(ip)

    def __len__(self):
        return len(self._ips)

    def __contains__(self, ip):
        return ip in self._ips

    def __iter__(self):
        return iter(sorted(self._ips))

blocklist = Blocklist()
blocklist.add("6.6.6.6")
blocklist.add("1.2.3.4")
print(len(blocklist))
print("6.6.6.6" in blocklist)
print(list(blocklist))"""
            ),
            out(
                """\
2
True
['1.2.3.4', '6.6.6.6']"""
            ),
            tip("In real projects use the standard library's `ipaddress` module for IP addresses. Building it once yourself shows how the pieces fit together."),
        ],
        "exercise": {
            "prompt": (
                "Write a class `IPv4`. `IPv4(\"192.168.1.10\")` splits the text into four whole-number parts (each 0–255, "
                "**ASCII digits only**) and raises `ValueError` for anything else. `str()` gives the address back and "
                "`repr()` gives `IPv4('192.168.1.10')`. Equal addresses compare equal and hash the same. The read-only "
                "property `is_private` is `True` for `10.x.x.x`, `172.16.x.x`–`172.31.x.x` and `192.168.x.x`."
            ),
            "starter": "class IPv4:\n    def __init__(self, text):\n        pass  # validate and store the four numbers\n\n    # add __str__, __repr__, __eq__, __hash__ and the is_private property\n",
            "hint": "Split with `text.split(\".\")`. Validate each part with `part.isascii() and part.isdigit()` and `0 <= int(part) <= 255` (plain `isdigit()` also accepts digits from other scripts). Store `self.octets = tuple(...)` and base `__eq__` and `__hash__` on it.",
            "solution": (
                "class IPv4:\n"
                "    def __init__(self, text):\n"
                '        parts = text.split(".")\n'
                "        valid = len(parts) == 4 and all(\n"
                "            part.isascii() and part.isdigit() and 0 <= int(part) <= 255 for part in parts\n"
                "        )\n"
                "        if not valid:\n"
                '            raise ValueError(f"invalid IPv4 address: {text!r}")\n'
                "        self.octets = tuple(int(part) for part in parts)\n\n"
                "    def __str__(self):\n"
                '        return ".".join(str(octet) for octet in self.octets)\n\n'
                "    def __repr__(self):\n"
                '        return f"IPv4({str(self)!r})"\n\n'
                "    def __eq__(self, other):\n"
                "        return isinstance(other, IPv4) and self.octets == other.octets\n\n"
                "    def __hash__(self):\n"
                "        return hash(self.octets)\n\n"
                "    @property\n"
                "    def is_private(self):\n"
                "        first, second = self.octets[:2]\n"
                "        return first == 10 or (first == 172 and 16 <= second <= 31) or (first == 192 and second == 168)\n"
            ),
            "check": """\
ip = IPv4("192.168.1.10")
assert str(ip) == "192.168.1.10", f"str(ip) should be '192.168.1.10' but is {str(ip)!r}."
assert repr(ip) == "IPv4('192.168.1.10')", f"repr(ip) should be \\"IPv4('192.168.1.10')\\" but is {repr(ip)!r}."
assert ip == IPv4("192.168.1.10"), "Two IPv4 objects with the same address should be equal."
assert ip != IPv4("192.168.1.11"), "Different addresses must not be equal."
assert len({IPv4("1.2.3.4"), IPv4("1.2.3.4")}) == 1, "Equal addresses must have the same hash so a set keeps only one."
cases = [("10.1.2.3", True), ("172.16.0.1", True), ("172.31.255.255", True), ("172.32.0.1", False),
         ("192.168.0.5", True), ("192.169.0.5", False), ("8.8.8.8", False)]
for text, private in cases:
    assert IPv4(text).is_private == private, f"{text} is_private should be {private}."
bad_inputs = ["1.2.3", "1.2.3.4.5", "256.1.1.1", "a.b.c.d", "1.2.3.-4", "", "1..2.3", " 1.2.3.4",
              "\\u0661\\u0662\\u0663.1.1.1"]
for bad in bad_inputs:
    try:
        IPv4(bad)
    except ValueError:
        continue
    raise AssertionError(f"IPv4({bad!r}) should raise ValueError. (Tip: str.isdigit() also accepts non-ASCII digits; add .isascii().)")
""",
        },
    },
    # ------------------------------------------------------------------ inheritance
    {
        "id": "inheritance",
        "title": "Inheritance & Polymorphism",
        "summary": "Build a family of detection rules that share one interface.",
        "blocks": [
            p(
                "**Inheritance** lets a class reuse and specialise another. The **child** class gets everything the "
                "**parent** has, and can add or override behaviour. `super()` reaches the parent's version of a method."
            ),
            code(
                """\
class Rule:
    def __init__(self, name):
        self.name = name

    def matches(self, event):
        return False

class FailedLoginRule(Rule):
    def __init__(self, limit):
        super().__init__("too many failed logins")
        self.limit = limit

    def matches(self, event):
        return event.get("failed_logins", 0) > self.limit

rule = FailedLoginRule(3)
print(rule.name)
print(rule.matches({"failed_logins": 5}))
print(rule.matches({"failed_logins": 1}))"""
            ),
            out(
                """\
too many failed logins
True
False"""
            ),
            p(
                "`super().__init__(...)` runs the parent's setup, so the child doesn't repeat it. `matches` is "
                "**overridden**: the child's version replaces the parent's."
            ),
            h("Polymorphism"),
            p(
                "**Polymorphism** means different classes respond to the same method call in their own way. The "
                "loop below doesn't care which kind of rule it has; it just calls `matches`."
            ),
            code(
                """\
class Rule:
    def __init__(self, name):
        self.name = name

    def matches(self, event):
        return False

class FailedLoginRule(Rule):
    def __init__(self, limit):
        super().__init__("too many failed logins")
        self.limit = limit

    def matches(self, event):
        return event.get("failed_logins", 0) > self.limit

class CountryRule(Rule):
    def __init__(self, blocked):
        super().__init__("blocked country")
        self.blocked = set(blocked)

    def matches(self, event):
        return event.get("country") in self.blocked

rules = [FailedLoginRule(3), CountryRule(["XX", "YY"])]
event = {"user": "ada", "failed_logins": 7, "country": "XX"}

for rule in rules:
    if rule.matches(event):
        print("ALERT:", rule.name)

print(isinstance(rules[0], Rule))
print(issubclass(CountryRule, FailedLoginRule))"""
            ),
            out(
                """\
ALERT: too many failed logins
ALERT: blocked country
True
False"""
            ),
            p("`isinstance(obj, Class)` is true for the class *and its parents*. `issubclass(A, B)` asks whether `A` inherits from `B`."),
            sec(
                "Detection tools grow by adding **new rule classes**, not by editing one giant `if` chain. New checks "
                "are easy to add and test in isolation, and can't accidentally break the old ones."
            ),
            tip("Use inheritance for **is-a** relationships (a `FailedLoginRule` *is a* `Rule`). For **has-a** relationships, the next lesson covers composition."),
        ],
        "exercise": {
            "prompt": (
                "`Rule` is provided. Write two subclasses. `PortRule(ports)` has the name `\"blocked port\"` and matches when "
                "`event[\"port\"]` is in `ports`. `KeywordRule(words)` has the name `\"suspicious keyword\"` and matches when "
                "any word appears in `event[\"message\"]`, ignoring upper/lower case. Both must cope with events "
                "that are missing those keys."
            ),
            "starter": 'class Rule:\n    def __init__(self, name):\n        self.name = name\n\n    def matches(self, event):\n        return False\n\n\n# Write PortRule and KeywordRule below\n',
            "hint": "Call `super().__init__(\"blocked port\")` in `PortRule.__init__`. Use `event.get(\"port\")` and `event.get(\"message\", \"\")` so missing keys don't crash. For keywords: `any(word in message for word in self.words)` after lower-casing both sides.",
            "solution": (
                "class Rule:\n    def __init__(self, name):\n        self.name = name\n\n    def matches(self, event):\n        return False\n\n\n"
                "class PortRule(Rule):\n"
                '    def __init__(self, ports):\n        super().__init__("blocked port")\n        self.ports = set(ports)\n\n'
                '    def matches(self, event):\n        return event.get("port") in self.ports\n\n\n'
                "class KeywordRule(Rule):\n"
                '    def __init__(self, words):\n        super().__init__("suspicious keyword")\n        self.words = [word.lower() for word in words]\n\n'
                '    def matches(self, event):\n        message = event.get("message", "").lower()\n        return any(word in message for word in self.words)\n'
            ),
            "check": """\
assert issubclass(PortRule, Rule), "PortRule should inherit from Rule."
assert issubclass(KeywordRule, Rule), "KeywordRule should inherit from Rule."
ports = PortRule([23, 3389])
assert ports.name == "blocked port", f"PortRule name should be 'blocked port' but is {ports.name!r} (call super().__init__)."
assert ports.matches({"port": 23}) is True, "Port 23 is in the blocked list."
assert ports.matches({"port": 443}) is False, "Port 443 is not blocked."
assert ports.matches({}) is False, "An event without a port must not match (and must not crash)."
words = KeywordRule(["password", "root"])
assert words.name == "suspicious keyword", f"KeywordRule name should be 'suspicious keyword' but is {words.name!r}."
assert words.matches({"message": "Attempt to login as ROOT"}) is True, "Matching should ignore upper/lower case."
assert words.matches({"message": "hello world"}) is False, "No keyword appears in that message."
assert words.matches({}) is False, "An event without a message must not match (and must not crash)."
""",
        },
    },
    # ------------------------------------------------------------------ abstract-composition
    {
        "id": "abstract-composition",
        "title": "Abstract Classes & Composition",
        "summary": "Define contracts that subclasses must follow, then combine objects into bigger tools.",
        "blocks": [
            p(
                "Sometimes a parent class should only describe **what** children must do, never be used itself. "
                "An **abstract base class** (ABC) is that contract: it can't be instantiated, and children must "
                "implement every `@abstractmethod`."
            ),
            code(
                """\
from abc import ABC, abstractmethod

class Rule(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def matches(self, event):
        \"\"\"Return True when the event should raise an alert.\"\"\"

class Forgetful(Rule):
    pass                              # forgot to write matches()

class BadHour(Rule):
    def matches(self, event):
        return event["hour"] < 6

for cls in (Rule, Forgetful):
    try:
        cls("test")
    except TypeError:
        print(cls.__name__, "is abstract: cannot create it")

rule = BadHour("night login")
print(rule.matches({"hour": 3}))"""
            ),
            out(
                """\
Rule is abstract: cannot create it
Forgetful is abstract: cannot create it
True"""
            ),
            p("Python refuses to create an object whose class still has unimplemented abstract methods, so a forgotten method is caught immediately instead of failing later in production."),
            h("Composition: has-a"),
            p(
                "Inheritance models **is-a**. **Composition** models **has-a**: one object holds other objects and "
                "delegates work to them. It is usually more flexible, because the parts can be swapped freely."
            ),
            code(
                """\
class PortRule:
    def __init__(self, port, action):
        self.port = port
        self.action = action

class Firewall:
    def __init__(self, default="deny"):
        self._rules = []
        self._default = default

    def add(self, rule):
        self._rules.append(rule)

    def decide(self, port):
        for rule in self._rules:
            if rule.port == port:
                return rule.action
        return self._default

firewall = Firewall()
firewall.add(PortRule(443, "allow"))
firewall.add(PortRule(22, "allow"))
print(firewall.decide(443))
print(firewall.decide(23))"""
            ),
            out(
                """\
allow
deny"""
            ),
            sec(
                "**Deny by default.** The firewall only allows what a rule explicitly permits, and blocks everything "
                "else. Forgetting a rule then fails *safe*, whereas allow-by-default fails *open*."
            ),
            tip("A `Firewall` **has** rules; it isn't a kind of rule. When you catch yourself inheriting just to reuse code, ask whether composition fits better."),
        ],
        "exercise": {
            "prompt": (
                "`Rule`, `PortRule` and `KeywordRule` are provided. Build a `Monitor` that **has** rules (composition). "
                "`add_rule(rule)` registers a rule. `process(event)` returns the list of names of every rule that matched "
                "and records `(rule_name, event[\"user\"])` for each. `alerts` is a read-only property returning a "
                "**copy** of the recorded alerts (so outside code can't tamper with the log). `summary()` returns a "
                "dictionary counting alerts per rule name."
            ),
            "starter": (
                "from abc import ABC, abstractmethod\n\n\n"
                "class Rule(ABC):\n    def __init__(self, name):\n        self.name = name\n\n    @abstractmethod\n    def matches(self, event):\n        ...\n\n\n"
                "class PortRule(Rule):\n    def __init__(self, ports):\n        super().__init__(\"blocked port\")\n        self.ports = set(ports)\n\n"
                "    def matches(self, event):\n        return event.get(\"port\") in self.ports\n\n\n"
                "class KeywordRule(Rule):\n    def __init__(self, words):\n        super().__init__(\"suspicious keyword\")\n        self.words = [w.lower() for w in words]\n\n"
                "    def matches(self, event):\n        message = event.get(\"message\", \"\").lower()\n        return any(w in message for w in self.words)\n\n\n"
                "class Monitor:\n    # A Monitor HAS rules; it is not a kind of Rule\n    pass\n"
            ),
            "hint": "Keep `self._rules = []` and `self._alerts = []`. In `process`, loop over the rules, and for each match append the name to a result list and `(rule.name, event[\"user\"])` to `self._alerts`. The `alerts` property should `return list(self._alerts)`.",
            "solution": (
                "from abc import ABC, abstractmethod\n\n\n"
                "class Rule(ABC):\n    def __init__(self, name):\n        self.name = name\n\n    @abstractmethod\n    def matches(self, event):\n        ...\n\n\n"
                "class PortRule(Rule):\n    def __init__(self, ports):\n        super().__init__(\"blocked port\")\n        self.ports = set(ports)\n\n"
                "    def matches(self, event):\n        return event.get(\"port\") in self.ports\n\n\n"
                "class KeywordRule(Rule):\n    def __init__(self, words):\n        super().__init__(\"suspicious keyword\")\n        self.words = [w.lower() for w in words]\n\n"
                "    def matches(self, event):\n        message = event.get(\"message\", \"\").lower()\n        return any(w in message for w in self.words)\n\n\n"
                "class Monitor:\n"
                "    def __init__(self):\n        self._rules = []\n        self._alerts = []\n\n"
                "    def add_rule(self, rule):\n        self._rules.append(rule)\n\n"
                "    def process(self, event):\n"
                "        triggered = []\n"
                "        for rule in self._rules:\n"
                "            if rule.matches(event):\n"
                "                triggered.append(rule.name)\n"
                '                self._alerts.append((rule.name, event["user"]))\n'
                "        return triggered\n\n"
                "    @property\n    def alerts(self):\n        return list(self._alerts)\n\n"
                "    def summary(self):\n"
                "        counts = {}\n"
                "        for name, _ in self._alerts:\n"
                "            counts[name] = counts.get(name, 0) + 1\n"
                "        return counts\n"
            ),
            "check": """\
monitor = Monitor()
monitor.add_rule(PortRule([23]))
monitor.add_rule(KeywordRule(["root"]))
assert monitor.process({"user": "ada", "port": 443, "message": "hi"}) == [], "A harmless event should trigger no rules."
got = monitor.process({"user": "bob", "port": 23, "message": "login as root"})
assert got == ["blocked port", "suspicious keyword"], f"Both rules should match, in the order added. Got {got!r}."
assert monitor.process({"user": "eve", "port": 23, "message": "x"}) == ["blocked port"], "Only the port rule should match here."
expected = [("blocked port", "bob"), ("suspicious keyword", "bob"), ("blocked port", "eve")]
assert monitor.alerts == expected, f"alerts should be {expected!r} but is {monitor.alerts!r}."
monitor.alerts.append(("forged", "nobody"))
assert len(monitor.alerts) == 3, "alerts must return a COPY so callers can't tamper with the real log."
assert monitor.summary() == {"blocked port": 2, "suspicious keyword": 1}, f"summary() is wrong: {monitor.summary()!r}."
try:
    monitor.alerts = []
except AttributeError:
    pass
else:
    raise AssertionError("alerts must be read-only (a property without a setter).")
""",
        },
    },
    # ------------------------------------------------------------------ dataclasses-enums
    {
        "id": "dataclasses-enums",
        "title": "Dataclasses & Enums",
        "summary": "Model data with less code, and make evidence tamper-resistant.",
        "blocks": [
            p(
                "Many classes only exist to hold data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you "
                "from a list of typed fields."
            ),
            code(
                """\
from dataclasses import dataclass

@dataclass
class LogEntry:
    user: str
    ip: str
    success: bool = True

entry = LogEntry("ada", "10.0.0.5")
print(entry)
print(entry == LogEntry("ada", "10.0.0.5"))

entry.success = False
print(entry)"""
            ),
            out(
                """\
LogEntry(user='ada', ip='10.0.0.5', success=True)
True
LogEntry(user='ada', ip='10.0.0.5', success=False)"""
            ),
            p("Fields with a default (`success: bool = True`) must come after fields without one. The type hints document intent; Python itself doesn't enforce them."),
            h("Frozen: records that can't be edited"),
            p("`@dataclass(frozen=True)` makes instances **immutable**. Assigning to a field raises an error, and the object becomes hashable, so it can go in sets."),
            code(
                """\
from dataclasses import dataclass, FrozenInstanceError

@dataclass(frozen=True)
class AuditRecord:
    actor: str
    action: str

record = AuditRecord("ada", "deleted file")
try:
    record.action = "read file"
except FrozenInstanceError:
    print("Audit records cannot be edited")

print(record)
print(len({record, AuditRecord("ada", "deleted file")}))"""
            ),
            out(
                """\
Audit records cannot be edited
AuditRecord(actor='ada', action='deleted file')
1"""
            ),
            sec("**Audit logs and evidence should be append-only and immutable.** If a record can be quietly edited after the fact, it can't be trusted. Freezing the object is the first line of defence."),
            h("Mutable defaults"),
            p("Never share one list between all objects. Use `field(default_factory=list)` so each object gets its own."),
            code(
                """\
from dataclasses import dataclass, field

@dataclass
class Host:
    name: str
    open_ports: list = field(default_factory=list)

web = Host("web")
db = Host("db")
web.open_ports.append(443)
print(web.open_ports, db.open_ports)"""
            ),
            out("[443] []"),
            h("Enums"),
            p(
                "An **Enum** is a fixed set of named values. It replaces \"magic strings\": a typo like `\"admn\"` "
                "silently does the wrong thing, whereas a bad enum lookup fails loudly. `IntEnum` members also compare like numbers."
            ),
            code(
                """\
from enum import Enum, IntEnum

class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Role(Enum):
    VIEWER = "viewer"
    ADMIN = "admin"

print(Severity.HIGH > Severity.LOW)
print(Severity.HIGH.name, Severity.HIGH.value)
print(Severity(2).name)
print(Role.ADMIN)
print(Role("viewer"))

try:
    Role("root")
except ValueError:
    print("Unknown role rejected")"""
            ),
            out(
                """\
True
HIGH 3
MEDIUM
Role.ADMIN
Role.VIEWER
Unknown role rejected"""
            ),
            sec("Converting untrusted text into an enum (`Role(user_input)`) is an easy way to **allow-list** valid values: anything unexpected raises `ValueError` instead of slipping through."),
        ],
        "exercise": {
            "prompt": (
                "Model vulnerability findings. Create an `IntEnum` called `Severity` with `LOW = 1`, `MEDIUM = 2`, `HIGH = 3`. "
                "Create a **frozen** dataclass `Finding` with fields `title` (str) and `severity` (Severity). Then write "
                "`worst(findings)`, which returns the finding with the highest severity, or `None` for an empty list."
            ),
            "starter": "from dataclasses import dataclass\nfrom enum import IntEnum\n\n# 1. Define the Severity enum\n\n# 2. Define the frozen dataclass Finding\n\n# 3. Write worst(findings)\n",
            "hint": "`class Severity(IntEnum):` with three members. `@dataclass(frozen=True)` above `class Finding:`. In `worst`, keep a `highest` variable that starts as `None` and update it whenever `finding.severity > highest.severity`.",
            "solution": (
                "from dataclasses import dataclass\nfrom enum import IntEnum\n\n\n"
                "class Severity(IntEnum):\n    LOW = 1\n    MEDIUM = 2\n    HIGH = 3\n\n\n"
                "@dataclass(frozen=True)\nclass Finding:\n    title: str\n    severity: Severity\n\n\n"
                "def worst(findings):\n"
                "    highest = None\n"
                "    for finding in findings:\n"
                "        if highest is None or finding.severity > highest.severity:\n"
                "            highest = finding\n"
                "    return highest\n"
            ),
            "check": """\
import dataclasses as real_dataclasses
assert [s.name for s in Severity] == ["LOW", "MEDIUM", "HIGH"], "Severity should have LOW, MEDIUM and HIGH, in that order."
assert Severity.LOW == 1 and Severity.MEDIUM == 2 and Severity.HIGH == 3, "LOW, MEDIUM and HIGH should be 1, 2 and 3."
assert Severity.HIGH > Severity.MEDIUM > Severity.LOW, "Severity levels should compare like numbers (use IntEnum)."
assert real_dataclasses.is_dataclass(Finding), "Finding should be a dataclass."
finding = Finding("Open port", Severity.MEDIUM)
assert finding.title == "Open port" and finding.severity is Severity.MEDIUM, "Finding should store title and severity."
assert finding == Finding("Open port", Severity.MEDIUM), "Findings with equal fields should be equal."
try:
    finding.title = "changed"
except real_dataclasses.FrozenInstanceError:
    pass
else:
    raise AssertionError("Finding must be frozen: assigning to a field should raise FrozenInstanceError.")
items = [Finding("Weak cipher", Severity.LOW), Finding("SQL injection", Severity.HIGH), Finding("Open port", Severity.MEDIUM)]
assert worst(items).title == "SQL injection", f"worst() should return the SQL injection finding but returned {worst(items)!r}."
assert worst(items[:1]).title == "Weak cipher", "worst() of a one-item list is that item."
assert worst([]) is None, "worst([]) should return None."
""",
        },
    },
    # ------------------------------------------------------------------ secure-classes
    {
        "id": "secure-classes",
        "title": "Capstone: A Secure User Store",
        "summary": "Hash passwords with salts, compare safely and build a class that never keeps secrets in plain text.",
        "blocks": [
            p(
                "Every breach story ends the same way when passwords were stored in plain text: everyone's "
                "account is instantly exposed. The golden rules are to **never store passwords**, **never invent your own "
                "cryptography** and **compare secrets safely**. This capstone applies everything from the OOP lessons."
            ),
            h("Hashing"),
            p(
                "A **hash function** turns any input into a fixed-size fingerprint. The same input always gives the same "
                "output, a tiny change gives a completely different one, and you can't run it backwards."
            ),
            code(
                """\
import hashlib

print(hashlib.sha256(b"hello").hexdigest())
print(hashlib.sha256(b"Hello").hexdigest()[:16])
print(hashlib.sha256(b"hello").hexdigest() == hashlib.sha256(b"hello").hexdigest())"""
            ),
            out(
                """\
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
185f8db32271fe25
True"""
            ),
            p(
                "So a site can store the hash and compare hashes at login, never the password itself. But a plain, "
                "fast hash is **not enough**: attackers can test billions of guesses per second, and two users with "
                "the same password would get the same hash. The fix is a **salt** (random data unique to each user) plus a "
                "**deliberately slow** hash that repeats the work many thousands of times."
            ),
            h("Salting and stretching (a teaching model)"),
            code(
                """\
import hashlib
import secrets

def stretch(password, salt, rounds=5000):
    digest = salt + password.encode()
    for _ in range(rounds):
        digest = hashlib.sha256(digest).digest()
    return digest

salt_a = secrets.token_bytes(16)
salt_b = secrets.token_bytes(16)

print(len(stretch("hunter2", salt_a)))
print(stretch("hunter2", salt_a) == stretch("hunter2", salt_a))
print(stretch("hunter2", salt_a) == stretch("hunter2", salt_b))"""
            ),
            out(
                """\
32
True
False"""
            ),
            warn(
                "`stretch` is a **teaching model** of what real password hashing does. In real projects never write "
                "your own: use a vetted algorithm such as PBKDF2, scrypt, bcrypt or Argon2, like the example below."
            ),
            example(
                """\
import hashlib
import secrets

salt = secrets.token_bytes(16)
key = hashlib.pbkdf2_hmac("sha256", b"hunter2", salt, 600_000)   # 600,000 rounds
# store the salt and the key, never the password"""
            ),
            p("That example runs on your own computer. (The Python inside this browser has no OpenSSL, so `pbkdf2_hmac` isn't available here, which is why we use the model above. OWASP currently suggests at least 600,000 rounds for PBKDF2-SHA256.)"),
            h("Comparing secrets safely"),
            p(
                "Ordinary `==` on bytes can stop at the first difference, so how long it takes can leak how close a guess was "
                "(a **timing attack**). `hmac.compare_digest` takes the same time either way."
            ),
            code(
                """\
import hmac

print(hmac.compare_digest(b"secret", b"secret"))
print(hmac.compare_digest(b"secret", b"secreT"))"""
            ),
            out(
                """\
True
False"""
            ),
            h("Random secrets"),
            code(
                """\
import secrets

token = secrets.token_hex(16)
print(len(token))
print(token == secrets.token_hex(16))"""
            ),
            out(
                """\
32
False"""
            ),
            sec("Use the `secrets` module for tokens, salts and keys. The `random` module is **predictable** and must never be used for anything security-related."),
            h("Custom exceptions"),
            p("Your own exception classes make failures explicit and easy to handle. Inherit from `Exception`."),
            code(
                """\
class AccessDenied(Exception):
    pass

def delete_user(actor_role, target):
    if actor_role != "admin":
        raise AccessDenied(f"role {actor_role!r} may not delete users")
    return f"deleted {target}"

try:
    delete_user("viewer", "bob")
except AccessDenied as error:
    print("Denied:", error)

print(delete_user("admin", "bob"))"""
            ),
            out(
                """\
Denied: role 'viewer' may not delete users
deleted bob"""
            ),
            sec("Checking **who is allowed to do what** before acting is called *access control*. Keep the check inside the class that owns the data, so no code path can skip it."),
        ],
        "exercise": {
            "prompt": (
                "Finish the `User` class. `User(name, password)` stores `name`, a random 16-byte `salt` and the "
                "`password_hash`, and **never the password itself**. `check_password(candidate)` returns `True`/`False`, "
                "comparing with `hmac.compare_digest`. `change_password(old, new)` raises `AuthenticationError` if `old` is "
                "wrong, raises `ValueError` if `new` is shorter than 8 characters, and otherwise stores a fresh salt and hash. "
                "`repr()` must show only the name. (The helper uses just 1,000 rounds so this runs instantly; real systems "
                "use far more, with a proper algorithm.)"
            ),
            "starter": (
                "import hashlib\nimport hmac\nimport secrets\n\n"
                "ROUNDS = 1_000\n\n\n"
                "class AuthenticationError(Exception):\n    \"\"\"Raised when a password check fails.\"\"\"\n\n\n"
                "def hash_password(password, salt):\n"
                "    digest = salt + password.encode()\n"
                "    for _ in range(ROUNDS):\n"
                "        digest = hashlib.sha256(digest).digest()\n"
                "    return digest\n\n\n"
                "class User:\n"
                "    # __init__(self, name, password): keep name, salt and password_hash. NOT the password.\n"
                "    # check_password(self, candidate) -> bool\n"
                "    # change_password(self, old, new)\n"
                "    # __repr__: show only the name\n"
                "    pass\n"
            ),
            "hint": "In `__init__`: `self.salt = secrets.token_bytes(16)` and `self.password_hash = hash_password(password, self.salt)`. In `check_password`, hash the candidate with the same salt and compare with `hmac.compare_digest`. In `change_password`, verify `old` first, then check the length of `new`.",
            "solution": (
                "import hashlib\nimport hmac\nimport secrets\n\n"
                "ROUNDS = 1_000\n\n\n"
                "class AuthenticationError(Exception):\n    \"\"\"Raised when a password check fails.\"\"\"\n\n\n"
                "def hash_password(password, salt):\n"
                "    digest = salt + password.encode()\n"
                "    for _ in range(ROUNDS):\n"
                "        digest = hashlib.sha256(digest).digest()\n"
                "    return digest\n\n\n"
                "class User:\n"
                "    MIN_LENGTH = 8\n\n"
                "    def __init__(self, name, password):\n"
                "        self.name = name\n"
                "        self.salt = secrets.token_bytes(16)\n"
                "        self.password_hash = hash_password(password, self.salt)\n\n"
                "    def check_password(self, candidate):\n"
                "        candidate_hash = hash_password(candidate, self.salt)\n"
                "        return hmac.compare_digest(candidate_hash, self.password_hash)\n\n"
                "    def change_password(self, old, new):\n"
                "        if not self.check_password(old):\n"
                '            raise AuthenticationError("current password is incorrect")\n'
                "        if len(new) < self.MIN_LENGTH:\n"
                '            raise ValueError("new password must be at least 8 characters")\n'
                "        self.salt = secrets.token_bytes(16)\n"
                "        self.password_hash = hash_password(new, self.salt)\n\n"
                "    def __repr__(self):\n"
                '        return f"User(name={self.name!r})"\n'
            ),
            "check": """\
secret = "correct horse"
ada = User("ada", secret)
eve = User("eve", secret)
assert ada.name == "ada", "User should keep the name."
assert isinstance(ada.salt, bytes) and len(ada.salt) >= 16, "salt should be at least 16 random bytes."
assert isinstance(ada.password_hash, bytes), "password_hash should be the bytes returned by hash_password."
assert secret not in repr(ada) and secret not in str(vars(ada)), "The plain-text password must not be stored anywhere on the object."
assert repr(ada) == "User(name='ada')", f"repr should be \\"User(name='ada')\\" but is {repr(ada)!r}."
assert ada.salt != eve.salt, "Each user needs their own random salt."
assert ada.password_hash != eve.password_hash, "Same password + different salts must give different hashes."
assert ada.check_password(secret) is True, "The right password should be accepted."
assert ada.check_password("wrong guess") is False, "A wrong password should be rejected."
assert "compare_digest" in _code, "Compare the hashes with hmac.compare_digest, not ==."
try:
    ada.change_password("wrong guess", "a brand new password")
except AuthenticationError:
    pass
else:
    raise AssertionError("change_password with the wrong old password should raise AuthenticationError.")
try:
    ada.change_password(secret, "short")
except ValueError:
    pass
else:
    raise AssertionError("A new password shorter than 8 characters should raise ValueError.")
assert ada.check_password(secret) is True, "A failed change must leave the old password working."
old_salt = ada.salt
ada.change_password(secret, "brand new pass")
assert ada.check_password("brand new pass") is True, "The new password should work after changing it."
assert ada.check_password(secret) is False, "The old password must stop working after changing it."
assert ada.salt != old_salt, "Use a fresh salt when the password changes."
""",
        },
    },
]
