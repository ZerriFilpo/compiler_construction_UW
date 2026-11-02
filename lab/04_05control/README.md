# Compiler — Lab 3: Register Allocation

## Usage

```bash
uv run compiler.py <input file> [--registers n] > out.s
gcc -no-pie -z noexecstack out.s src/runtime.c -o out
./out
```

## Options

- `--registers n` — limits the number of registers used for variables
  (`0`–`11`, default `11`). The `n` most used colours stay in registers;
  the rest are spilled to the stack. `--registers 0` puts every variable on
  the stack. Invalid values are ignored (all 11 registers are used).

## Tests

- `tests/test1.lvar` — interfering variables get different registers
- `tests/test2.lvar` — non-interfering variables share a register
- `tests/test3.lvar` — call-live variables use callee-saved registers (saved and restored)
- `tests/test4.lvar` — spilling
- `tests/test5.lvar` — stack alignment

---

**Notice:** this README and the tests were generated with AI (Claude).