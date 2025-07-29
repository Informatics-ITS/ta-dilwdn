from PIL import Image
import pytesseract
import re
from anytree import Node, RenderTree

pytesseract.pytesseract.tesseract_cmd = r'E:\Program Files\Tesseract-OCR\tesseract.exe'
im = Image.open("perkalian 8.png")

text = pytesseract.image_to_string(im, lang = 'eng')
text = text.strip()
print(text)
numbers = []
numbers=re.findall('\d+', text)
operator = ''.join([i for i in text if not i.isdigit()])
print(numbers)
print(operator[0])

#class Node:
#    def __init__(self, data):
#        self.left = None
#        self.right = None
#        self.data = data

#root = Node(operator[0])

#root.left = Node(numbers[0])
#root.right = Node(numbers[1])
num=[7,9,63]
nilai = 0
print("Tree 1")
root = Node(operator[0])

level_1_child_11 = Node(num[0], parent=root)
level_1_child_21 = Node(num[1], parent=root)
#level_2_child_1 = Node(45, parent=level_1_child_1)
#level_2_child_2 = Node(50, parent=level_1_child_2)

for pre, fill, node in RenderTree(root):
    print("%s%s" % (pre, node.name))
print("Jawaban:"+str(num[2]))
print("\n")
print("Tree 2")
operatordua = '*'
root2 = Node(operatordua)

level_1_child_12 = Node(numbers[0], parent=root2)
level_1_child_22 = Node(numbers[1], parent=root2)
#level_2_child_1 = Node(45, parent=level_1_child_1)
#level_2_child_2 = Node(50, parent=level_1_child_2)

for pre, fill, node in RenderTree(root2):
    print("%s%s" % (pre, node.name))
jawabandua = 56
print("Jawaban:"+str(jawabandua))
print("\n")
if (int(num[0])==int(numbers[0])):
	nilai=nilai+25
	print("Child 1 benar\n")
else:
	print("Child 1 salah\n")
if (int(num[1])==int(numbers[1])):
	nilai=nilai+25
	print("Child 2 benar\n")
else:
	print("Child 2 salah\n")
if (operator[0]==operatordua):
	nilai=nilai+25
	print("Operator benar\n")
else:
	print("Operator salah\n")
if (int(numbers[2])==int(jawabandua)):
	nilai=nilai+25
	print("Jawaban benar\n")
else:
	print("Jawaban salah\n")

print("Nilai : "+str(nilai))

