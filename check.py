#find the second largest
numbers = [10, 25, 7, 42, 18]
largest=float('-inf')
second_largset=float('-inf')
for i in numbers:
    if i>largest:
        second_largset=largest
        largest=i
    elif i>second_largset:
        second_largset=i
print(second_largset)