from typing import *
from z3 import *
from dataclasses import dataclass
import inspect


def todo(msg: str | None):
    raise NotImplementedError(msg)


##########################################
# SYMBOLIC EXECUTION
##########################################


def foobar(a: int, b: int):
    x = 1
    y = 0
    if a != 0:
        y = 3 + x
        if b == 0:
            x = 2 * (a + b)
    assert x - y != 0
    return x, y


# try:
#    foobar(2, 0)
#    print("ok")
# except:
#    print("not ok")


s = Solver()
path: List[bool] = []
constraints: List[BoolRef | Probe] = []

T = TypeVar("T")


@dataclass
class Proxy(Generic[T]):
    sym: T


@dataclass
class IntProxy(Proxy[ArithRef]):
    sym: ArithRef

    def __eq__(self, other):
        if not isinstance(other, IntProxy):
            other = IntProxy(IntVal(other))

        constraint = self.sym == other.sym

        if isinstance(constraint, BoolRef):
            return BoolProxy(constraint)
        else:
            raise ValueError(f"unsupported constraint: {constraint}")

    def __req__(self, other):
        return self.__eq__(other)

    def __add__(self, other):
        if not isinstance(other, IntProxy):
            other = IntProxy(IntVal(other))
        return IntProxy(self.sym + other.sym)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if not isinstance(other, IntProxy):
            other = IntProxy(IntVal(other))
        formula = self.sym * other.sym
        assert isinstance(formula, ArithRef)
        return IntProxy(formula)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __gt__(self, other):
        if not isinstance(other, IntProxy):
            other = IntProxy(IntVal(other))
        return BoolProxy(self.sym > other.sym)

    def __rgt__(self, other):
        return self.__gt__(other)

    def __lt__(self, other):
        if not isinstance(other, IntProxy):
            other = IntProxy(IntVal(other))
        return BoolProxy(self.sym < other.sym)

    def __rlt__(self, other):
        return self.__lt__(other)


@dataclass
class BoolProxy(Proxy):
    sym: BoolRef | Probe

    def __bool__(self):
        global path, constraints

        t_cond = s.check(*(constraints + [self.sym])) == sat
        f_cond = s.check(*(constraints + [Not(self.sym)])) == sat

        # Short-circuit on non-free branches (where there's only one possible way)
        match t_cond, f_cond:
            case True, False:
                return True
            case False, True:
                return False

        # we have a predetermined path to follow
        if len(path) > len(constraints):
            branch = path[len(constraints)]
            constraints.append(self.sym if branch else Not(self.sym))
            return branch

        # todo: prune search on max depth?

        path.append(True)
        constraints.append(self.sym)
        return True

    def __not__(self):
        return BoolProxy(Not(self.sym))  # type: ignore


def test(f: Callable):
    def make_sym(name: str, ann: Any) -> Proxy:
        if ann == None:
            raise ValueError(f"{f} lacks type annotation for argument {name}")
        elif ann == int:
            return IntProxy(Int(name))
        elif ann == bool:
            return BoolProxy(Bool(name))
        else:
            return todo(f"support type: {ann}")

    spec = inspect.getfullargspec(f)

    while True:
        constraints = []
        print(f"Testing with path: {path}")
        proxies = [make_sym(arg, spec.annotations.get(arg)) for arg in spec.args]
        try:
            ret = f(*proxies)
            args = ", ".join([str(s.model().eval(proxy.sym)) for proxy in proxies])
            print(f"{f.__name__}({args}) = {ret}")
            print(s.model())
        except Exception as e:
            args = ", ".join([str(s.model().eval(proxy.sym)) for proxy in proxies])
            print(f"{f.__name__}({args}) raised: {e}")
            print(s.model())

        # drop the false (already explored) branches at the end
        while len(path) > 0 and not path[-1]:
            print("Dropping explored branch.")
            path.pop()

        # stop if the whole tree has been explored
        if path == []:
            print("Entire tree explored.")
            return

        # switch the last branch
        print(f"Switching last branch in path: {path}")
        path[-1] = False


# test(foobar)


def other(x: int):
    if x > 100:
        if (x + 1) > 1000:
            return True
    return False


test(other)
