from forms.classes import FormVar, FormConst, FormWild


__all__ = ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'i', 'j',
           'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
           'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
           'U', 'V', 'W', 'X', 'Y', 'Z',
           'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10']


# Variables are lowercase
a = FormVar('a')
b = FormVar('b')
c = FormVar('c')
d = FormVar('d')
# e = FormVar('e')
f = FormVar('f')
g = FormVar('g')
h = FormVar('h')
i = FormVar('i')
j = FormVar('j')
k = FormVar('k')
l = FormVar('l')
m = FormVar('m')
n = FormVar('n')
o = FormVar('o')
p = FormVar('p')
q = FormVar('q')
r = FormVar('r')
s = FormVar('s')
t = FormVar('t')
u = FormVar('u')
v = FormVar('v')
w = FormVar('w')
x = FormVar('x')
y = FormVar('y')
z = FormVar('z')

# Constants are uppercase
A = FormConst('A')
B = FormConst('B')
C = FormConst('C')
D = FormConst('D')
E = FormConst('E')
F = FormConst('F')
G = FormConst('G')
H = FormConst('H')
I = FormConst('I')
J = FormConst('J')
K = FormConst('K')
L = FormConst('L')
M = FormConst('M')
N = FormConst('N')
O = FormConst('O')
P = FormConst('P')
Q = FormConst('Q')
R = FormConst('R')
S = FormConst('S')
T = FormConst('T')
U = FormConst('U')
V = FormConst('V')
W = FormConst('W')
X = FormConst('X')
Y = FormConst('Y')
Z = FormConst('Z')

# Arbitrary expressions are "a"+number
a1 = FormWild('a1')
a2 = FormWild('a2')
a3 = FormWild('a3')
a4 = FormWild('a4')
a5 = FormWild('a5')
a6 = FormWild('a6')
a7 = FormWild('a7')
a8 = FormWild('a8')
a9 = FormWild('a9')
a10 = FormWild('a10')