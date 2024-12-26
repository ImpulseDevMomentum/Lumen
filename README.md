This "language" was "created" for school purposes. Because of that, it is very, very simple, so please don't try to code next Cyberpunk. 
It was based on this tutorial: https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&index by CodePulse.

> Here are some syntax differences:

- instead of `ELIF` you have `OTHER` <br>
- instead of `RETURN` you have `BACK` <br>
- instead of `END` you have `STOP` <br>
- instead of `FUN/DEF` you have `FUNC` <br>
- instead of `VAR` you have `SET` <br>

To start your own program, simply run `shell.py` and then type RUN("your file with **.lum** extension"). The basic code example
is in the **/examples/example1.lum** or **/examples/calc.lum** or **/examples/name.lum** files; I _probably_ won't include any other examples.

You can also use the shell interactively. For example: 

- `SET b = 5`
- `IF b == 5 THEN PRINT("True") ELSE PRINT("NO")`

You can then type:

- `b + 1` <br>
and again: <br>

- `IF b == 5 THEN PRINT("True") ELSE PRINT("NO")` <br><br><br><br>


> ⭐ Furture features/plans:
- Add `l"{}"` to PRINT() ( so instead of `PRINT(f"{}")`, you'll be able to use `PRINT(l"{}")` ).
- Add support for `+=` and `-=` operators.
- Introduce `&` as an alternative for `AND` (without replacing `AND`).
- Add built-in functions: `INT()`, `STR()`, and `FLOAT()`.

> 😑 Complex Features:
- Enhance `PRINT("") -> variable` functionality to automatically determine the type (`int`, `string`, or `float`) based on the context.
- Integrate more APIs (from existing libraries such as `os`, `colorama`, etc.).
- Create comprehensive documentation.
- Develop a way to code custom libraries.
- Custom `Lumen IDE`


> 🔗 Useful Links: <br>
CodePulse's Github: https://github.com/davidcallanan <br>
Lumen IDE: https://github.com/ImpulseDevMomentum/Lumen-IDE <br>
Wish Logger PY: https://github.com/ImpulseDevMomentum/WishLoggerPY <br>
Wish Logger JS: https://github.com/ImpulseDevMomentum/WishLoggerJS <br>
FuzeMC: https://github.com/ImpulseDevMomentum/fuzemc <br>
