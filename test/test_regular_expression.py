import re

text = 'bs.d_np_r'

list1 = re.findall(r'(.*)\.(.*)', text)

print(list1)