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
