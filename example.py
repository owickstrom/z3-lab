from typing import Union
from z3 import (
    And,
    ArithRef,
    Concat,
    Function,
    Implies,
    Int,
    IntSort,
    Length,
    PrefixOf,
    Real,
    Solver,
    Strings,
    SuffixOf,
    prove,
    sat,
    solve,
)
from dataclasses import dataclass


###############################
# Rect
###############################


@dataclass
class Rect:
    x: Union[int, ArithRef]
    y: Union[int, ArithRef]

    def area(self):
        return self.x * self.y

    def perimeter(self):
        return 2 * (self.x + self.y)

    def __str__(self):
        return f"Rect(x={self.x}, y={self.y})"

    def map(self, f):
        return Rect(f(self.x), f(self.y))


r = Rect(Int("x"), Int("y"))

s = Solver()
s.add(r.area() == 10, r.x >= 2, r.y >= 2)

if s.check() == sat:
    m = s.model()
    r2 = r.map(lambda x: m.evaluate(x))
    print(r2)
else:
    print("No solution found.")


###############################
# Strings
###############################

s = Solver()
x, y, z = Strings("x y z")
s.add(
    Implies(
        And(PrefixOf(x, y), SuffixOf(z, y), Length(y) == Length(x) + Length(z)),
        y == Concat(x, z),
    )
)
s.set("smt.string_solver", "z3str3")
s.check()
print(s.model())


###############################
# Functions
###############################

x = Int("x")
y = Int("y")
f = Function("f", IntSort(), IntSort())
s = Solver()
s.add(f(f(x)) == x, f(x) == y, x != y)
s.check()
m = s.model()
print("f(f(f(x))) =", m.evaluate(f(f(f(x)))))
print("f(f(x)) =", m.evaluate(f(f(x))))
print("f(x)    =", m.evaluate(f(x)))
