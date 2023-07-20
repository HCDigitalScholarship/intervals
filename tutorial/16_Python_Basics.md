# Python Basics

## Introduction
In Python, like other programming languages, we declare **variables**, then use **functions** transform them in various ways.  There are functions (and libraries) that help us work with numbers, text, statistics, graphs, etc.

Read more about [Python with w3school reference guide](https://www.w3schools.com/python/python_intro.asp)


---


## Data Types
It's important to understand **data types**:

*   **integer**:  any whole number, such as 1, 2, 10

*   **float**:  decimal numbers, such as 2.25, 6.875

*   **string**:   any alpha-numeric character, surrounded by quotation marks (double or single)
*   **Boolean**:  True or False (in fact these are reserved words in Python and should not be used beyond Boolean functions)

---
## Collections

These can also be combined as various kind of **collections**:

*   **lists**:  an ordered sequence presented in brackets and separated by commas, such as **["Blues", "Gospel", "Country"]** or **[1.0, 4.0, 6.0]**.  Lists can contain duplicates
*   **set**:  an unordered sequence; it cannot contain duplicates
*   **tuples**: a special kind of list that cannot be altered, presented as **("Jazz", "Classical", "Folk")** or **(1.25, 4.76, 8.03)**

*   **dictionaries**:  a series of **key : value** pairs contained within braces, such as **{"artist" : "McCartney, Paul", "title" : "Yesterday"}**

Read more about [Python data types at the w3schools resource](https://www.w3schools.com/python/python_datatypes.asp)

---

## Checking Data Types

Check the **data type** of any item:

`type(item)`


    item_1 = 'guitar'
    item_2 = 1
    item_3 = 2.25
    item_4 = True
    item_5 = ["Blues", "Gospel", "Country", 4] 
    item_6 = ("Jazz", "Classical", "Folk")
    item_7 = {"artist_surname" : "McCartney", "artist_given_name" : "Paul", "title" : "Yesterday"}
Note that simply defining a variable does not produce any output. 
If you want to see the value of a variable, you can print it:

    print(my_variable)

or just write it as the last line in the cell:

    my_variable

---
## Numbers, Strings, Floats, and Booleans
Depending on the data type, it's possible to perform various **operations** on them.

* You **can** add/subtract **integers** and **floats** to each other
* You **cannot** add an **integer** to **text or a Boolean**
* Many other kinds of operators can be used to compare items, test for thresholds, etc.  

**Integers** and **floats** can be used with various mathematical tests:

```
Equals: a == b
Not Equals: a != b
Less than: a < b
Less than or equal to: a <= b
Greater than: a > b
Greater than or equal to: a >= b
```


Read about [operators at the w3school site](https://www.w3schools.com/python/python_operators.asp)


**Strings** are text.  There are a wide variety of built-in methods that allow to you to work with them to:

* change lower/upper case
* strip out certain characters (like punctuation)
* split texts (at spaces, for example)
* find substrings, or first/last characters
* etc!

See more [about strings at w3schools](https://www.w3schools.com/python/python_strings_methods.asp).



## Collections:  Lists, Dictionaries, Sets, and Tuples

In Python, items gathered together are called a **collection**. There are four types, each with its own properties: 

* **Lists** are used to store an **ordered sequence of  items** in a single variable.  Each item is surrounded by quotation marks, separated by a comma from the next. Square brackets surround the whole.  The example below is a list of strings (note the quotation marks). See [about lists at w3schools](https://www.w3schools.com/python/python_lists.asp).

```
list_of_genres =  ["Blues", "Gospel", "Country", "Hip-Hop"] 
```

* **Sets** are like lists, but are **not ordered**, and cannot contain duplicates. See more [about sets at w3schools](https://www.w3schools.com/python/python_sets.asp).

```
set(list_of_genres)
{'Blues', 'Country', 'Gospel', 'Hip-Hop'}

```
Turn a set back into a list:  

```
list(set(list_of_genres)
```
---
* **Dictionaries** are used to store data values in **key:value pairs**. Like lists, they are ordered. But like sets they do not allow duplicates. Each key or value is surrounded by quotation marks. Each key:value pair is followed by a comma. Curly brackets surround the whole. Dictionaries can also contain other dictionaries, as 'nested' dictionaries. See more [about dictionaries at w3schools,](https://www.w3schools.com/python/python_dictionaries.asp) and below.

>    In this example the **keys** and **values** are both strings.  But we could also restrict certain data types.  For instance, we could insist that the `date` value be that specific data type (and not just a string).

```
my_dict = {"artist_first_name" : "Wolfgang Amadeus",
"artist_last_name" : "Mozart",
"work_title" : "The Magic Flute",
"work_genre" : "singspiel",
"date" : "1791",
"first_performance_place" : "Vienna"}
```

* **Tuples** are a special type of collection:  ordered (like lists), but unchangeable (it is not possible to add or remove items). See more [about tuples at w3schools](https://www.w3schools.com/python/python_tuples.asp). 



---

## Working with Lists
In the case of lists, we often need to:
* **Add or remove items**, as in `my_list.append(another_item)` or `my_list.remove(some_item)`
* Find out **how many items** are in a list (that is, the "length"), such as `len(my_list)`
* Find the **unique items** in a list (that is, the "set"), such as `set(my_list)`.
* Find **how many unique items** there are in a given list, which is the "length" of the "set": `len(set(my_list))`.  Note the nested parentheses!
* Find particular **items by their index** (= position in the list): `my_list[0]` (remember that the index of first position is always "0").  The last item in a list is `my_list[-1]` (a "negative index" counts back from the end, starting with "-1").
* Find the **index (= position)** of a particular item: `my_list.index(item_name)`.  This will return a value, rather than the item in question.
* **Sort** the list: ``my_list.sort()``, or in reverse alphabetical order: ``my_list.sort(reverse = True)``

**Note** that there are many other ways to work with lists, including methods for find a **range** of items ("the first 10 items", "every other item", "all but the first and last items").

**Note** that some methods modify a list but don't show you the result. In order to see the modification, output the new list by just typing the name of the list again.  It can be confusing!

Read more about [working with **Lists** at w3schools](https://www.w3schools.com/python/python_lists.asp)

[Try them out with list exercises.](https://www.w3schools.com/python/python_lists_exercises.asp)

[Read about the list methods.](https://www.w3schools.com/python/python_lists_methods.asp)

---

## Working with Dictionaries
You can think of a dictionary like a small catalog, with a series of unique "keys" and their associated "values", like:

```
my_dict = {"artist_first_name" : "Wolfgang Amadeus",
"artist_last_name" : "Mozart",
"work_title" : "The Magic Flute",
"work_genre" : "singspiel",
"date" : "1791",
"first_performance_place" : "Vienna"}
```
The values can repeat, but the keys in any dictionary must be unique.

There are various ways to:

* list the **keys**:  `my_dict.keys()`
* list the **values**:  `my_dict.values()`
* list all the **items** (both the keys and values): `my_dict.items()`
* list the **value for a particular key**: `my_dict["date"]`
* update the **value for a particular key**: `my_dict["date"] = "1789"`
* add a **key/value pair**:  `my_dict["language"] = "German"
* remove a **key/value pair**: `my_dict.pop("language")

It is also possible to encounter **nested dictionaries**, in which one dictionary contains another.  

**Nested Dictionaries** are ones in which one dictionary contains another.  For example:

For example, this dictionary of works in a concert, each with their own details about composer, title, genre, etc.

```
my_concert = {
    "work_1": {
        "composer_first_name" : "Wolfgang Amadeus",
        "composer_last_name" : "Mozart",     
        "work_title" : "The Magic Flute",
        "work_genre" : "singspiel",
        "date" : "1791",
        "first_performance_place" : "Vienna"},
    "work_2": {
        "composer_first_name" : "Giuseppe",
        "composer_last_name" : "Verdi",     
        "work_title" : "Aïda",
        "work_genre" : "opera",
        "date" : "1871",
        "first_performance_place" : "Cairo"}
```

Access the **top-level key** 'work_1':

```
my_concert['work_1']

```
Access **all the keys nested** within 'work_1':

```
my_concert['work_1'].keys()

```
Access an **individual key nested** within 'work_1':

```
my_concert['work_1']['work_title']
```
**Add a key/value pair** to one item:

```
my_concert['work_1']["librettist"] = 'Schickaneder'
```


[More about dictionaries from w3schools](https://www.w3schools.com/python/python_dictionaries.asp).


---


## "If" Statements

"If" statements allow you to perform **logical tests** on your data, such as:

```
Equals: a == b
Not Equals: a != b
Less than: a < b
Less than or equal to: a <= b
Greater than: a > b
Greater than or equal to: a >= b
```
Examples in "if" statement:

```
if item_value > 10:
  print("high value")
elif item_value > 5:
  print("medium value")
else:  # default case, item_value <= 5
  print("low value")
```

or

```
group_name = "Beatles"
if group_name.startswith("B"):
  print(True)
```
Note that "if" statements can be multi-stage, with **"if"** followed by **"elif"** (another condition to test if the first condition is not met), and **"else"** (a default result if none of the previous tests are true). 

More about "if" statements [here](https://www.w3schools.com/python/python_conditions.asp).


## "For" Loops
"For" loops allow you to iterate over the items in any collection, performing the same operation or function on each.

**Note** loops like are very helpful when working with individual lists or dictionaries.  But you will want to **avoid** attempting to use them directly on a **Pandas column**.  Instead, write the function by "apply" it to that column for all rows in the dataframe.  More about that in Notebook B!


**"if"** statement **within a "for"** loop:

```
genres =  ["Blues", "Gospel", "Country", "Hip-Hop"] 
for genre in genres:
  if genre.startswith("B"):
    print(genre)

```

or to all those that do _not_ satisfy the condition:

```
genres =  ["Blues", "Gospel", "Country", "Hip-Hop"] 
for genre in genres:
  if genre.startswith("B"):
    pass
  else:
    print(genre)
```

Note that **list comprehension** allows you work with lists without the need to create separate **for** loops.  For example:

```
b_list = [x for x in genres if x.startswith("B")]
```

More about **list comprehension** [here](https://www.w3schools.com/python/python_lists_comprehension.asp).


---

## For Loops with Nested Dictionaries

Now create a **nested** dictionary based on the one you made above.  This could be a *series of related items* (like songs on a playlist, or instruments in a collection, or scores on your shelf). The id's (or keys) for each item will need to be unique at the highest level, but the keys within each item can repeat.  

Sample nested dictionary of works on opera season:

```
my_operas = {
    "work_1": {
        "composer_first_name" : "Wolfgang Amadeus",
        "composer_last_name" : "Mozart",     
        "work_title" : "The Magic Flute",
        "work_genre" : "singspiel",
        "date" : "1791",
        "first_performance_place" : "Vienna"},
    "work_2": {
        "composer_first_name" : "Giuseppe",
        "composer_last_name" : "Verdi",     
        "work_title" : "Aïda",
        "work_genre" : "opera",
        "date" : "1871",
        "first_performance_place" : "Cairo"}
```


Then try the following to iterate through each work in the dictionary, and then print the individual key-value pairs for each work:



```
for work_id, work_info in my_concert.items():
    print("\nWork ID:", work_id)
    
    for key in work_info:
        print(key + ':', work_info[key])
```

---
## Functions

Functions are just what they sound like:  a short series of steps that can be applied to 
some data, and **return** various results depending on the logic you apply.

We will take a simple example that can be applied later in our work with Pandas data sets.

Let's imagine that you have a dataset in which a particular column contains data that are inconsistent:  in some places for the name of an artist you have `John Lennon`, and other places `John Lenin`.  You could correct them by hand in a spreadsheet.  But there is an easier way with a Python **function**.


```

def name_check(sample_name):
    if sample_name == "John Lenin":
        print("That should be John Lennon instead")
    else:
        print("It's spelled correctly")
```

So far all we have done is to **define the function** (take note of the ":" signs and of the indentations.  But now we must actually run it with some data.

First on **one** sample name:

```
sample_name = "John Lenin"
name_check(sample_name)
```

Or combined with a **for** loop, we can run this over a list of names:

```
sample_name_list = ["John Lenin", "John Lennon", "John Lenin"]
for sample_name in sample_name_list:
    name_check(sample_name)
```

---


## Sections in this guide

  * [01_Introduction_and_Corpus](01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](02_Notes_Rests.md)
  * [03_Durations](03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](04_TimeSignatures_Beat_Strength.md)
  * [05_DetailIndex](05_DetailIndex.md)
  * [06_MelodicIntervals](06_MelodicIntervals.md)
  * [07_HarmonicIntervals](07_HarmonicIntervals.md)
  * [08_Contrapuntal_Modules](08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](10_Lyrics_Homorhythm.md)
  * [11_Cadences](11_Cadences.md)
  * [12_Presentation_Types](12_Presentation_Types.md)
  * [13_Model_Finder](13_Model_Finder.md)
  * [14_Visualizations_Summary](14_Visualizations_Summary.md)
  * [15_Network_Graphs](15_Network_Graphs.md)
  * [16_Python_Basics](16_Python_Basics.md)
  * [17_Pandas_Basics](17_Pandas_Basics.md)