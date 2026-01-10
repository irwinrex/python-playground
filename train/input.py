import os

# num = input("Enter a number: ")
# print(num)

folders = input("Please provide list of folder names with space in between: ").split()

for folder in folders:
    files = os.listdir(folder)
    print(files)
