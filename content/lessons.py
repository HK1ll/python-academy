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


# Course outline: groups lessons for the sidebar, the home page and the progress page.
# Every lesson id must appear in exactly one section (build.py enforces this).
SECTIONS = [
    {
        "title": "Python Basics",
        "ids": [
            "hello-world", "variables", "numbers", "strings", "conditionals", "lists",
            "loops", "dictionaries", "functions", "comprehensions", "errors",
        ],
    },
    {"title": "Modules & Files", "ids": ["modules", "files", "data-files", "own-modules"]},
    {
        "title": "Object-Oriented Programming",
        "ids": ["classes", "class-design", "special-methods", "inheritance", "abstract-composition", "dataclasses-enums"],
    },
    {"title": "Intermediate Python", "ids": ["flexible-functions", "generators", "decorators"]},
    {
        "title": "Programming for Security",
        "ids": [
            "secure-classes", "regex", "collections-tools", "networking",
            "encoding", "integrity", "time-detection", "project-log-analyzer",
        ],
    },
    {
        "title": "Building Real Tools & Apps",
        "ids": ["cli-tools", "app-structure", "testing", "gui-concepts", "security-toolkit"],
    },
]

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
    # ------------------------------------------------------------------ flexible-functions
    {
        "id": "flexible-functions",
        "title": "Flexible Functions & Scope",
        "summary": "Variable arguments, keyword-only options, closures and recursion.",
        "blocks": [
            p("Functions can accept any number of arguments. `*name` collects extra positional arguments into a **tuple**, and `**name` collects extra keyword arguments into a **dictionary**."),
            code(
                """\
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3))
print(total())

def describe(**details):
    for key in sorted(details):
        print(key, "=", details[key])

describe(user="ada", role="admin")"""
            ),
            out(
                """\
6
0
role = admin
user = ada"""
            ),
            h("Options and unpacking"),
            p(
                "Parameters after a bare `*` are **keyword-only**: callers must name them. You can also *unpack* a list "
                "or dictionary into a call with `*` and `**`."
            ),
            code(
                """\
def connect(host, port=443, *, secure=True):
    return f"{host}:{port} secure={secure}"

print(connect("example.com"))
print(connect("example.com", 8443, secure=False))

settings = {"host": "example.org", "port": 22}
print(connect(**settings))

args = ["example.net", 80]
print(connect(*args))"""
            ),
            out(
                """\
example.com:443 secure=True
example.com:8443 secure=False
example.org:22 secure=True
example.net:80 secure=True"""
            ),
            sec(
                "Make risky options **keyword-only with a safe default**, like `verify_tls=True`. To turn it off, "
                "someone must write `verify_tls=False` out loud, which stands out in code review instead of hiding as a "
                "mystery `False` in a list of arguments."
            ),
            h("The mutable default trap"),
            p("A default value is created **once**, when the function is defined. A list default is then shared by every call."),
            code(
                """\
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag("a"))
print(add_tag("b"))

def add_tag_safe(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

print(add_tag_safe("a"))
print(add_tag_safe("b"))"""
            ),
            out(
                """\
['a']
['a', 'b']
['a']
['b']"""
            ),
            p("The safe pattern is `None` as the default, then create the list inside the function."),
            h("Scope"),
            p("A name assigned inside a function is **local** to it. Assigning to a name never changes a variable of the same name outside."),
            code(
                """\
counter = 0

def bump():
    counter = 100          # a brand-new LOCAL variable
    return counter

print(bump())
print(counter)

def bump_global():
    global counter
    counter += 1

bump_global()
print(counter)"""
            ),
            out(
                """\
100
0
1"""
            ),
            tip("Avoid `global`. Pass values in and return results instead, so a function's behaviour depends only on what it is given."),
            h("Closures"),
            p("A function defined inside another can **remember** the outer function's variables, even after the outer function has finished. `nonlocal` lets it change them."),
            code(
                """\
def make_multiplier(factor):
    def multiply(number):
        return number * factor
    return multiply

double = make_multiplier(2)
print(double(21))

def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
print(counter(), counter(), counter())"""
            ),
            out(
                """\
42
1 2 3"""
            ),
            h("Recursion"),
            p("A function can call itself. It needs a **base case** that stops the calls, and each call must move toward it."),
            code(
                """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))

def depth(nested):
    if not isinstance(nested, list):
        return 0
    return 1 + max((depth(item) for item in nested), default=0)

print(depth([1, [2, [3]], 4]))

def count_down(n):
    return count_down(n - 1)      # no base case!

try:
    count_down(10)
except RecursionError:
    print("Too deep: RecursionError")"""
            ),
            out(
                """\
120
3
Too deep: RecursionError"""
            ),
            sec("Code that recurses over **untrusted nested data** (deeply nested JSON, for instance) can be crashed by input nested thousands of levels deep. Cap the depth you accept, and handle `RecursionError`."),
        ],
        "exercise": {
            "prompt": (
                "Write two functions. `format_event(event_type, *details, **fields)` returns the event type in upper case, then "
                "(only if given) the details joined by spaces, then (only if given) the fields as `key=value` sorted by key and "
                "joined by spaces, with the parts separated by `\" | \"`. For example `format_event(\"login\", \"ok\", user=\"ada\", "
                "ip=\"1.2.3.4\")` is `LOGIN | ok | ip=1.2.3.4 user=ada`. `make_limiter(max_calls)` returns a function `allow()`: "
                "it returns `True` for the first `max_calls` calls and `False` afterwards. Each limiter keeps its own count."
            ),
            "starter": "def format_event(event_type, *details, **fields):\n    pass\n\n\ndef make_limiter(max_calls):\n    pass\n",
            "hint": "Build a list `parts = [event_type.upper()]` and append the details and fields strings only when they exist, then `\" | \".join(parts)`. For the limiter, keep `calls = 0` in the outer function, and in the inner function use `nonlocal calls`, increment, and return `calls <= max_calls`.",
            "solution": (
                "def format_event(event_type, *details, **fields):\n"
                "    parts = [event_type.upper()]\n"
                "    if details:\n"
                '        parts.append(" ".join(str(detail) for detail in details))\n'
                "    if fields:\n"
                '        parts.append(" ".join(f"{key}={fields[key]}" for key in sorted(fields)))\n'
                '    return " | ".join(parts)\n\n\n'
                "def make_limiter(max_calls):\n"
                "    calls = 0\n\n"
                "    def allow():\n"
                "        nonlocal calls\n"
                "        calls += 1\n"
                "        return calls <= max_calls\n\n"
                "    return allow\n"
            ),
            "check": """\
assert format_event("login") == "LOGIN", f"format_event('login') should be 'LOGIN' but is {format_event('login')!r}."
assert format_event("login", "ok") == "LOGIN | ok", f"got {format_event('login', 'ok')!r}"
assert format_event("login", "ok", "fast") == "LOGIN | ok fast", f"got {format_event('login', 'ok', 'fast')!r}"
assert format_event("login", user="ada") == "LOGIN | user=ada", f"got {format_event('login', user='ada')!r}"
got = format_event("login", "ok", user="ada", ip="1.2.3.4")
assert got == "LOGIN | ok | ip=1.2.3.4 user=ada", f"Expected 'LOGIN | ok | ip=1.2.3.4 user=ada' but got {got!r}."
first = make_limiter(2)
assert [first(), first(), first(), first()] == [True, True, False, False], "A limiter with max_calls=2 should allow exactly 2 calls."
second = make_limiter(1)
assert second() is True, "Each limiter must keep its own count (a new limiter starts fresh)."
assert first() is False, "The first limiter is still used up."
assert make_limiter(0)() is False, "max_calls=0 should never allow anything."
""",
        },
    },
    # ------------------------------------------------------------------ generators
    {
        "id": "generators",
        "title": "Iterators & Generators",
        "summary": "Produce values one at a time so huge inputs never fill memory.",
        "blocks": [
            p("A `for` loop works on anything **iterable**. Under the hood Python asks for an **iterator** with `iter()` and then calls `next()` until it runs out."),
            code(
                """\
letters = iter(["a", "b"])
print(next(letters))
print(next(letters))

try:
    next(letters)
except StopIteration:
    print("done")"""
            ),
            out(
                """\
a
b
done"""
            ),
            h("Generators"),
            p(
                "A function that uses `yield` is a **generator function**. Calling it doesn't run the body; it returns an "
                "iterator. Each `next()` runs the code until the next `yield`, hands back that value, and **pauses** there."
            ),
            code(
                """\
def countdown(n):
    while n > 0:
        yield n
        n -= 1

print(list(countdown(3)))

for value in countdown(2):
    print(value)"""
            ),
            out(
                """\
[3, 2, 1]
2
1"""
            ),
            p("Generators are **lazy**: nothing is produced until someone asks. Watch the order of the messages."),
            code(
                """\
def numbers():
    print("producing 1")
    yield 1
    print("producing 2")
    yield 2

gen = numbers()
print("created")
print(next(gen))
print(next(gen))"""
            ),
            out(
                """\
created
producing 1
1
producing 2
2"""
            ),
            h("Pipelines"),
            p("Generators chain together: each stage pulls one item at a time from the previous one, so a huge file is processed with almost no memory."),
            code(
                """\
def read_lines(text):
    for line in text.splitlines():
        yield line.strip()

def only_failures(lines):
    for line in lines:
        if "FAILED" in line:
            yield line

log = "ok 1\\nFAILED 2\\n  ok 3  \\nFAILED 4"
for line in only_failures(read_lines(log)):
    print(line)"""
            ),
            out(
                """\
FAILED 2
FAILED 4"""
            ),
            sec(
                "Attackers can send **enormous** inputs to exhaust memory. Read logs and uploads a line or a chunk at a time "
                "with generators, and enforce a maximum size, instead of loading everything with a single `read()`."
            ),
            h("Endless streams and iterable classes"),
            code(
                """\
from itertools import islice

def naturals():
    n = 1
    while True:
        yield n
        n += 1

print(list(islice(naturals(), 5)))

class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1

print(list(Countdown(3)))"""
            ),
            out(
                """\
[1, 2, 3, 4, 5]
[3, 2, 1]"""
            ),
            p("An endless generator is safe because it is lazy: `islice` takes just the first few values. A class becomes iterable by defining `__iter__`, and writing it as a generator is the easiest way."),
            warn("A generator can only be used **once**. After it is exhausted, looping over it again gives nothing. Call the generator function again to start over."),
        ],
        "exercise": {
            "prompt": (
                "Write the generator function `failed_ips(lines)`. `lines` is any iterable of log lines. Yield the **IP address** "
                "(the last word) of every line that starts with `Failed password for`, and ignore all other lines. It must be "
                "**lazy**: it may only read as many lines as it needs to produce the next value."
            ),
            "starter": "def failed_ips(lines):\n    pass\n",
            "hint": "Loop over `lines`. For each line, `if line.startswith(\"Failed password for\"):` then `yield line.split()[-1]`. Use `yield`, not a list, so it stays lazy.",
            "solution": (
                "def failed_ips(lines):\n"
                "    for line in lines:\n"
                '        if line.startswith("Failed password for"):\n'
                "            yield line.split()[-1]\n"
            ),
            "check": """\
pulled = []

def feed():
    for i in range(1, 1001):
        pulled.append(i)
        if i % 3 == 0:
            yield f"Failed password for user{i} from 10.0.0.{i}"
        else:
            yield f"Accepted password for user{i} from 10.0.0.1"

stream = failed_ips(feed())
assert next(stream) == "10.0.0.3", "The first failed login is line 3, from 10.0.0.3."
assert len(pulled) == 3, f"failed_ips must be lazy: it read {len(pulled)} lines just to find the first result (it should read 3). Use yield, not a list."
assert next(stream) == "10.0.0.6", "The second failed login is line 6."
assert len(pulled) == 6, "It should only have read 6 lines so far."
assert list(failed_ips([])) == [], "No lines means no results."
assert list(failed_ips(["Accepted password for a from 1.1.1.1", "cron: job done"])) == [], "Only 'Failed password for' lines count."
assert list(failed_ips(["Failed password for a from 1.1.1.1", "x", "Failed password for b from 2.2.2.2"])) == ["1.1.1.1", "2.2.2.2"], "It should yield every failed login's IP, in order."
""",
        },
    },
    # ------------------------------------------------------------------ decorators
    {
        "id": "decorators",
        "title": "Decorators & Context Managers",
        "summary": "Wrap behaviour around functions and blocks: access control, auditing and guaranteed cleanup.",
        "blocks": [
            p(
                "In Python, functions are values you can pass around. A **decorator** is a function that takes a function and "
                "returns an improved one. `@shout` above a function is shorthand for `greet = shout(greet)`."
            ),
            code(
                """\
def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def greet(name):
    return f"hello, {name}"

print(greet("ada"))"""
            ),
            out("HELLO, ADA"),
            p("`wrapper` accepts `*args, **kwargs` so it can forward any arguments. Use `functools.wraps` to keep the original function's name and documentation."),
            code(
                """\
from functools import wraps

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def add(a, b):
    return a + b

print(add(2, 3))
print(add.__name__)"""
            ),
            out(
                """\
calling add
5
add"""
            ),
            h("Decorators with arguments"),
            p("To configure a decorator, add one more layer: a function that takes the settings and returns the real decorator."),
            code(
                """\
from functools import wraps

def require_role(role):
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.get("role") != role:
                raise PermissionError(f"{user['name']} needs role {role!r}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_role("admin")
def delete_account(user, target):
    return f"{target} deleted by {user['name']}"

admin = {"name": "ada", "role": "admin"}
guest = {"name": "eve", "role": "guest"}

print(delete_account(admin, "bob"))
try:
    delete_account(guest, "bob")
except PermissionError as error:
    print("Denied:", error)"""
            ),
            out(
                """\
bob deleted by ada
Denied: eve needs role 'admin'"""
            ),
            sec(
                "Decorators keep **cross-cutting rules in one place**: permission checks, audit logging, rate limits. Put the "
                "rule on every sensitive function with one line, and a function can't forget it. (Real systems still "
                "enforce permissions on the server side too.)"
            ),
            h("Context managers"),
            p(
                "A `with` block guarantees setup and **cleanup**, even if an error happens inside. Any object with `__enter__` "
                "and `__exit__` works. Returning `False` from `__exit__` lets errors continue on their way."
            ),
            code(
                """\
class AuditScope:
    def __init__(self, action):
        self.action = action

    def __enter__(self):
        print("START", self.action)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        status = "FAILED" if exc_type else "OK"
        print("END", self.action, status)
        return False            # don't swallow the error

with AuditScope("backup"):
    print("working")

try:
    with AuditScope("restore"):
        raise ValueError("disk full")
except ValueError:
    print("error propagated")"""
            ),
            out(
                """\
START backup
working
END backup OK
START restore
END restore FAILED
error propagated"""
            ),
            p("`contextlib.contextmanager` builds one from a generator: code before `yield` is the setup, code after it (in `finally`) is the cleanup."),
            code(
                """\
from contextlib import contextmanager

@contextmanager
def opened(name):
    print("open", name)
    try:
        yield name
    finally:
        print("close", name)

with opened("db") as handle:
    print("using", handle)"""
            ),
            out(
                """\
open db
using db
close db"""
            ),
            sec("`with` and `finally` make sure privileged actions are always **closed out**: files closed, locks released, and the end of a sensitive operation logged, even when something fails halfway."),
        ],
        "exercise": {
            "prompt": (
                "Write a decorator and a context manager. `audit(log)` is a decorator factory: the wrapped function's calls are "
                "recorded in the list `log` as `(function_name, \"ok\")` after a successful call, or `(function_name, \"error\")` "
                "if it raises (the error must still propagate). The wrapped function must keep its `__name__`. "
                "`temporary_flag(settings, key, value)` is a context manager that sets `settings[key] = value` inside the "
                "`with` block and afterwards restores the old value (or removes the key if it wasn't there), **even if an error occurs**."
            ),
            "starter": "from contextlib import contextmanager\nfrom functools import wraps\n\n\ndef audit(log):\n    pass\n\n\n@contextmanager\ndef temporary_flag(settings, key, value):\n    yield\n",
            "hint": "`audit` needs three layers: `audit(log)` returns `decorator(func)` which returns `wrapper(*args, **kwargs)`. In the wrapper use `try`/`except Exception:` to append `\"error\"` and `raise` again. For the context manager, remember `existed = key in settings` and `previous = settings.get(key)`, set the new value, then `try: yield` / `finally:` restore.",
            "solution": (
                "from contextlib import contextmanager\nfrom functools import wraps\n\n\n"
                "def audit(log):\n"
                "    def decorator(func):\n"
                "        @wraps(func)\n"
                "        def wrapper(*args, **kwargs):\n"
                "            try:\n"
                "                result = func(*args, **kwargs)\n"
                "            except Exception:\n"
                '                log.append((func.__name__, "error"))\n'
                "                raise\n"
                '            log.append((func.__name__, "ok"))\n'
                "            return result\n"
                "        return wrapper\n"
                "    return decorator\n\n\n"
                "@contextmanager\n"
                "def temporary_flag(settings, key, value):\n"
                "    existed = key in settings\n"
                "    previous = settings.get(key)\n"
                "    settings[key] = value\n"
                "    try:\n"
                "        yield\n"
                "    finally:\n"
                "        if existed:\n"
                "            settings[key] = previous\n"
                "        else:\n"
                "            del settings[key]\n"
            ),
            "check": """\
log = []

@audit(log)
def divide(a, b):
    return a / b

assert divide(6, 3) == 2, "The wrapped function must still return its result."
try:
    divide(1, 0)
except ZeroDivisionError:
    pass
else:
    raise AssertionError("The error must still propagate out of the decorated function.")
assert log == [("divide", "ok"), ("divide", "error")], f"log should be [('divide', 'ok'), ('divide', 'error')] but is {log!r}."
assert divide.__name__ == "divide", "Use functools.wraps so the function keeps its name."

other_log = []

@audit(other_log)
def ping():
    return "pong"

assert ping() == "pong" and other_log == [("ping", "ok")] and len(log) == 2, "Each audit(log) decorator must write to its own log."

settings = {"debug": False}
with temporary_flag(settings, "debug", True):
    assert settings["debug"] is True, "Inside the block the new value must be set."
assert settings == {"debug": False}, f"The old value must be restored afterwards, but settings is {settings!r}."

with temporary_flag(settings, "trace", 1):
    assert settings["trace"] == 1, "A brand-new key must be set inside the block."
assert settings == {"debug": False}, f"A key that didn't exist before must be removed afterwards, but settings is {settings!r}."

try:
    with temporary_flag(settings, "debug", "temporary"):
        raise RuntimeError("boom")
except RuntimeError:
    pass
else:
    raise AssertionError("Errors inside the with block must propagate.")
assert settings == {"debug": False}, "The value must be restored even when an error happens inside the block."
""",
        },
    },
    # ------------------------------------------------------------------ secure-classes
    {
        "id": "secure-classes",
        "title": "Secure Passwords & Access Control",
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
    # ------------------------------------------------------------------ regex
    {
        "id": "regex",
        "title": "Regular Expressions",
        "summary": "Find, extract and validate text with patterns, the defender's log-reading tool.",
        "blocks": [
            p(
                "A **regular expression** (regex) is a pattern that describes text, such as \"three digits, then a dot\". "
                "Python's `re` module finds and extracts whatever matches. Regexes are the everyday tool for reading logs."
            ),
            code(
                r"""import re

log = "Failed password for admin from 203.0.113.5 port 22"

match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", log)
print(match.group(0))
print(match.group(1))"""
            ),
            out(
                """\
from 203.0.113.5
203.0.113.5"""
            ),
            p(
                "`re.search` looks anywhere in the text and returns a match (or `None`). `group(0)` is everything that "
                "matched, and `group(1)` is the part inside the first pair of parentheses. Write patterns as **raw "
                "strings** (`r\"...\"`) so Python leaves the backslashes alone."
            ),
            h("Pattern building blocks"),
            items(
                r"`\d` a digit, `\w` a letter, digit or underscore, `\s` whitespace, `.` any single character",
                "`+` one or more, `*` zero or more, `?` optional, `{2,5}` between 2 and 5",
                "`[abc]` one of these characters, `[^abc]` anything except these, `[a-z]` a range",
                "`^` start of the text, `$` end of the text, `( )` a group to capture, `|` means \"or\"",
                r'`\.` a literal dot (a plain `.` means "any character")',
            ),
            code(
                r"""import re

text = "Blocked 198.51.100.7, then 203.0.113.42 and 198.51.100.7 again"
ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
print(ips)
print(len(set(ips)))"""
            ),
            out(
                """\
['198.51.100.7', '203.0.113.42', '198.51.100.7']
2"""
            ),
            p("`re.findall` returns every match as a list. Turning it into a `set` removes the repeats, so you can count *distinct* addresses."),
            tip("The example addresses here (`203.0.113.x`, `198.51.100.x`, `192.0.2.x`) are reserved for documentation and testing, so they never belong to a real person."),
            h("Named groups"),
            p("Give groups names with `(?P<name>...)` to pull out labelled pieces."),
            code(
                r"""import re

line = "Sep 20 10:15:01 Failed password for admin from 203.0.113.5"
pattern = r"Failed password for (?P<user>\w+) from (?P<ip>[\d.]+)"

match = re.search(pattern, line)
print(match.group("user"))
print(match.group("ip"))
print(match.groupdict())"""
            ),
            out(
                """\
admin
203.0.113.5
{'user': 'admin', 'ip': '203.0.113.5'}"""
            ),
            h("Validation: fullmatch, not search"),
            p(
                "To check that a *whole* string is acceptable, use `re.fullmatch`. It demands that the pattern match the "
                "entire text. `re.search` succeeds if the pattern appears **anywhere**, which is a classic validation bug."
            ),
            code(
                r"""import re

def is_valid_username(name):
    return re.fullmatch(r"[a-z][a-z0-9_]{2,15}", name) is not None

print(is_valid_username("ada_99"))
print(is_valid_username("9lives"))
print(is_valid_username("bob; DROP TABLE"))

print(bool(re.search(r"[a-z]+", "ada; rm -rf /")))
print(bool(re.fullmatch(r"[a-z]+", "ada; rm -rf /")))"""
            ),
            out(
                """\
True
False
False
True
False"""
            ),
            sec(
                "**Validate with an allow-list**: describe exactly what *is* allowed and reject everything else. "
                "Trying to list what is *bad* always misses something. And use `fullmatch`, so hostile text can't hide "
                "after a harmless-looking start."
            ),
            h("Untrusted input inside a pattern"),
            p("If part of a pattern comes from a user, wrap it in `re.escape` so its special characters are treated as plain text."),
            code(
                r"""import re

user_input = "1.2.3.4"
pattern = re.escape(user_input)
print(pattern)
print(bool(re.fullmatch(pattern, "1.2.3.4")))
print(bool(re.fullmatch(pattern, "1x2y3z4")))"""
            ),
            out(
                r"""1\.2\.3\.4
True
False"""
            ),
            warn(
                "A pattern with **nested repetition**, like `(a+)+$`, can take exponentially long on crafted input. This "
                "is called **ReDoS** (regular-expression denial of service). Keep patterns simple, avoid repeating "
                "a repeated group, and be careful with patterns that come from outside."
            ),
            tip(r"A regex like `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` also matches `999.999.999.999`. Regexes find text; they don't understand numbers. Use the `ipaddress` module (coming up) to validate real addresses."),
        ],
        "exercise": {
            "prompt": (
                "Write `parse_failed_logins(text)`. `text` is a multi-line SSH log. Return a list of `(user, ip)` tuples, in "
                "order, for every **failed** login. Lines look like `... Failed password for admin from 203.0.113.5 port 22 "
                "ssh2`, and some say `Failed password for invalid user oracle from ...`. Ignore `Accepted` lines and anything else."
            ),
            "starter": "import re\n\n\ndef parse_failed_logins(text):\n    pass\n",
            "hint": r"Use `re.findall` with two capturing groups: `Failed password for (?:invalid user )?(\w+) from ([\d.]+)`. The `(?:...)` group is optional and not captured. With two groups, `findall` returns tuples.",
            "solution": r"""import re

PATTERN = re.compile(r"Failed password for (?:invalid user )?(\w+) from ([\d.]+)")


def parse_failed_logins(text):
    return PATTERN.findall(text)
""",
            "check": """\
log = (
    "Sep 20 10:15:01 sshd[101]: Failed password for admin from 203.0.113.5 port 22 ssh2\\n"
    "Sep 20 10:15:09 sshd[101]: Accepted password for ada from 198.51.100.7 port 22 ssh2\\n"
    "Sep 20 10:15:20 sshd[102]: Failed password for invalid user oracle from 203.0.113.5 port 22 ssh2\\n"
    "Sep 20 10:15:44 cron[7]: session opened for user root\\n"
    "Sep 20 10:16:00 sshd[103]: Failed password for root from 192.0.2.44 port 22 ssh2\\n"
)
expected = [("admin", "203.0.113.5"), ("oracle", "203.0.113.5"), ("root", "192.0.2.44")]
got = parse_failed_logins(log)
assert isinstance(got, list), f"Return a list of (user, ip) tuples, not {got!r}."
assert got == expected, f"Expected {expected!r} but got {got!r}."
assert parse_failed_logins("") == [], "An empty log should give an empty list."
assert parse_failed_logins("Accepted password for ada from 198.51.100.7 port 22") == [], "Accepted logins must be ignored."
""",
        },
    },
    # ------------------------------------------------------------------ collections-tools
    {
        "id": "collections-tools",
        "title": "Sorting & Counting",
        "summary": "Rank, pair up and tally data to spot the noisiest sources in a log.",
        "blocks": [
            p(
                "Analysing logs mostly means answering \"which one is the most?\" Python has small, sharp tools for "
                "sorting, pairing and counting. Start with sorting by something other than the item itself."
            ),
            code(
                """\
attempts = [("ada", 3), ("bob", 9), ("eve", 5)]

print(sorted(attempts))
print(sorted(attempts, key=lambda pair: pair[1]))
print(sorted(attempts, key=lambda pair: pair[1], reverse=True))"""
            ),
            out(
                """\
[('ada', 3), ('bob', 9), ('eve', 5)]
[('ada', 3), ('eve', 5), ('bob', 9)]
[('bob', 9), ('eve', 5), ('ada', 3)]"""
            ),
            p(
                "`key=` tells `sorted` what to sort **by**. A `lambda` is a tiny nameless function written inline: "
                "`lambda pair: pair[1]` means \"given a pair, return its second item\". `reverse=True` flips the order."
            ),
            h("enumerate and zip"),
            code(
                """\
users = ["ada", "bob", "eve"]

for number, user in enumerate(users, start=1):
    print(number, user)

scores = [90, 72, 85]
for user, score in zip(users, scores):
    print(user, score)

print(dict(zip(users, scores)))"""
            ),
            out(
                """\
1 ada
2 bob
3 eve
ada 90
bob 72
eve 85
{'ada': 90, 'bob': 72, 'eve': 85}"""
            ),
            p("`enumerate` numbers the items as you loop. `zip` walks several lists in step, pairing up their items."),
            h("Counter"),
            code(
                """\
from collections import Counter

ips = ["203.0.113.5", "198.51.100.7", "203.0.113.5", "203.0.113.5", "192.0.2.44", "198.51.100.7"]
counts = Counter(ips)

print(counts["203.0.113.5"])
print(counts["10.0.0.1"])
print(counts.most_common(2))"""
            ),
            out(
                """\
3
0
[('203.0.113.5', 3), ('198.51.100.7', 2)]"""
            ),
            p("A `Counter` tallies how often each item appears. Missing items count as `0`, and `most_common(n)` gives the top `n`."),
            sec("**Volume is a signal.** One address with hundreds of failed logins, or one user hit from dozens of places, stands out immediately once you count. Counting is the first step of almost every detection."),
            h("defaultdict"),
            p("A `defaultdict` creates a missing entry for you, so you can group things without checking first."),
            code(
                """\
from collections import defaultdict

users_by_ip = defaultdict(set)
for user, ip in [("admin", "192.0.2.1"), ("root", "192.0.2.1"), ("admin", "192.0.2.2")]:
    users_by_ip[ip].add(user)

print(sorted(users_by_ip["192.0.2.1"]))
print(len(users_by_ip["192.0.2.2"]))"""
            ),
            out(
                """\
['admin', 'root']
1"""
            ),
            sec("One source trying **many different usernames** is a classic sign of password spraying. Grouping by source and counting distinct usernames reveals it."),
            h("Generator expressions"),
            p("A comprehension without the brackets is a **generator expression**. You can pass it straight to `sum`, `max`, `any`, `all`, `Counter` and friends."),
            code(
                """\
print(sum(n * n for n in range(4)))
print(any(word == "root" for word in ["ada", "root"]))"""
            ),
            out(
                """\
14
True"""
            ),
        ],
        "exercise": {
            "prompt": (
                "Write `top_offenders(events, n)`. Each event is a dictionary like `{\"ip\": \"203.0.113.5\", \"success\": False}`. "
                "Count only the **failed** events per IP and return the top `n` as a list of `(ip, count)` tuples, biggest "
                "count first. When counts tie, put the IP that sorts first alphabetically first."
            ),
            "starter": "from collections import Counter\n\n\ndef top_offenders(events, n):\n    pass\n",
            "hint": "`Counter(event[\"ip\"] for event in events if not event[\"success\"])` counts failures. Then sort `failures.items()` with `key=lambda item: (-item[1], item[0])` (a tuple sorts by its first item, then its second) and slice the first `n`.",
            "solution": (
                "from collections import Counter\n\n\n"
                "def top_offenders(events, n):\n"
                '    failures = Counter(event["ip"] for event in events if not event["success"])\n'
                "    ranked = sorted(failures.items(), key=lambda item: (-item[1], item[0]))\n"
                "    return ranked[:n]\n"
            ),
            "check": """\
def failed(ip):
    return {"ip": ip, "success": False}

def ok(ip):
    return {"ip": ip, "success": True}

events = (
    [failed("203.0.113.5")] * 3
    + [failed("198.51.100.7")] * 2 + [ok("198.51.100.7")]
    + [failed("192.0.2.44")] * 2
    + [ok("10.0.0.9")]
)
got = top_offenders(events, 2)
assert got == [("203.0.113.5", 3), ("192.0.2.44", 2)], f"Expected [('203.0.113.5', 3), ('192.0.2.44', 2)] (tie at 2 goes to the lower IP) but got {got!r}."
assert len(top_offenders(events, 10)) == 3, "Only IPs with at least one failure should appear."
assert top_offenders(events, 1) == [("203.0.113.5", 3)], "n=1 should return just the top offender."
assert top_offenders([], 3) == [], "No events means no offenders."
assert top_offenders([ok("10.0.0.9")], 3) == [], "Successful logins must not be counted."
""",
        },
    },
    # ------------------------------------------------------------------ networking
    {
        "id": "networking",
        "title": "Networking Concepts (Offline)",
        "summary": "Parse and validate URLs, IP addresses and HTTP data, and learn to block unsafe destinations.",
        "blocks": [
            p(
                "Networking is computers exchanging messages. The Python inside your browser can't open network "
                "connections (that's part of what keeps this app safe), so these lessons focus on **reading and "
                "validating** network data. That is the skill defenders use most, and the standard library does the heavy lifting."
            ),
            h("URLs"),
            code(
                """\
from urllib.parse import urlparse

url = urlparse("https://example.com:8443/login?next=/home#top")
print(url.scheme)
print(url.hostname)
print(url.port)
print(url.path)
print(url.query)"""
            ),
            out(
                """\
https
example.com
8443
/login
next=/home"""
            ),
            p("Never split URLs by hand with string tricks. Use `urlparse`: it follows the real rules, including the odd ones attackers exploit."),
            h("IP addresses"),
            p("The `ipaddress` module understands IPv4 and IPv6 addresses and networks (ranges written like `192.168.1.0/24`)."),
            code(
                """\
import ipaddress

ip = ipaddress.ip_address("192.168.1.20")
print(ip.is_private)
print(ipaddress.ip_address("127.0.0.1").is_loopback)
print(ipaddress.ip_address("8.8.8.8").is_global)

network = ipaddress.ip_network("192.168.1.0/24")
print(ip in network)
print(network.num_addresses)

try:
    ipaddress.ip_address("999.1.1.1")
except ValueError:
    print("Invalid address")"""
            ),
            out(
                """\
True
True
True
True
256
Invalid address"""
            ),
            p("Unlike a regex, `ip_address` *understands* the numbers, so `999.1.1.1` is rejected. `is_global` is true only for addresses that are publicly routable on the internet."),
            h("HTTP status codes"),
            code(
                """\
from http import HTTPStatus

print(HTTPStatus(404).phrase)
print(HTTPStatus.FORBIDDEN.value)
print(HTTPStatus(500).phrase)"""
            ),
            out(
                """\
Not Found
403
Internal Server Error"""
            ),
            p(
                "Codes starting with **2** mean success, **3** redirect, **4** the client's mistake and **5** the server's "
                "failure. In logs, many `401` or `403` answers from one address are a warning sign."
            ),
            h("Reading an HTTP request"),
            p("An HTTP request is plain text: a request line, then headers, then a blank line. `*rest` collects the remaining items into a list."),
            code(
                r"""raw = "GET /admin?user=ada HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/8.0\r\n\r\n"

head, _, _body = raw.partition("\r\n\r\n")
request_line, *header_lines = head.split("\r\n")
method, target, version = request_line.split(" ")

headers = {}
for line in header_lines:
    name, _, value = line.partition(":")
    headers[name.strip().lower()] = value.strip()

print(method, target, version)
print(headers["host"])
print(headers)"""
            ),
            out(
                """\
GET /admin?user=ada HTTP/1.1
example.com
{'host': 'example.com', 'user-agent': 'curl/8.0'}"""
            ),
            sec(
                "**SSRF (server-side request forgery).** A service that fetches a URL on a user's behalf can be tricked into "
                "contacting *internal* addresses such as `http://127.0.0.1/`, `http://192.168.x.x/` or a cloud "
                "metadata address like `169.254.169.254`. Defenders check the scheme, the host, the port and the "
                "destination IP against an allow-list **before** fetching anything."
            ),
            warn(
                "A host **name** can also point at a private address (and can change after you check it). A real "
                "defence must check the IP address the name actually resolves to, at the moment of connecting. "
                "The exercise below does the offline part of the job."
            ),
        ],
        "exercise": {
            "prompt": (
                "Write `check_url(url)` for a service that may only fetch safe web addresses. Return `True` only when: "
                "the scheme is `https`; there is a host name; there is **no** username or password in the URL; the port is "
                "absent, `443` or `8443`; and, if the host is an IP address, it is **globally routable** (not private, loopback "
                "or link-local). Anything malformed returns `False`; it must never raise."
            ),
            "starter": "from ipaddress import ip_address\nfrom urllib.parse import urlparse\n\n\ndef check_url(url):\n    pass\n",
            "hint": "Parse with `urlparse` inside `try`/`except ValueError` (reading `.port` can raise). Check `.scheme`, `.hostname`, `.username`/`.password` and the port. To test whether the host is an IP, call `ip_address(hostname)` in another `try`: a ValueError means it's a normal name; otherwise return `address.is_global`.",
            "solution": (
                "from ipaddress import ip_address\n"
                "from urllib.parse import urlparse\n\n"
                "ALLOWED_PORTS = {443, 8443}\n\n\n"
                "def check_url(url):\n"
                "    try:\n"
                "        parts = urlparse(url)\n"
                "        port = parts.port\n"
                "    except ValueError:\n"
                "        return False\n"
                '    if parts.scheme != "https" or not parts.hostname:\n'
                "        return False\n"
                "    if parts.username or parts.password:\n"
                "        return False\n"
                "    if port is not None and port not in ALLOWED_PORTS:\n"
                "        return False\n"
                "    try:\n"
                "        address = ip_address(parts.hostname)\n"
                "    except ValueError:\n"
                "        return True  # a normal host name (a real system must also check what it resolves to)\n"
                "    return address.is_global\n"
            ),
            "check": """\
allowed = ["https://example.com/", "https://example.com:8443/x", "https://example.com:443/", "https://8.8.8.8/"]
blocked = [
    "http://example.com/", "ftp://example.com/", "example.com", "not a url", "",
    "https://example.com:8080/", "https://example.com:99999/",
    "https://127.0.0.1/", "https://192.168.1.5/admin", "https://10.0.0.1/", "https://169.254.169.254/latest/meta-data",
    "https://[::1]/", "https://localhost@127.0.0.1/",
    "https://user:pw@example.com/", "https://good.example.com@evil.example.net/",
    "https:///path",
]
for url in allowed:
    assert check_url(url) is True, f"{url!r} should be allowed (True)."
for url in blocked:
    assert check_url(url) is False, f"{url!r} should be rejected (False)."
""",
        },
    },
    # ------------------------------------------------------------------ encoding
    {
        "id": "encoding",
        "title": "Encoding, Bytes & Base64",
        "summary": "Understand text vs bytes, why encoding is not encryption, and how lookalike characters fool people.",
        "blocks": [
            p(
                "Computers store **bytes**: numbers from 0 to 255. Text becomes bytes through an **encoding**, almost always "
                "**UTF-8**. Python keeps the two apart: `str` is text and `bytes` is raw data."
            ),
            code(
                """\
text = "héllo"
data = text.encode("utf-8")

print(data)
print(len(text), len(data))
print(data.decode("utf-8"))"""
            ),
            out(
                r"""b'h\xc3\xa9llo'
5 6
héllo"""
            ),
            p("`é` is one character but two bytes in UTF-8, so the byte length can differ from the text length. That matters when you check sizes and limits."),
            code(
                """\
data = b"Hi!"
print(list(data))
print(data.hex())
print(bytes.fromhex("486921"))"""
            ),
            out(
                """\
[72, 105, 33]
486921
b'Hi!'"""
            ),
            h("Base64"),
            p("**Base64** turns any bytes into plain letters and digits so they can travel through text-only places such as email, URLs and HTTP headers."),
            code(
                r"""import base64

encoded = base64.b64encode(b"admin:secret")
print(encoded)
print(base64.b64decode(encoded))
print(base64.urlsafe_b64encode(b"\xfb\xff").decode())"""
            ),
            out(
                """\
b'YWRtaW46c2VjcmV0'
b'admin:secret'
-_8="""
            ),
            sec(
                "**Encoding is not encryption.** Base64 and hex hide nothing: anyone can reverse them in one line. "
                "`YWRtaW46c2VjcmV0` is simply `admin:secret`. That is exactly how HTTP Basic authentication sends credentials, "
                "which is why it is only safe over HTTPS."
            ),
            h("URL encoding"),
            code(
                """\
from urllib.parse import quote, unquote

print(quote("a b&c=d/é"))
print(quote("a b&c=d/é", safe=""))
print(unquote("%3Cscript%3E"))"""
            ),
            out(
                """\
a%20b%26c%3Dd/%C3%A9
a%20b%26c%3Dd%2F%C3%A9
<script>"""
            ),
            p("Special characters travel as `%` and two hex digits. Encoded input can hide dangerous text, so **decode first, then check**."),
            code(
                """\
from urllib.parse import unquote

path = "/files/%2e%2e/%2e%2e/etc/passwd"
decoded = unquote(path)

print(decoded)
print(".." in decoded)
print(".." in path)"""
            ),
            out(
                """\
/files/../../etc/passwd
True
False"""
            ),
            sec("A check that looks for `..` in the raw text misses `%2e%2e`. Always **decode (and normalise) input before validating it**, and validate again at the point where it is used. This is a classic path-traversal bug."),
            h("Lookalike characters"),
            p(
                "Unicode contains thousands of characters that look identical to ordinary letters. Below, the first letter of "
                "`fake` is the **Cyrillic** \"а\", not the Latin \"a\"."
            ),
            code(
                """\
import unicodedata

real = "admin"
fake = "аdmin"      # the first letter is Cyrillic, not Latin

print(real == fake)
print(fake.isascii())
print(unicodedata.name(fake[0]))
print(unicodedata.normalize("NFKC", "ｆｕｌｌ"))"""
            ),
            out(
                """\
False
False
CYRILLIC SMALL LETTER A
full"""
            ),
            p("`isascii()` catches non-ASCII characters, and `unicodedata.normalize(\"NFKC\", ...)` converts \"compatibility\" forms (like the full-width letters above) into their plain equivalents."),
            sec("**Homograph attacks**: an account named `аdmin` (Cyrillic) can impersonate `admin`. Restrict usernames to an allow-list of characters, normalise before comparing, and reject anything else."),
        ],
        "exercise": {
            "prompt": (
                "Write `decode_basic_auth(header)` for an HTTP `Authorization` header like `Basic YWRtaW46c2VjcmV0`. Return the "
                "tuple `(username, password)`. The scheme name is case-insensitive. Split at the **first** colon only "
                "(passwords may contain colons). For anything malformed (wrong scheme, missing token, invalid Base64, no colon, "
                "bytes that aren't valid UTF-8, or a value that isn't text) return `None`. It must **never raise**."
            ),
            "starter": "import base64\n\n\ndef decode_basic_auth(header):\n    pass\n",
            "hint": "`scheme, _, token = header.partition(\" \")`. Decode with `base64.b64decode(token, validate=True).decode(\"utf-8\")` inside `try`/`except ValueError` (both a bad Base64 string and bad UTF-8 raise a ValueError). Then `decoded.partition(\":\")` splits at the first colon.",
            "solution": (
                "import base64\n\n\n"
                "def decode_basic_auth(header):\n"
                "    if not isinstance(header, str):\n"
                "        return None\n"
                '    scheme, _, token = header.partition(" ")\n'
                '    if scheme.lower() != "basic" or not token:\n'
                "        return None\n"
                "    try:\n"
                '        decoded = base64.b64decode(token.strip(), validate=True).decode("utf-8")\n'
                "    except ValueError:\n"
                "        return None\n"
                '    user, separator, password = decoded.partition(":")\n'
                "    if not separator:\n"
                "        return None\n"
                "    return (user, password)\n"
            ),
            "check": """\
import base64 as real_base64

def header(raw, scheme="Basic"):
    return f"{scheme} " + real_base64.b64encode(raw).decode()

assert decode_basic_auth(header(b"admin:secret")) == ("admin", "secret"), "A normal header should decode to ('admin', 'secret')."
assert decode_basic_auth(header(b"ada:pa:ss")) == ("ada", "pa:ss"), "Split at the FIRST colon only: the password is 'pa:ss'."
assert decode_basic_auth(header(b"admin:secret", scheme="basic")) == ("admin", "secret"), "The scheme name is case-insensitive."
assert decode_basic_auth(header("zo\\u00eb:p\\u00e4ss".encode("utf-8"))) == ("zo\\u00eb", "p\\u00e4ss"), "UTF-8 text should decode properly."
bad = [
    "", "Basic", "Basic ", "Bearer abc123", "Basic !!!not-base64!!!", "Basic YWRtaW4",
    header(b"no-colon-here"), header(b"\\xff\\xfe:pw"), "Basicc " + real_base64.b64encode(b"a:b").decode(),
    "Basic YWRt*aW46c2VjcmV0", "Basic YWRtaW46 c2VjcmV0",   # a valid header with a stray character/space inside
    None, 42, b"Basic YTpi",
]
for value in bad:
    try:
        result = decode_basic_auth(value)
    except Exception as error:
        raise AssertionError(f"decode_basic_auth({value!r}) must not raise, but raised {type(error).__name__}: {error}") from None
    assert result is None, f"decode_basic_auth({value!r}) should return None but returned {result!r}."
""",
        },
    },
    # ------------------------------------------------------------------ integrity
    {
        "id": "integrity",
        "title": "Integrity: Hashes, HMAC & Tamper-Evident Logs",
        "summary": "Detect changes to files and records, and prove a message wasn't forged.",
        "blocks": [
            p(
                "**Integrity** means data hasn't been changed. A hash is a fingerprint of the data, so if the fingerprint "
                "still matches, the data is unchanged. Big files are hashed in **chunks** so they never have to fit in memory."
            ),
            code(
                """\
import hashlib

with open("data.bin", "wb") as file:
    file.write(b"hello " * 1000)

digest = hashlib.sha256()
with open("data.bin", "rb") as file:
    while chunk := file.read(1024):
        digest.update(chunk)

print(digest.hexdigest() == hashlib.sha256(b"hello " * 1000).hexdigest())
print(len(digest.hexdigest()))"""
            ),
            out(
                """\
True
64"""
            ),
            p("`while chunk := file.read(1024)` reads a piece, stores it in `chunk`, and keeps looping until the file is empty. `mode=\"rb\"` reads raw bytes."),
            warn("**MD5 and SHA-1 are broken** for security use: attackers can craft two different files with the same hash. Use SHA-256 or better."),
            h("Verifying a download"),
            p("Publishers list the expected hash of a file. Compute it yourself and compare with `hmac.compare_digest`."),
            code(
                """\
import hashlib
import hmac

expected = hashlib.sha256(b"installer-bytes").hexdigest()

def verify(data, expected_hex):
    actual = hashlib.sha256(data).hexdigest()
    return hmac.compare_digest(actual, expected_hex)

print(verify(b"installer-bytes", expected))
print(verify(b"installer-bytes!", expected))"""
            ),
            out(
                """\
True
False"""
            ),
            p("A hash alone can't stop a clever attacker: they can change the file **and** recompute the hash. What proves *who* made something is a **secret key**."),
            h("HMAC"),
            p("An **HMAC** mixes a secret key into the hash. Only someone who knows the key can create a valid tag, so it proves the message is authentic **and** unaltered."),
            code(
                """\
import hashlib
import hmac

key = b"shared-secret-key"
message = b"transfer 100 to bob"
tag = hmac.new(key, message, hashlib.sha256).hexdigest()

print(tag[:16])

same = hmac.new(key, message, hashlib.sha256).hexdigest()
forged = hmac.new(b"wrong-key", message, hashlib.sha256).hexdigest()
tampered = hmac.new(key, b"transfer 900 to bob", hashlib.sha256).hexdigest()

print(hmac.compare_digest(tag, same))
print(hmac.compare_digest(tag, forged))
print(hmac.compare_digest(tag, tampered))"""
            ),
            out(
                """\
c3e2b5cb52e9b0f6
True
False
False"""
            ),
            sec("Use an HMAC to protect anything you hand to a user and later trust when it comes back (session tokens, download links, form fields): if the tag doesn't match, someone edited it."),
            h("Hash chains"),
            p(
                "A **hash chain** links records: each entry's hash includes the **previous** entry's hash. Changing any old record "
                "changes its hash, which changes the next hash, and so on, so every later hash stops matching."
            ),
            code(
                """\
import hashlib

def link(previous_hash, record):
    return hashlib.sha256((previous_hash + record).encode()).hexdigest()

records = ["login ada", "delete file", "logout ada"]

previous = "0" * 64
for record in records:
    previous = link(previous, record)
original_head = previous
print(original_head[:12])

records[1] = "read file"        # someone edits history...
previous = "0" * 64
for record in records:
    previous = link(previous, record)
print(previous == original_head)"""
            ),
            out(
                """\
b660354d725e
False"""
            ),
            sec(
                "A hash chain makes tampering **evident**, not impossible: an attacker who can rewrite the whole log can recompute "
                "the entire chain. So defenders also keep the latest hash (the \"head\") somewhere the attacker can't reach, "
                "such as another server or write-once storage, and compare against it."
            ),
        ],
        "exercise": {
            "prompt": (
                "Build a tamper-evident `AuditLog`. `entries` is a list of `(text, digest)` tuples. Each digest is `link(previous_digest, text)`, "
                "where the first previous digest is `GENESIS`. `append(text)` adds an entry. The read-only property `head` is the "
                "last digest (or `GENESIS` for an empty log). `verify()` recomputes the whole chain and returns `True` only if every "
                "digest matches."
            ),
            "starter": (
                "import hashlib\n\n"
                'GENESIS = "0" * 64\n\n\n'
                "def link(previous_hash, text):\n"
                "    return hashlib.sha256((previous_hash + text).encode()).hexdigest()\n\n\n"
                "class AuditLog:\n"
                "    def __init__(self):\n"
                "        self.entries = []\n\n"
                "    # add: the head property, append(text) and verify()\n"
            ),
            "hint": "`head` is `self.entries[-1][1]` when there are entries, otherwise `GENESIS`. `append` stores `(text, link(self.head, text))`. `verify` starts with `previous = GENESIS` and for each `(text, digest)` checks `link(previous, text) == digest`, then sets `previous = digest`.",
            "solution": (
                "import hashlib\n\n"
                'GENESIS = "0" * 64\n\n\n'
                "def link(previous_hash, text):\n"
                "    return hashlib.sha256((previous_hash + text).encode()).hexdigest()\n\n\n"
                "class AuditLog:\n"
                "    def __init__(self):\n"
                "        self.entries = []\n\n"
                "    @property\n"
                "    def head(self):\n"
                "        return self.entries[-1][1] if self.entries else GENESIS\n\n"
                "    def append(self, text):\n"
                "        self.entries.append((text, link(self.head, text)))\n\n"
                "    def verify(self):\n"
                "        previous = GENESIS\n"
                "        for text, digest in self.entries:\n"
                "            if link(previous, text) != digest:\n"
                "                return False\n"
                "            previous = digest\n"
                "        return True\n"
            ),
            "check": """\
def build():
    log = AuditLog()
    for text in ["login ada", "delete file", "logout ada"]:
        log.append(text)
    return log

empty = AuditLog()
assert empty.head == GENESIS, "An empty log's head should be GENESIS."
assert empty.verify() is True, "An empty log is valid."

log = build()
assert len(log.entries) == 3 and log.entries[0][0] == "login ada", "entries should hold (text, digest) tuples in order."
assert log.entries[0][1] == link(GENESIS, "login ada"), "The first digest is link(GENESIS, text)."
assert log.entries[1][1] == link(log.entries[0][1], "delete file"), "Each digest is link(previous_digest, text)."
assert log.head == log.entries[-1][1], "head should be the last digest."
assert log.verify() is True, "An untouched log must verify."

edited = build()
edited.entries[1] = ("read file", edited.entries[1][1])
assert edited.verify() is False, "Editing an entry's text must make verify() False."

forged_digest = build()
forged_digest.entries[2] = (forged_digest.entries[2][0], "f" * 64)
assert forged_digest.verify() is False, "Replacing a digest must make verify() False."

removed = build()
del removed.entries[1]
assert removed.verify() is False, "Deleting an entry from the middle must make verify() False."

# An attacker who recomputes the WHOLE chain passes verify(), but the head changes, which is what defenders compare.
attacker = build()
anchor = attacker.head
rewritten = AuditLog()
for text in ["login ada", "read file", "logout ada"]:
    rewritten.append(text)
assert rewritten.verify() is True, "A correctly recomputed chain is internally consistent."
assert rewritten.head != anchor, "But its head differs from the original head. That is how the tampering is caught."
""",
        },
    },
    # ------------------------------------------------------------------ time-detection
    {
        "id": "time-detection",
        "title": "Time-Based Detection",
        "summary": "Work with dates and times, and spot attacks by how fast events happen.",
        "blocks": [
            p("Most attacks show up as a **rate**: too many events in too little time. First, dates and times in Python."),
            code(
                """\
from datetime import datetime, timedelta

stamp = datetime.strptime("2026-09-20 10:15:30", "%Y-%m-%d %H:%M:%S")
print(stamp.year, stamp.hour)
print(stamp + timedelta(minutes=5))
print(stamp.strftime("%d %b %Y, %H:%M"))"""
            ),
            out(
                """\
2026 10
2026-09-20 10:20:30
20 Sep 2026, 10:15"""
            ),
            p("`strptime` **parses** text into a `datetime` using a format, `strftime` **formats** one back to text, and `timedelta` is an amount of time you can add or subtract."),
            code(
                """\
from datetime import datetime, timedelta

start = datetime(2026, 9, 20, 10, 0, 0)
end = datetime(2026, 9, 20, 10, 4, 30)

gap = end - start
print(gap)
print(gap.total_seconds())
print(gap < timedelta(minutes=5))"""
            ),
            out(
                """\
0:04:30
270.0
True"""
            ),
            p("Subtracting two datetimes gives a `timedelta`, which you can compare, print or turn into seconds."),
            h("Time zones"),
            p("A **naive** datetime has no time zone; an **aware** one does. Python refuses to compare the two, which prevents a whole class of silent mistakes."),
            code(
                """\
from datetime import datetime, timezone

aware = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
naive = datetime(2026, 9, 20, 10, 0)

print(aware.isoformat())
try:
    print(aware < naive)
except TypeError:
    print("cannot compare naive and aware")"""
            ),
            out(
                """\
2026-09-20T10:00:00+00:00
cannot compare naive and aware"""
            ),
            sec("**Log in UTC**, always. When servers in different time zones log local times, events line up wrongly and an attack spread across machines can look like harmless, unrelated blips."),
            h("A sliding window"),
            p(
                "To detect bursts, keep only the events from the last N seconds. A `deque` (double-ended queue) removes items "
                "from the front quickly: add new events at the back, drop old ones from the front."
            ),
            code(
                """\
from collections import deque
from datetime import datetime, timedelta

def parse(text):
    return datetime.strptime(text, "%H:%M:%S")

WINDOW = timedelta(seconds=60)
recent = deque()
alerts = []

for text in ["10:00:00", "10:00:20", "10:00:50", "10:02:00", "10:02:10"]:
    moment = parse(text)
    recent.append(moment)
    while moment - recent[0] > WINDOW:
        recent.popleft()
    if len(recent) >= 3:
        alerts.append(text)

print(alerts)"""
            ),
            out("['10:00:50']"),
            p("Three events fell within 60 seconds only at `10:00:50`. By `10:02:00` the early ones had aged out of the window."),
            sec(
                "**Rate-based rules** like \"5 failed logins from one address within a minute\" catch brute-force attacks "
                "without flagging the person who mistypes a password once a day. Tune the limit and window to your normal traffic."
            ),
        ],
        "exercise": {
            "prompt": (
                "Write `burst_ips(events, limit, window_seconds)`. `events` is a list of `(timestamp, ip)` tuples in chronological "
                "order, where `timestamp` looks like `\"2026-09-20 10:00:00\"`. Return a **sorted** list of every IP that had at least "
                "`limit` events inside some window of `window_seconds` seconds (events exactly `window_seconds` apart still count as inside)."
            ),
            "starter": "from collections import defaultdict, deque\nfrom datetime import datetime, timedelta\n\n\ndef burst_ips(events, limit, window_seconds):\n    pass\n",
            "hint": "Keep a `defaultdict(deque)` of recent times per IP. For each event: parse the timestamp with `datetime.strptime(stamp, \"%Y-%m-%d %H:%M:%S\")`, append it, pop from the left while `moment - times[0] > window`, and flag the IP when `len(times) >= limit`.",
            "solution": (
                "from collections import defaultdict, deque\nfrom datetime import datetime, timedelta\n\n\n"
                "def burst_ips(events, limit, window_seconds):\n"
                "    window = timedelta(seconds=window_seconds)\n"
                "    recent = defaultdict(deque)\n"
                "    flagged = set()\n"
                "    for stamp, ip in events:\n"
                '        moment = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")\n'
                "        times = recent[ip]\n"
                "        times.append(moment)\n"
                "        while moment - times[0] > window:\n"
                "            times.popleft()\n"
                "        if len(times) >= limit:\n"
                "            flagged.add(ip)\n"
                "    return sorted(flagged)\n"
            ),
            "check": """\
events = [
    ("2026-09-20 10:00:00", "203.0.113.5"),
    ("2026-09-20 10:00:05", "198.51.100.7"),
    ("2026-09-20 10:00:10", "203.0.113.5"),
    ("2026-09-20 10:00:20", "203.0.113.5"),
    ("2026-09-20 10:01:00", "192.0.2.44"),
    ("2026-09-20 10:01:30", "192.0.2.44"),
    ("2026-09-20 10:02:00", "192.0.2.44"),
    ("2026-09-20 10:05:05", "198.51.100.7"),
    ("2026-09-20 10:10:05", "198.51.100.7"),
]
got = burst_ips(events, 3, 60)
assert got == ["192.0.2.44", "203.0.113.5"], f"limit=3, window=60 should give ['192.0.2.44', '203.0.113.5'] (events exactly 60s apart count) but got {got!r}."
assert burst_ips(events, 3, 59) == ["203.0.113.5"], f"With a 59-second window only 203.0.113.5 qualifies, got {burst_ips(events, 3, 59)!r}."
assert burst_ips(events, 2, 10) == ["203.0.113.5"], f"limit=2, window=10 should give ['203.0.113.5'], got {burst_ips(events, 2, 10)!r}."
assert burst_ips(events, 3, 3600) == ["192.0.2.44", "198.51.100.7", "203.0.113.5"], f"With a whole hour as the window, all three IPs have 3 events, got {burst_ips(events, 3, 3600)!r}."
assert burst_ips(events, 4, 3600) == [], "No IP has 4 events, even within an hour."
assert burst_ips([], 3, 60) == [], "No events, no bursts."
across = [("2026-09-20 23:59:50", "10.9.9.9"), ("2026-09-21 00:00:05", "10.9.9.9"), ("2026-09-21 00:00:10", "10.9.9.9")]
assert burst_ips(across, 3, 30) == ["10.9.9.9"], "Windows must work across midnight (compare full dates, not just times)."
other_days = [("2026-09-19 10:00:00", "10.8.8.8"), ("2026-09-20 10:00:05", "10.8.8.8"), ("2026-09-21 10:00:10", "10.8.8.8")]
assert burst_ips(other_days, 3, 30) == [], "Events on DIFFERENT days at the same time of day are a day apart, not seconds apart. Compare full dates."
assert burst_ips(events, 3, 60) == got, "Calling the function twice must give the same answer (no leftover state)."
""",
        },
    },
    # ------------------------------------------------------------------ project-log-analyzer
    {
        "id": "project-log-analyzer",
        "title": "Project: Log Analyzer",
        "summary": "Put it all together: read a real-looking log file and build a small detection tool.",
        "blocks": [
            p(
                "Time for a real project. Security analysts read authentication logs to spot attacks. You will build a small "
                "**log analyzer** that combines almost everything you have learned: files, regular expressions, "
                "dataclasses, classes, `Counter` and `sorted`."
            ),
            h("Plan before you code"),
            items(
                "**Parse** each line into an `Event` (time, result, user, IP), skipping lines that don't fit.",
                "**Count** failed logins per IP address.",
                "**Flag** addresses with too many failures.",
                "**Report** the findings and save them to a file.",
            ),
            p("The starting code below turns one log line into an `Event`. Run it, then read how it works."),
            code(
                r"""import re
from dataclasses import dataclass

LINE = re.compile(
    r"(?P<time>\d\d:\d\d:\d\d) (?P<result>Failed|Accepted) password "
    r"for (?P<user>\w+) from (?P<ip>[\d.]+)"
)

@dataclass(frozen=True)
class Event:
    time: str
    result: str
    user: str
    ip: str

def parse_line(line):
    match = LINE.fullmatch(line)
    return Event(**match.groupdict()) if match else None

print(parse_line("10:15:01 Failed password for admin from 203.0.113.5"))
print(parse_line("this line is corrupted %%%"))"""
            ),
            out(
                """\
Event(time='10:15:01', result='Failed', user='admin', ip='203.0.113.5')
None"""
            ),
            p("`Event(**match.groupdict())` unpacks the dictionary of named groups into keyword arguments. `parse_line` returns `None` for a line it can't understand instead of crashing."),
            sec(
                "**Logs are untrusted, messy input**: they can be truncated, corrupted, or even contain text an attacker chose. "
                "Robust tools never crash on a strange line. They count it, skip it and carry on. Also, never *execute* or "
                "*trust* anything you read out of a log."
            ),
            tip("Read a file line by line with `for line in file:`, and `strip()` each line. Skip blank lines before parsing."),
        ],
        "exercise": {
            "prompt": (
                "Build the class `LogAnalyzer(path)`. It reads the log file and keeps `events` (a list of `Event`) and `skipped` "
                "(how many non-blank lines could not be parsed). Blank lines are ignored entirely. Methods: "
                "`failures_by_ip()` returns a dictionary of IP to number of **failed** logins. `suspicious_ips(threshold=3)` returns "
                "a sorted list of IPs with at least `threshold` failures. `users_targeted(ip)` returns a sorted list of the "
                "distinct usernames that IP **failed** to log in as. `report()` returns the text shown in the starter comments. "
                "`write_report(path)` saves the report to a file."
            ),
            "files": {
                "auth.log": (
                    "10:15:01 Failed password for admin from 203.0.113.5\n"
                    "10:15:04 Failed password for root from 203.0.113.5\n"
                    "10:15:07 Failed password for oracle from 203.0.113.5\n"
                    "10:15:30 Accepted password for ada from 198.51.100.7\n"
                    "10:16:02 Failed password for ada from 198.51.100.7\n"
                    "this line is corrupted %%%\n"
                    "10:17:45 Failed password for admin from 192.0.2.44\n"
                    "10:17:50 Failed password for admin from 192.0.2.44\n"
                    "\n"
                    "10:18:20 Accepted password for grace from 192.0.2.99\n"
                    "10:19:00 Failed password for root from 203.0.113.5\n"
                )
            },
            "starter": r'''import re
from collections import Counter
from dataclasses import dataclass

LINE = re.compile(
    r"(?P<time>\d\d:\d\d:\d\d) (?P<result>Failed|Accepted) password "
    r"for (?P<user>\w+) from (?P<ip>[\d.]+)"
)


@dataclass(frozen=True)
class Event:
    time: str
    result: str
    user: str
    ip: str


def parse_line(line):
    match = LINE.fullmatch(line)
    return Event(**match.groupdict()) if match else None


class LogAnalyzer:
    # __init__(self, path): fill self.events and self.skipped from the file
    # failures_by_ip(self)            -> {"203.0.113.5": 4, ...}
    # suspicious_ips(self, threshold=3) -> sorted list of IPs with >= threshold failures
    # users_targeted(self, ip)        -> sorted list of distinct usernames that failed
    # report(self) -> text like:
    #     Parsed events: 9
    #     Skipped lines: 1
    #     Suspicious IPs (3+ failures): 203.0.113.5      (or "none")
    # write_report(self, path)        -> save the report to a file
    pass


analyzer = LogAnalyzer("auth.log")
print(analyzer.report())
''',
            "hint": "In `__init__`, loop over the file, `strip()` each line, `continue` on blank lines, call `parse_line`, and either append the event or add 1 to `self.skipped`. `failures_by_ip` can be `dict(Counter(e.ip for e in self.events if e.result == 'Failed'))`. The report joins the flagged IPs with `', '.join(...)` and falls back to `'none'` when the list is empty.",
            "solution": r'''import re
from collections import Counter
from dataclasses import dataclass

LINE = re.compile(
    r"(?P<time>\d\d:\d\d:\d\d) (?P<result>Failed|Accepted) password "
    r"for (?P<user>\w+) from (?P<ip>[\d.]+)"
)


@dataclass(frozen=True)
class Event:
    time: str
    result: str
    user: str
    ip: str


def parse_line(line):
    match = LINE.fullmatch(line)
    return Event(**match.groupdict()) if match else None


class LogAnalyzer:
    def __init__(self, path):
        self.events = []
        self.skipped = 0
        with open(path) as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                event = parse_line(line)
                if event is None:
                    self.skipped += 1
                else:
                    self.events.append(event)

    def failures_by_ip(self):
        return dict(Counter(e.ip for e in self.events if e.result == "Failed"))

    def suspicious_ips(self, threshold=3):
        return sorted(ip for ip, count in self.failures_by_ip().items() if count >= threshold)

    def users_targeted(self, ip):
        return sorted({e.user for e in self.events if e.ip == ip and e.result == "Failed"})

    def report(self):
        flagged = ", ".join(self.suspicious_ips()) or "none"
        return (
            f"Parsed events: {len(self.events)}\n"
            f"Skipped lines: {self.skipped}\n"
            f"Suspicious IPs (3+ failures): {flagged}"
        )

    def write_report(self, path):
        with open(path, "w") as file:
            file.write(self.report() + "\n")


analyzer = LogAnalyzer("auth.log")
print(analyzer.report())
''',
            "check": """\
analyzer = LogAnalyzer("auth.log")
assert len(analyzer.events) == 9, f"9 lines are valid events but analyzer.events has {len(analyzer.events)}."
assert all(isinstance(event, Event) for event in analyzer.events), "events must be a list of Event objects."
assert analyzer.skipped == 1, f"Exactly 1 non-blank line is corrupted but skipped is {analyzer.skipped}. (Blank lines must not count.)"
assert analyzer.failures_by_ip() == {"203.0.113.5": 4, "198.51.100.7": 1, "192.0.2.44": 2}, f"failures_by_ip() is wrong: {analyzer.failures_by_ip()!r}"
assert analyzer.suspicious_ips() == ["203.0.113.5"], f"suspicious_ips() should be ['203.0.113.5'] but is {analyzer.suspicious_ips()!r}."
assert analyzer.suspicious_ips(threshold=2) == ["192.0.2.44", "203.0.113.5"], f"suspicious_ips(threshold=2) should be sorted: got {analyzer.suspicious_ips(threshold=2)!r}."
assert analyzer.suspicious_ips(threshold=99) == [], "No IP has 99 failures."
assert analyzer.users_targeted("203.0.113.5") == ["admin", "oracle", "root"], f"users_targeted is wrong: {analyzer.users_targeted('203.0.113.5')!r}"
assert analyzer.users_targeted("192.0.2.99") == [], "Successful logins don't count as targeted users."
expected = "Parsed events: 9\\nSkipped lines: 1\\nSuspicious IPs (3+ failures): 203.0.113.5"
assert analyzer.report() == expected, f"report() should be exactly:\\n{expected}\\nbut it is:\\n{analyzer.report()}"
analyzer.write_report("report-out.txt")
with open("report-out.txt") as saved:
    assert saved.read().strip() == expected, "write_report() should save the report text to the file."
with open("empty.log", "w") as handle:
    handle.write("\\n\\n")
quiet = LogAnalyzer("empty.log")
assert quiet.events == [] and quiet.skipped == 0, "An empty log has no events and skips nothing."
assert quiet.report() == "Parsed events: 0\\nSkipped lines: 0\\nSuspicious IPs (3+ failures): none", f"Unexpected report for an empty log: {quiet.report()!r}"
""",
        },
    },
    # ------------------------------------------------------------------ cli-tools
    {
        "id": "cli-tools",
        "title": "Command-Line Tools",
        "summary": "Read flags, options and subcommands with argparse, the way real programs do.",
        "blocks": [
            p(
                "Programs run from a terminal read their input from **command-line arguments**: the words after the "
                "program's name, like `python backup.py --verbose files/`. Python's built-in `argparse` module turns "
                "those words into ordinary Python values."
            ),
            code(
                """\
import argparse

parser = argparse.ArgumentParser(description="Greet someone")
parser.add_argument("name")

args = parser.parse_args(["Ada"])
print(args.name)
print(type(args))"""
            ),
            out(
                """\
Ada
<class 'argparse.Namespace'>"""
            ),
            p(
                "`parser.parse_args()` normally reads the real command line automatically. This app has no real "
                "command line, so the examples pass a list of words instead, exactly like typing `python program.py Ada` would."
            ),
            h("Flags and options"),
            code(
                """\
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--shout", action="store_true")
parser.add_argument("--times", type=int, default=1)

args = parser.parse_args(["ada", "--shout", "--times", "3"])
print(args.name, args.shout, args.times)

args2 = parser.parse_args(["bob"])
print(args2.name, args2.shout, args2.times)"""
            ),
            out(
                """\
ada True 3
bob False 1"""
            ),
            p("`action=\"store_true\"` makes a flag that needs no value: present means `True`, absent means `False`. `type=int` converts the text automatically, and rejects anything that isn't a whole number."),
            h("Choices, and handling a bad value"),
            code(
                """\
import argparse


class QuietParser(argparse.ArgumentParser):
    # By default, an invalid argument makes argparse print its own message and exit the
    # whole program. Overriding error() lets a larger app catch the problem itself instead.
    def error(self, message):
        raise ValueError(message)


parser = QuietParser()
parser.add_argument("--level", choices=["low", "medium", "high"], default="medium")

args = parser.parse_args(["--level", "high"])
print(args.level)

try:
    parser.parse_args(["--level", "extreme"])
except ValueError:
    print("Rejected: 'extreme' is not a valid choice")"""
            ),
            out(
                """\
high
Rejected: 'extreme' is not a valid choice"""
            ),
            sec(
                "**Validate at the boundary, again.** `choices=[...]` and `type=int` reject bad input before your "
                "program's real logic ever runs, the same allow-list discipline as the `@property` setters and "
                "`Enum` conversions earlier in the course."
            ),
            h("Subcommands"),
            p("One program can offer several **subcommands**, each with its own options, the way `git commit` and `git push` share one `git` but behave completely differently."),
            code(
                """\
import argparse


class QuietParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


parser = QuietParser(prog="toolkit")
subparsers = parser.add_subparsers(dest="command")

scan_parser = subparsers.add_parser("scan")
scan_parser.add_argument("target")

report_parser = subparsers.add_parser("report")
report_parser.add_argument("--format", choices=["text", "json"], default="text")


def run(argv):
    args = parser.parse_args(argv)
    if args.command == "scan":
        return f"Scanning {args.target}..."
    elif args.command == "report":
        return f"Building a {args.format} report"
    return "No command given"


print(run(["scan", "10.0.0.5"]))
print(run(["report", "--format", "json"]))
print(run([]))"""
            ),
            out(
                """\
Scanning 10.0.0.5...
Building a json report
No command given"""
            ),
            tip("On your own computer, call `parser.parse_args()` with no list at all, and argparse reads the real command line (`sys.argv[1:]`) for you."),
            example(
                """\
import argparse


def main():
    parser = argparse.ArgumentParser(description="A tiny backup tool")
    parser.add_argument("source")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, but change nothing")
    args = parser.parse_args()          # reads sys.argv for real

    print(f"Backing up {args.source}" + (" (dry run)" if args.dry_run else ""))


if __name__ == "__main__":
    main()"""
            ),
        ],
        "exercise": {
            "prompt": (
                "Write `build_parser()`, returning an `ArgumentParser` with: a positional argument `name`; a flag "
                "`--shout` (`action=\"store_true\"`); and `--times` (`type=int`, `default=1`). Then write `greet(args)`, "
                "returning a **list** of greeting strings: `f\"Hello, {name}!\"` (or shouted in capitals) repeated `times` times."
            ),
            "starter": "import argparse\n\n\ndef build_parser():\n    pass\n\n\ndef greet(args):\n    pass\n",
            "hint": "`parser.add_argument(\"name\")`, `parser.add_argument(\"--shout\", action=\"store_true\")`, `parser.add_argument(\"--times\", type=int, default=1)`. In `greet`, build one message (upper-cased with `.upper()` if `args.shout`) and return `[message] * args.times`.",
            "solution": (
                "import argparse\n\n\n"
                "def build_parser():\n"
                "    parser = argparse.ArgumentParser()\n"
                '    parser.add_argument("name")\n'
                '    parser.add_argument("--shout", action="store_true")\n'
                '    parser.add_argument("--times", type=int, default=1)\n'
                "    return parser\n\n\n"
                "def greet(args):\n"
                '    message = f"Hello, {args.name}!"\n'
                "    if args.shout:\n"
                "        message = message.upper()\n"
                "    return [message] * args.times\n"
            ),
            "check": """\
parser = build_parser()
assert greet(parser.parse_args(["ada"])) == ["Hello, ada!"], f"got {greet(parser.parse_args(['ada']))!r}"
assert greet(parser.parse_args(["ada", "--shout"])) == ["HELLO, ADA!"], f"got {greet(parser.parse_args(['ada', '--shout']))!r}"
assert greet(parser.parse_args(["ada", "--times", "3"])) == ["Hello, ada!"] * 3, "the --times value should repeat the message."
combo = parser.parse_args(["ada", "--shout", "--times", "2"])
assert greet(combo) == ["HELLO, ADA!"] * 2, f"got {greet(combo)!r}"
default_args = parser.parse_args(["bob"])
assert default_args.times == 1 and default_args.shout is False, "--times should default to 1 and --shout to False."
""",
        },
    },
    # ------------------------------------------------------------------ app-structure
    {
        "id": "app-structure",
        "title": "Config Files & Logging",
        "summary": "Keep settings out of your code, and replace scattered print() calls with real logging.",
        "blocks": [
            p(
                "Real projects are more than one file (you've already split code across files in **Your Own Modules**). "
                "The next ingredients are settings that don't belong baked into code, and messages that explain what "
                "a program is doing while it runs."
            ),
            h("Configuration files"),
            p("Hard-coding settings means changing code every time they change. A config file keeps them separate. `configparser` reads the familiar `[section]` / `key = value` format used by many real tools."),
            code(
                """\
import configparser

with open("app.ini", "w") as file:
    file.write('''[app]
name = Python Academy
debug = yes
max_retries = 3
''')

config = configparser.ConfigParser()
config.read("app.ini")

print(config["app"]["name"])
print(config.getboolean("app", "debug"))
print(config.getint("app", "max_retries"))"""
            ),
            out(
                """\
Python Academy
True
3"""
            ),
            p("`getboolean`/`getint`/`getfloat` convert the text for you, and understand common spellings like `yes`/`no` and `on`/`off`."),
            h("Logging instead of print"),
            p("`print()` is fine for a small script. A real tool needs to say **how important** each message is, and let the person running it choose what to see. That's what the `logging` module is for."),
            code(
                """\
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

logging.debug("Loaded config (hidden: below INFO level)")
logging.info("Starting up")
logging.warning("Config file is missing max_retries; using the default")
logging.error("Could not reach the server")"""
            ),
            out(
                """\
INFO: Starting up
WARNING: Config file is missing max_retries; using the default
ERROR: Could not reach the server"""
            ),
            sec("Logging lets you turn on detailed **DEBUG** output only while investigating an incident, without editing code or drowning normal operation in noise."),
            h("Levels, low to high"),
            items(
                "`DEBUG` — detailed diagnostic information, usually hidden",
                "`INFO` — a normal event worth a record",
                "`WARNING` — something unexpected, but the program continues",
                "`ERROR` — a real problem: something failed",
                "`CRITICAL` — the program probably can't continue",
            ),
            tip("Call `logging.basicConfig(level=...)` once, near the start of your program, then use `logging.info(...)`, `logging.warning(...)` and so on everywhere else."),
            warn("`basicConfig()` only takes effect the **first** time it's called in a running program; calling it again does nothing by default. Real tools call it exactly once, right at startup."),
        ],
        "exercise": {
            "prompt": (
                "Write `parse_settings(ini_text)`. It reads the `[app]` section of the given INI text and returns a dictionary "
                "`{\"debug\": <bool>, \"retries\": <int>}` from its `debug` and `retries` keys. Then write `log_level(settings)`, "
                "returning `logging.DEBUG` when `settings[\"debug\"]` is true, otherwise `logging.INFO`."
            ),
            "starter": "import configparser\nimport logging\n\n\ndef parse_settings(ini_text):\n    pass\n\n\ndef log_level(settings):\n    pass\n",
            "hint": "`configparser.ConfigParser().read_string(ini_text)`, then `parser.getboolean(\"app\", \"debug\")` and `parser.getint(\"app\", \"retries\")`.",
            "solution": (
                "import configparser\nimport logging\n\n\n"
                "def parse_settings(ini_text):\n"
                "    parser = configparser.ConfigParser()\n"
                "    parser.read_string(ini_text)\n"
                "    return {\n"
                '        "debug": parser.getboolean("app", "debug"),\n'
                '        "retries": parser.getint("app", "retries"),\n'
                "    }\n\n\n"
                "def log_level(settings):\n"
                '    return logging.DEBUG if settings["debug"] else logging.INFO\n'
            ),
            "check": """\
settings = parse_settings("[app]\\ndebug = yes\\nretries = 5\\n")
assert settings == {"debug": True, "retries": 5}, f"got {settings!r}"
assert log_level(settings) == logging.DEBUG, "debug=yes should give logging.DEBUG."
settings2 = parse_settings("[app]\\ndebug = no\\nretries = 2\\n")
assert settings2 == {"debug": False, "retries": 2}, f"got {settings2!r}"
assert log_level(settings2) == logging.INFO, "debug=no should give logging.INFO."
""",
        },
    },
    # ------------------------------------------------------------------ testing
    {
        "id": "testing",
        "title": "Testing Your Code",
        "summary": "Write automated tests with unittest instead of checking things by hand.",
        "blocks": [
            p(
                "Running a program by hand to see if it still works doesn't scale, and it's easy to forget a case. An "
                "**automated test** checks your code for you, every time, in a fraction of a second. Python's built-in "
                "`unittest` module is one way to write them."
            ),
            code(
                """\
import io
import unittest


def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


class DivideTests(unittest.TestCase):
    def test_normal_division(self):
        self.assertEqual(divide(10, 2), 5)

    def test_division_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide(1, 0)


suite = unittest.TestLoader().loadTestsFromTestCase(DivideTests)
result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
print("Ran", result.testsRun, "tests")
print("All passed:", result.wasSuccessful())"""
            ),
            out(
                """\
Ran 2 tests
All passed: True"""
            ),
            p(
                "A test class inherits from `unittest.TestCase`. Each method starting with `test_` is one test. "
                "`assertEqual` checks a value; `assertRaises` checks that the right error happens. `TextTestRunner` "
                "runs every test and reports the result (its usual, chatty report goes to a throwaway `io.StringIO()` "
                "here so this example prints a short summary instead)."
            ),
            h("A failing test"),
            code(
                """\
import io
import unittest


class MathTests(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)

    def test_broken(self):
        self.assertEqual(2 + 2, 5)      # deliberately wrong, to see a failure


suite = unittest.TestLoader().loadTestsFromTestCase(MathTests)
result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)

print("Ran", result.testsRun, "tests,", len(result.failures), "failed")
for test, _ in result.failures:
    print("FAILED:", test)"""
            ),
            out(
                """\
Ran 2 tests, 1 failed
FAILED: test_broken (__main__.MathTests.test_broken)"""
            ),
            p("The full failure also includes exactly which line and value were wrong (left out here for brevity); on your own computer, `python -m unittest -v` prints all of that directly to your terminal."),
            sec(
                "Tests turn \"I think this works\" into \"I proved it works, and I'll know immediately if I ever break "
                "it.\" Validators, parsers and crypto helpers deserve tests most of all: a subtle bug there is a vulnerability."
            ),
            tip("Write a test for the normal case, a test for an edge case (empty input, zero, the boundary of a range), and a test for the error case. That combination catches most bugs."),
        ],
        "exercise": {
            "prompt": (
                "Write `is_strong_password(password)`: it returns `True` only when the password is **at least 10 "
                "characters**, contains **a digit**, and contains an **uppercase letter**. Then write the class "
                "`PasswordTests(unittest.TestCase)` with at least three `test_` methods that check your function "
                "(a password that should pass, and at least two that should fail, for different reasons)."
            ),
            "starter": "import unittest\n\n\ndef is_strong_password(password):\n    pass\n\n\nclass PasswordTests(unittest.TestCase):\n    pass  # write at least 3 test_ methods\n",
            "hint": "`len(password) >= 10 and any(c.isdigit() for c in password) and any(c.isupper() for c in password)`. In the tests, call `self.assertTrue(...)` or `self.assertFalse(...)` on `is_strong_password(...)`.",
            "solution": (
                "import unittest\n\n\n"
                "def is_strong_password(password):\n"
                "    return (\n"
                "        len(password) >= 10\n"
                "        and any(char.isdigit() for char in password)\n"
                "        and any(char.isupper() for char in password)\n"
                "    )\n\n\n"
                "class PasswordTests(unittest.TestCase):\n"
                "    def test_strong_password_passes(self):\n"
                '        self.assertTrue(is_strong_password("Hunter2024"))\n\n'
                "    def test_short_password_fails(self):\n"
                '        self.assertFalse(is_strong_password("Ab1"))\n\n'
                "    def test_password_without_a_digit_fails(self):\n"
                '        self.assertFalse(is_strong_password("NoDigitsHere"))\n'
            ),
            "check": """\
import io
assert is_strong_password("Hunter2024") is True, "A 10+ character password with a digit and an uppercase letter should be strong."
assert is_strong_password("weak") is False, "A short password must not be strong."
assert is_strong_password("nodigitshere") is False, "A password without any digit must not be strong."
assert is_strong_password("alllowercase1") is False, "A password without any uppercase letter must not be strong."
method_names = [name for name in dir(PasswordTests) if name.startswith("test_")]
assert len(method_names) >= 3, f"PasswordTests should have at least 3 test_ methods, found {len(method_names)}."
suite = unittest.TestLoader().loadTestsFromTestCase(PasswordTests)
result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
assert result.wasSuccessful(), f"Your own tests should pass against your own function ({len(result.failures)} failed, {len(result.errors)} errored)."
""",
        },
    },
    # ------------------------------------------------------------------ gui-concepts
    {
        "id": "gui-concepts",
        "title": "GUI Concepts: Events & Widgets",
        "summary": "The ideas behind every graphical app: widgets, callbacks and state — simulated here, real on your computer.",
        "blocks": [
            p(
                "A GUI app — a window with buttons you click — is built in Python the same way as any other program: "
                "with a library. This in-browser sandbox intentionally has no real screen to draw on, so a real window "
                "can't open here. But the **ideas** behind every GUI toolkit — widgets, events, callbacks and state — "
                "are exactly the same whether the widgets are real or, as here, simulated in text. Everything in this "
                "lesson transfers directly to `tkinter`, PyQt, or any other GUI you build on your own computer."
            ),
            warn("This sandbox has no display, so no real window can open here. A real, runnable `tkinter` example is at the end of this lesson, to try on your own computer."),
            h("The event loop idea"),
            p(
                "A GUI program doesn't run top to bottom like the scripts you've written. It sits and waits for "
                "**events** (a click, a key press) and calls the function you registered for that event: a **callback**."
            ),
            code(
                """\
class Button:
    def __init__(self, label):
        self.label = label
        self._on_click = None

    def on_click(self, callback):
        self._on_click = callback

    def click(self):          # a real toolkit calls this itself when the mouse is pressed
        if self._on_click:
            self._on_click()


count = 0
button = Button("Add one")

def handle_click():
    global count
    count += 1
    print(f"{button.label} clicked -> count is now {count}")

button.on_click(handle_click)

button.click()
button.click()
button.click()"""
            ),
            out(
                """\
Add one clicked -> count is now 1
Add one clicked -> count is now 2
Add one clicked -> count is now 3"""
            ),
            h("Widgets and shared state"),
            p("A small app is usually a class holding its widgets and its state together, with callbacks as its own methods."),
            code(
                """\
class Label:
    def __init__(self, text=""):
        self.text = text

    def render(self):
        print(f"[Label] {self.text}")


class Button:
    def __init__(self, label):
        self.label = label
        self._on_click = None

    def on_click(self, callback):
        self._on_click = callback

    def click(self):
        if self._on_click:
            self._on_click()


class CounterApp:
    def __init__(self):
        self.count = 0
        self.label = Label("Count: 0")
        self.button = Button("+1")
        self.button.on_click(self.increment)

    def increment(self):
        self.count += 1
        self.label.text = f"Count: {self.count}"
        self.label.render()


app = CounterApp()
app.button.click()
app.button.click()"""
            ),
            out(
                """\
[Label] Count: 1
[Label] Count: 2"""
            ),
            sec(
                "**A text field's content is still untrusted input**, just like a function argument or a CLI flag. "
                "Validate it the same way: convert inside a `try`/`except`, never with `eval()`."
            ),
            code(
                """\
class TextInput:
    def __init__(self):
        self.value = ""

    def type(self, text):     # simulates the user typing
        self.value += text


class Label:
    def __init__(self, text=""):
        self.text = text


class Form:
    def __init__(self):
        self.age_input = TextInput()
        self.message = Label()

    def submit(self):
        try:
            age = int(self.age_input.value)
        except ValueError:
            self.message.text = "Please enter a whole number"
            return
        if not 0 <= age <= 120:
            self.message.text = "That doesn't look like a real age"
            return
        self.message.text = f"Thanks, you are {age} years old"


form = Form()
form.age_input.type("thirty")
form.submit()
print(form.message.text)

form2 = Form()
form2.age_input.type("30")
form2.submit()
print(form2.message.text)"""
            ),
            out(
                """\
Please enter a whole number
Thanks, you are 30 years old"""
            ),
            h("The real thing: tkinter"),
            p("`tkinter` ships with Python already, so `python my_app.py` runs it with nothing extra to install. Compare it with `CounterApp` above: same shape, a real window."),
            example(
                """\
import tkinter as tk


def increment():
    global count
    count += 1
    label.config(text=f"Count: {count}")


count = 0
root = tk.Tk()
root.title("Counter")

label = tk.Label(root, text="Count: 0")
label.pack()

button = tk.Button(root, text="+1", command=increment)
button.pack()

root.mainloop()   # the REAL event loop: it waits here, calling your callbacks, until the window closes"""
            ),
            p("A widget (`Button`), a callback (`increment`), and state (`count`, the label's text) updated inside it: the same three ideas as the simulation above. For richer apps look at PyQt/PySide or Kivy, or, for the web, a framework like Flask serving HTML forms instead of widgets."),
        ],
        "exercise": {
            "prompt": (
                "Widgets (`Label`, `TextInput`, `Button`) are provided. Build `LoginForm`. `__init__` creates "
                "`self.username_input`, `self.password_input` (both `TextInput`), `self.message` (a `Label`, starting "
                "text `\"\"`), and `self.submit_button` (a `Button`), wired so clicking it calls `self.try_login`. "
                "`try_login` sets `self.message.text` to `\"Fields cannot be empty\"` if the username or password is "
                "empty; otherwise `\"Password is too short\"` if the password is under 8 characters; otherwise "
                "`f\"Welcome, {username}!\"`."
            ),
            "starter": (
                "class Label:\n    def __init__(self, text=\"\"):\n        self.text = text\n\n\n"
                "class TextInput:\n    def __init__(self):\n        self.value = \"\"\n\n"
                "    def type(self, text):\n        self.value += text\n\n\n"
                "class Button:\n    def __init__(self):\n        self._on_click = None\n\n"
                "    def on_click(self, callback):\n        self._on_click = callback\n\n"
                "    def click(self):\n        if self._on_click:\n            self._on_click()\n\n\n"
                "class LoginForm:\n    def __init__(self):\n        pass  # create the widgets described above\n\n"
                "    def try_login(self):\n        pass  # fill in the validation rules described in the prompt\n"
            ),
            "hint": "In `__init__`, create the four attributes and call `self.submit_button.on_click(self.try_login)`. In `try_login`, read `self.username_input.value` and `self.password_input.value` first, then check them in order: empty, then short, then success.",
            "solution": (
                "class Label:\n    def __init__(self, text=\"\"):\n        self.text = text\n\n\n"
                "class TextInput:\n    def __init__(self):\n        self.value = \"\"\n\n"
                "    def type(self, text):\n        self.value += text\n\n\n"
                "class Button:\n    def __init__(self):\n        self._on_click = None\n\n"
                "    def on_click(self, callback):\n        self._on_click = callback\n\n"
                "    def click(self):\n        if self._on_click:\n            self._on_click()\n\n\n"
                "class LoginForm:\n"
                "    def __init__(self):\n"
                "        self.username_input = TextInput()\n"
                "        self.password_input = TextInput()\n"
                "        self.message = Label()\n"
                "        self.submit_button = Button()\n"
                "        self.submit_button.on_click(self.try_login)\n\n"
                "    def try_login(self):\n"
                "        username = self.username_input.value\n"
                "        password = self.password_input.value\n"
                "        if not username or not password:\n"
                '            self.message.text = "Fields cannot be empty"\n'
                "        elif len(password) < 8:\n"
                '            self.message.text = "Password is too short"\n'
                "        else:\n"
                '            self.message.text = f"Welcome, {username}!"\n'
            ),
            "check": """\
form = LoginForm()
form.submit_button.click()
assert form.message.text == "Fields cannot be empty", f"Empty fields should give 'Fields cannot be empty' but got {form.message.text!r}."
form2 = LoginForm()
form2.username_input.type("ada")
form2.submit_button.click()
assert form2.message.text == "Fields cannot be empty", "A missing password should still count as empty fields."
form3 = LoginForm()
form3.username_input.type("ada")
form3.password_input.type("short")
form3.submit_button.click()
assert form3.message.text == "Password is too short", f"A password under 8 characters should be rejected, got {form3.message.text!r}."
form4 = LoginForm()
form4.username_input.type("ada")
form4.password_input.type("longenoughpassword")
form4.submit_button.click()
assert form4.message.text == "Welcome, ada!", f"Expected 'Welcome, ada!' but got {form4.message.text!r}."
assert isinstance(form4.submit_button, Button) and isinstance(form4.username_input, TextInput), "Use the provided widget classes."
""",
        },
    },
    # ------------------------------------------------------------------ security-toolkit
    {
        "id": "security-toolkit",
        "title": "Capstone: An Interactive Security Toolkit",
        "summary": "Build a full command-driven app: classes, hashing and a dispatch loop, tied together.",
        "blocks": [
            p(
                "This capstone pulls together classes, hashing and command handling into one small tool: the shape "
                "every larger program takes, pieces that each do one job, combined behind a simple interface."
            ),
            h("The dispatch pattern"),
            p("A command-driven program reads a line, decides which piece of code should handle it, and calls it. A dictionary of handlers is a clean way to do that."),
            code(
                """\
def cmd_double(argument):
    return int(argument) * 2

def cmd_upper(argument):
    return argument.upper()

handlers = {"double": cmd_double, "upper": cmd_upper}

def dispatch(line):
    command, _, rest = line.partition(" ")
    handler = handlers.get(command)
    if handler is None:
        return f"Unknown command: {command}"
    return handler(rest)

for line in ["double 21", "upper hello", "delete everything"]:
    print(dispatch(line))"""
            ),
            out(
                """\
42
HELLO
Unknown command: delete"""
            ),
            sec(
                "A dictionary (or `if`/`elif` chain) that only runs code you explicitly registered is another "
                "**allow-list**: nothing outside the known commands can execute, so a typo or a hostile command name "
                "is simply rejected instead of doing something unexpected."
            ),
            h("Putting it together: a real interactive app"),
            p(
                "Your turn: build `Toolkit`, an object that remembers a log of what it has done, an audit trail like "
                "the `AuditLog` from the Integrity lesson, and exposes a couple of operations. Then wrap it in a loop "
                "that reads a command and dispatches it, the same idea behind `git`'s subcommands or the menu of any "
                "interactive program. Type commands into the Input box below, one per line, exactly like a real terminal session."
            ),
            tip("A class holding state and behaviour, plus a small loop turning typed commands into method calls, is the skeleton of countless real tools: package managers, deployment scripts, chat bots, database shells."),
        ],
        "exercise": {
            "prompt": (
                "Finish `Toolkit`. It starts with `self.log = []`. `check_password(password)` returns `\"strong\"` if the "
                "password is at least 10 characters **and** has a digit **and** has an uppercase letter, otherwise "
                "`\"weak\"`; either way it appends `f\"checked password: {result}\"` to the log. `hash_text(text)` returns "
                "`hashlib.sha256(text.encode()).hexdigest()` and appends `\"hashed text\"` to the log. `history()` returns "
                "a **copy** of the log, never the original list. Then finish `main()`'s loop: on `\"password <text>\"` print "
                "`check_password(...)`; on `\"hash <text>\"` print `hash_text(...)`; on `\"history\"` print the log joined "
                "with `\", \"`; on `\"quit\"` print `\"Goodbye!\"` and stop; otherwise print `f\"Unknown command: {command}\"`."
            ),
            "starter": (
                "import hashlib\n\n\n"
                "class Toolkit:\n"
                "    def __init__(self):\n        self.log = []\n\n"
                "    def check_password(self, password):\n        pass\n\n"
                "    def hash_text(self, text):\n        pass\n\n"
                "    def history(self):\n        pass\n\n\n"
                "def main():\n"
                "    toolkit = Toolkit()\n"
                "    while True:\n"
                "        line = input()\n"
                '        command, _, rest = line.partition(" ")\n'
                "        # fill in the command handling described in the prompt\n\n\n"
                "main()\n"
            ),
            "hint": "check_password: `len(password) >= 10 and any(c.isdigit() for c in password) and any(c.isupper() for c in password)`, then `self.log.append(...)`. hash_text: `hashlib.sha256(text.encode()).hexdigest()`. history: `return list(self.log)`. In main's loop, use `if command == \"password\": print(toolkit.check_password(rest))`, and so on; `break` after printing \"Goodbye!\".",
            "solution": (
                "import hashlib\n\n\n"
                "class Toolkit:\n"
                "    def __init__(self):\n"
                "        self.log = []\n\n"
                "    def check_password(self, password):\n"
                "        strong = (\n"
                "            len(password) >= 10\n"
                "            and any(char.isdigit() for char in password)\n"
                "            and any(char.isupper() for char in password)\n"
                "        )\n"
                '        result = "strong" if strong else "weak"\n'
                '        self.log.append(f"checked password: {result}")\n'
                "        return result\n\n"
                "    def hash_text(self, text):\n"
                "        digest = hashlib.sha256(text.encode()).hexdigest()\n"
                '        self.log.append("hashed text")\n'
                "        return digest\n\n"
                "    def history(self):\n"
                "        return list(self.log)\n\n\n"
                "def main():\n"
                "    toolkit = Toolkit()\n"
                "    while True:\n"
                "        line = input()\n"
                '        command, _, rest = line.partition(" ")\n'
                '        if command == "quit":\n'
                '            print("Goodbye!")\n'
                "            break\n"
                '        elif command == "password":\n'
                "            print(toolkit.check_password(rest))\n"
                '        elif command == "hash":\n'
                "            print(toolkit.hash_text(rest))\n"
                '        elif command == "history":\n'
                '            print(", ".join(toolkit.history()))\n'
                "        else:\n"
                '            print(f"Unknown command: {command}")\n\n\n'
                "main()\n"
            ),
            "stdin": "password Hunter2024\nhash hello\nhistory\nquit",
            "check": """\
def run(commands):
    return run_again("\\n".join(commands))

out1 = run(["password Hunter2024", "quit"])
assert out1.splitlines() == ["strong", "Goodbye!"], f"Expected ['strong', 'Goodbye!'] but got {out1.splitlines()!r}."

out2 = run(["password weak", "quit"])
assert out2.splitlines() == ["weak", "Goodbye!"], f"'weak' (4 characters) should be reported as weak, got {out2.splitlines()!r}."

out3 = run(["hash hello", "quit"])
assert out3.splitlines()[0] == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824", f"hash_text('hello') should be the real sha256 hex digest, got {out3.splitlines()[0]!r}."

out4 = run(["password Hunter2024", "hash hello", "history", "quit"])
lines = out4.splitlines()
assert lines[0] == "strong", f"got {lines!r}"
assert lines[2] == "checked password: strong, hashed text", f"history() should be joined with ', ' but got {lines[2]!r}."

out5 = run(["unknown-thing", "quit"])
assert out5.splitlines()[0] == "Unknown command: unknown-thing", f"got {out5.splitlines()[0]!r}"

toolkit = Toolkit()
toolkit.check_password("Hunter2024")
copy = toolkit.history()
copy.append("forged")
assert toolkit.history() == ["checked password: strong"], "history() must return a copy so callers cannot tamper with the real log."

assert Toolkit().check_password("nodigitshere") == "weak", "A password without a digit should be weak even if long."
assert Toolkit().check_password("short1A") == "weak", "A password under 10 characters should be weak."
""",
        },
    },
]
