# untions is a block of code , in python curly brackets , we use indentations with tabs or spaces

# Create funtions

def sayHello(name):
    print(f'Hello {name}')

sayHello('Joe')

# Return Values
def getSum(num1,num2):
    total=num1+num2
    return(total)

num = getSum(4,3)
print(num)

# Single line coding using lambda
addSum = lambda num1,num2 : num1+num2

num3 = addSum(2,6)
print(num3)