## 1.3.3 (2023-02-08)

### Fix

- handle well comments in from import statements
- remove dependency with py

## 1.3.2 (2022-11-14)

### Fix

- type_checking bug

## 1.3.1 (2022-10-14)

### Fix

- Respect two newlines between code and imports.
- allow imports with dots

## 1.3.0 (2022-10-14)

### Feat

- added --ignore-init-modules flag (fixes #226)
- added __main__.py file (fixes #210)

### Fix

- ignore `if __name__ == "__main__":` lines for coverage
- ignore incorrect no-value-for-parameter lint
- fixed typing issue

## 1.2.3 (2022-09-15)

## 1.2.2 (2022-02-16)

### Perf

- remove the uppercap on python 3.11

## 1.2.1 (2022-02-11)

### Fix

- correct pdm local installation so mypy works

## 1.2.0 (2022-02-09)

## 1.1.1 (2022-02-04)

### Fix

- correct the package building
- correct the package building

## 1.1.0 (2022-02-03)

### Feat

- use pdm to manage dependencies
- use pdm to manage dependencies
- add support for python 3.10

## 1.0.5 (2022-02-03)

## 1.0.4 (2022-01-25)

## 1.0.3 (2022-01-24)

## 1.0.2 (2022-01-21)

### Fix

- don't touch files that are not going to be changed

## 1.0.1 (2022-01-21)

### Fix

- remove empty multiline import statements

## 1.0.0 (2022-01-18)

## 0.11.0 (2021-12-21)

### Feat

- support multi paragraph sections inside the TYPE_CHECKING block

## 0.10.0 (2021-12-08)

### Feat

- cli `--config-file` option

## 0.9.1 (2021-11-30)

### Fix

- support the removal of from x import y as z statements

## 0.9.0 (2021-11-30)

### Feat

- give priority to the common statements over the rest of sources
- added datetime and ModelFactory to the default imports

### feat

- support comments in simple import statementsgn

## 0.8.0 (2021-11-23)

### Feat

- extend common statements

## 0.7.5 (2021-10-22)

### Fix

- ignore unused import statements with noqa autoimport line

## 0.7.4 (2021-10-15)

### Fix

- deprecate python 3.6

## 0.7.3 (2021-08-31)

### Fix

- let autoimport handle empty files

## 0.7.2 (2021-08-20)

### Fix

- avoid RecursionError when searching for packages inside the project

## 0.7.1 (2021-08-20)

### Fix

- prevent autoimport from importing same package many times

## 0.7.0 (2021-04-23)

### Fix

- install wheel in the build pipeline

### feat

- add a ci job to test that the program is installable

### Perf

- add new Enum import alias

## 0.6.1 (2021-02-02)

### Fix

- respect newlines in the header section

### fix

- respect document trailing newline

## 0.6.0 (2021-02-01)

### Fix

- respect shebang and leading comments

### feat

- add BaseModel and Faker to common statements

## 0.5.0 (2021-01-25)

### Feat

- add FrozenDateTimeFactory and suppress import statements

## 0.4.3 (2020-12-29)

### Fix

- respect try except statements in imports

### fix

- remove autoimport from development dependencies

## 0.4.2 (2020-12-29)

### Fix

- wrong import indentation when moving up the imports.

### perf

- common import statements are now run sooner

## 0.4.1 (2020-12-29)

### Fix

- make fix_code respect if TYPE_CHECKING statements

## 0.4.0 (2020-12-17)

### Refactor

- make _find_package_in_our_project a statimethod

### Fix

- import developing package objects when not in src directory

### feat

- import objects defined in the __all__ special variable

## 0.3.0 (2020-12-17)

### Feat

- Add imports of the local package objects
- make autoimport manage the commonly used imports

### Refactor

- move the business logic to the SourceCode entity

### fix

- remove all unused imports instead of just one

## 0.2.2 (2020-12-11)

### Fix

- remove unused imported objects in multiline from import statements

## 0.2.1 (2020-12-10)

### Fix

- support multiline import statements and multiline strings

## 0.2.0 (2020-11-12)

### Feat

- move import statements to the top

### Fix

- **setup.py**: extract the version from source without exec statement

## 0.1.1 (2020-10-27)

### Fix

- correct the formatting of single line module docstrings.
- add newline between module docstring, import statements and code.

## 0.1.0 (2020-10-23)

### Feat

- create first version of the program (#3)
- create initial project structure
