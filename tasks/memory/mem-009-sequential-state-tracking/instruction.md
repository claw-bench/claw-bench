# Task: Sequential State Tracking

You are given a file at `workspace/transitions.txt` containing a list of state transitions, one per line. Execute all transitions in order and produce the final state of all variables.

## Transition Commands

- `SET x=5` - Set variable `x` to the value `5` (integer).
- `SET x=y` - Set variable `x` to the current value of variable `y`. If `y` is not defined, set `x` to 0.
- `ADD x 3` - Add 3 to variable `x`. The second operand can be a number or a variable name.
- `SUBTRACT x 2` - Subtract 2 from variable `x`. The second operand can be a number or a variable name.
- `MULTIPLY x 4` - Multiply variable `x` by 4. The second operand can be a number or a variable name.
- `DIVIDE x 2` - Integer-divide variable `x` by 2. The second operand can be a number or a variable name. Division by zero leaves the variable unchanged.
- `MOD x 3` - Set `x` to `x % 3` (modulo). The second operand can be a number or a variable name.
- `SWAP x y` - Swap the values of variables `x` and `y`.
- `DELETE x` - Remove variable `x` from the state. It should not appear in the output.

If an arithmetic operation references an undefined variable as operand, treat it as 0. If an arithmetic operation is performed on an undefined variable, that variable is created with initial value 0 before the operation.

Lines starting with `#` are comments and should be ignored. Empty lines should also be ignored.

## Output

Write the final state as a JSON object to `workspace/final_state.json`. Keys should be variable names (strings), values should be integers. Keys should be sorted alphabetically.

## Example

Given:
```
SET x=10
SET y=3
MULTIPLY x y
ADD y 7
```

Output `final_state.json`:
```json
{"x": 30, "y": 10}
```
