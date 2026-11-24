# Lab 6 — Lfun (functions)

Run: `uv run compiler.py <file.lfun> [--registers n]`

## Non-obvious elements

### Functions (new in this lab)
- **shrink**: the top-level statements are wrapped in a `main` function ending in `return 0`. Function definitions must come before the top-level code (`prog ::= def* stmt*`); a `def` after top-level code is rejected.
- **Arity table**: `function_arity` (name → number of parameters) is built from all definitions *before* any body is shrunk, so calls to functions defined later (mutual recursion, e.g. `even`/`odd`) can be checked. A call with the wrong number of arguments, or a function name used as a value, is rejected.
- **Rejected parameters**: default arguments, `*args`, `**kwargs`, keyword-only (and positional-only) parameters, and more than 6 parameters.
- **remove_complex_operands**: call arguments become atoms; the function name is not atomized (it names a label). The operand of `return` may stay complex, so `explicate_tail` can see its shape.
- **explicate_tail**: for `return e`, an `if`/`Begin` puts a `return` in each branch; anything else becomes `Return(e)`. `return f(x)` is an ordinary call (no tail-call optimisation). The `return` case of `explicate_stmt` discards its continuation.
- **explicate_effect**: every call is kept as a statement, since any function may have side effects (`print`, `input_int`); only pure expressions like `x + 1` are dropped.
- **Labels**: each function gets `f_start` and `f_conclusion`. The `blockN` counter is reset once per program, not per function, so block labels stay unique after all functions are flattened into one file.
- **select_instructions**: arguments go to `%rdi %rsi %rdx %rcx %r8 %r9`, then `callq f`, then `movq %rax, lhs`. Each function starts with `movq %rdi, x1`, `movq %rsi, x2`, … These moves look redundant but make each parameter interfere with the later argument registers, so the allocator does not clobber them. A complex `return` is computed into a temporary, moved to `%rax`, then `jmp f_conclusion`.
- **Per-function back end**: liveness, interference, register allocation, patching and prelude/conclusion run once per function, with fresh state each time, so variables from different functions do not interfere. A variable live across a call interferes with all caller-saved registers (the `W` set of `callq`), so it gets a callee-saved register if one is free.
- **Output**: all functions' blocks are flattened into one `X86Program`; only `main` is `.globl`, and each function entry gets `.align 16`.

### From previous labs
- `and`/`or` become `IfExp` in shrink; `while` test temporaries stay inside the test (`Begin`); liveness across blocks uses a fixpoint worklist; one home map per function.

## Tests

`tests/<name>.lfun` with input `.in`, expected output `.out` (from CPython) and the generated assembly `.s`.

| test | covers |
|---|---|
| params | non-recursive functions with up to 6 parameters |
| wrong_arity | wrong number of arguments is rejected |
| fib, mutual | recursion (`fib`, `fact`) and mutual recursion (`even`/`odd`) agree with CPython |
| live_param | a parameter live after a call gets a callee-saved register |
| callee | callee-saved registers are not clobbered across calls |
| effects | calls with side effects as statements, `input_int` inside a function, `print` inside a function (stack alignment) |
| tail_if | `return` of an `if` expression, early return, falling off the end returns 0 |
| calls_in_exprs | calls inside expressions, `if` tests and `while` conditions |
| deep | deep recursion (10000 calls) and Ackermann |
| many_vars | many variables live across a call |

## Known limitations
- At most 6 parameters; no first-class functions; no tail-call optimisation.
- A function that ends without `return` returns 0 (Python would return `None`).
- `print` of a boolean prints `1`/`0`; `//` and `%` truncate toward zero; integers are 64-bit.

---
*This README and some of the test programs in `tests/` were generated with AI assistance.*