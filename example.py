from typing import *
from z3 import solve
from dataclasses import dataclass


# symbolic execution example
def example(x, y) -> int:
    if x > 431:
        if y < 912:
            assert False
        else:
            return x
    else:
        return y


type Expr = int | bool | str | If | Lt | Gt | Fun | App | Fail


@dataclass
class If:
    cond: Expr
    t: Expr
    f: Expr


@dataclass
class Lt:
    lhs: Expr
    rhs: Expr


@dataclass
class Gt:
    lhs: Expr
    rhs: Expr


@dataclass
class Fun:
    args: list[str]
    body: Expr


@dataclass
class App:
    fun: Expr
    params: list[Expr]


@dataclass
class Fail:
    pass


type Value = int | bool | Closure

type Env = dict[str, Value]


@dataclass
class Closure:
    env: Env
    args: list[str]
    body: Expr


def eval(env: Env, expr: Expr) -> Value:
    match expr:
        case bool():
            return expr
        case int():
            return expr
        case str():
            return env[expr]
        case If(cond, t, f):
            if eval(env, cond):
                return eval(env, t)
            else:
                return eval(env, f)
        case Lt(lhs, rhs):
            l = eval(env, lhs)
            r = eval(env, rhs)
            if isinstance(l, int) and isinstance(r, int):
                return l < r
            else:
                raise ValueError(f"type error in expression: {expr}")
        case Gt(lhs, rhs):
            l = eval(env, lhs)
            r = eval(env, rhs)
            if isinstance(l, int) and isinstance(r, int):
                return l > r
            else:
                raise ValueError(f"type error in expression: {expr}")
        case Fun(args, body):
            return Closure(env, args, body)
        case App(fun, params):
            f = eval(env, fun)
            match f:
                case Closure(cenv, args, body):
                    if len(args) != len(params):
                        raise ValueError(f"arity mismatch in application: {expr}")
                    new_env = cenv.copy()
                    for arg, param in zip(args, params):
                        new_env[arg] = eval(env, param)
                    return eval(new_env, body)
                case _:
                    raise ValueError(f"expected closure in application, got: {f}")
        case Fail():
            raise ValueError("encountered failure")


example2 = Fun(["x", "y"], If(Gt("x", 431), If(Lt("y", 912), Fail(), "x"), "y"))

print(eval({}, App(example2, [1, 2])))
