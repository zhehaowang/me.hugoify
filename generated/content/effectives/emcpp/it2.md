# Understand auto type deduction

Auto type deduction actually largely follows the same rules as template type deduction.

```cpp
auto x = 27;          // case 3 (x is neither ptr nor reference)

const auto cx = x;    // case 3 (cx isn't either)

const auto& rx = x;   // case 1 (rx is a non-universal ref.)

// Case 2s:
auto&& uref1 = x;     // x is int and lvalue,
                      // so uref1's type is int&

auto&& uref2 = cx;    // cx is const int and lvalue,
                      // so uref2's type is const int&

auto&& uref3 = 27;    // 27 is int and rvalue,
                      // so uref3's type is int&&

// Same rule goes for arrays and functions

const char name[] =            // name's type is const char[13]
  "R. N. Briggs";

auto arr1 = name;              // arr1's type is const char*

auto& arr2 = name;             // arr2's type is
                               // const char (&)[13]


void someFunc(int, double);    // someFunc is a function;
                               // type is void(int, double)

auto func1 = someFunc;         // func1's type is
                               // void (*)(int, double)

auto& func2 = someFunc;        // func2's type is
                               // void (&)(int, double)
```

The only difference is in auto always treats {} as std::initializer\_list\<T\>, while template deduction does not.

```cpp
int x1 = 27;
int x2(27);
int x3 = { 27 };
int x4{ 27 };
// these four do the same thing

auto x1 = 27;             // type is int, value is 27

auto x2(27);              // ditto

auto x3 = { 27 };         // type is std::initializer_list<int>,
                          // value is { 27 }

auto x4{ 27 };            // ditto

// template type deduction does not work with {} as-is
auto x = { 11, 23, 9 };   // x's type is
                          // std::initializer_list<int>

template<typename T>      // template with parameter
void f(T param);          // declaration equivalent to
                          // x's declaration

f({ 11, 23, 9 });         // error! can't deduce type for T

// instead,
template<typename T>
void f(std::initializer_list<T> initList);

f({ 11, 23, 9 });         // T deduced as int, and initList's
                          // type is std::initializer_list<int>
```

**Takeaway**

* auto type deduction is usually the same as template type deduction, but auto type deduction assumes that a braced initializer represents a std::initializer_list, and template type deduction doesn’t.
* auto in a function return type or a lambda parameter implies template type deduction, not auto type deduction.


Snippet:
```cpp
// auto_type_deduction.m.cpp
#include <iostream>
#include <string>

// demonstrates the similarity between template type deduction and auto type
// deduction

int main() {
    const int from = 15;
    // this is like rule 2 in template type deduction.
    // When the given has const but it's pass-by-value, constness is dropped
    auto to = from;
    to += 27;
    std::cout << to << "\n";
    return 0;
}

```
