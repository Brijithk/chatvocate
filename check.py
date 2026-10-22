#find the largest number
numbers=[5,4,3,2,110]
highest_number=float('-inf')
for i in numbers:
    if i>highest_number:
        highest_number=i
if highest_number==float('-inf'):
    print("No number exist")
else:
    print(highest_number)