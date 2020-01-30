def yufa(lst):
    a = []
    b = {'{': '}', '[': ']', '(': ')'}
    for i in lst:
        if i in ['}', ']', ')']:
            c = a.pop()
            if b[c] != i:
                print('括号不匹配')
                return
        elif i in ['{', '[', '(']:
            a.append(i)
    if len(a):
        print('括号不匹配2')
    else:
        print('括号匹配')



class shu():
    def __int__(self, data):
        self.left = None
        self.right = None
        self.data = data

def bianlishu(a):
    print(a.data)
    bianlishu(a.left)
    bianlishu(a.right)

import time
a = time.time()
# time.sleep(5)
b = time.time()
# print(a, end=' ')
# print(b)
# print('%.2f'%(b-a))

def fenzu():
    l = []
    d = []
    for i in range(1,112):
        d.append(i)
        if i == 111:
            l.append(d)
        if len(d) == 3:
            l.append(d)
            d = []

    return l
# print(fenzu())

def wai(a,b):
    def nei(x):
        return a*x+b
    return nei

_list = []



for i in range(3):
    def func(a):
        return i + a
    _list.append(func)
for f in _list:
    print(id(f(1)))
