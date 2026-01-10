import os,sys

# num = input("Enter a number: ")
# print(num)

# folders = input("Please provide list of folder names with space in between: ").split()
#
# for folder in folders:
#     try:
#         files = os.listdir(folder)
#         print("=== listing files for the folder - ", folder)
#         # print(files)
#         print("\n".join(files))
#     except:
#         print("Please provide the valid folder name", folder)
#         # break
    
# num1 = len(sys.argv[1])
# num2 = len(sys.argv[2])
# try:
#     div =num1/num2
#     print(div) # python input.py test bye
# except ZeroDivisionError:
#     print("Do not try to divide by 0")

def list_files (files):
    try:
        file = os.listdir(files)
        return file, None
    except FileExistsError:
        return None, "File not found"
    except PermissionError:
        return None, "Permission denied"

def main():
    path =input("Enter the folder path which starts with / : ").split()

    for folder in path:
        files, error_message = list_files(folder)
        if files:
            print(f"Files in {folder}:\n" + "\n".join(files))
        else:
            print(f"Error in {folder}: {error_message}")

if __name__ == "__main__":
    main()

