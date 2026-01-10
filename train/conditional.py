# If/Else conditions are used to decide to do something based on something being true or false

x = 10
y = 5

# Comparisons Operators (==, !=, >, <, >=, <=)  --> Used to compare values

# simple if
if x>y:
    print(f"{x} is greater than {y}")

# if/Else
    
a = 10
b = 10

if a>b:
    print(f"{a} is greater than {b}")
else:
    print(f"{a} is smaller than {b}")

# Eljif
    
m = 2
v = 2

if m>v:
    print(f"{m} is greater than {v}")
elif m == v:
    print(f"{m} is equal to {v}")
else:
    print(f"{m} is smaller than {v}")

# Nested if

h = 6

if h > 2:
    if h <= 10:
        print(f"{h} is greater than 2 and less than or equal to 10")

# Logical Operators (and , or, not) --> Used to combine conditional statements

j = 7

# and
if j > 2 and j <=10:
    print(f"{j} is greater than 2 and less than or equal to 10")
# or
if j > 2 or j <=10:
    print(f"{j} is greater than 2 or equal and less than 10")
# not
if not (j == a):
    print(f"{j} is not equal to {a}")


# Membership operators (in, not in) - Membership Operators are used to test if a sequence is presented in a object


m=10
o=2
numbers=[1,2,3,4,5,6,7,8,9]

# in
if o in numbers:
    print(f"{o} is in the list")

# not in
if m not in numbers:
    print(f"{m} is not in the list")

# Identity Operator (is, is not) - Compare the objects not if they are equal but if they are actually the same object
# memory location

e=1
u=2
r=1

# is
if e is r:
    print(f'{e} is equal to {r}')

# is not
if e is not u:
    print(f'{e} is not equal to {u}')