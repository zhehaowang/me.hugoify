# Prefer const, enum, inline, to define

Alternatively, this item can be called "prefer compilers to preprocessors"

\#define is substituted by the preprocessor thus the symbol is never seen by the compiler, nor does it exist inside symbol table.
A language const instead will be seen by the compiler.

Advantages of using the latter include
* The compiler will be able to point out the symbol should an error occur
* If the const appears multiple times, the memory footprint is smaller using a const (only one copy in memory)
* No way to create class-specific const with \#define because define does not respect scope

When declaring const to replace \#define, keep in mind that pointers should have both the pointer and the object it refers to declared const. E.g.
```cpp
const char* const author = "me";
```
Though item 3 would claim in this case, a const std::string is preferable
```cpp
const std::string author = "me";
```

Another case to keep in mind is class-specific consts, to limit the scope of a constant to a class, you should make it a member, to ensure there is only one copy, make it a static member.
```cpp
class GamePlayer {
private:
  static const int NumTurns = 5;      // constant declaration
  int scores[NumTurns];               // use of constant
  ...
};
```
If you need to take the address of NumTurns, define it in the impl file of this class like this
```cpp
#include <game_player.h>
...
const int GamePlayer::NumTurns;  // definition
```
This does not go in the header so that you don't double define when the header is included in multiple places, and the definition does not have '=' since an initial value is already given at the point of declaration.

In-class initialization is allowed only for integral types and only for constants.
In cases where the above syntax can't be used, you put the initial value at the point of definition. Like this
```cpp
class CostEstimate {
private:

  static const double FudgeFactor;       // declaration of static class
  ...                                    // constant; goes in header file
};
const double                             // definition of static class
  CostEstimate::FudgeFactor = 1.35;      // constant; goes in impl. file
```

If your compiler wrongfully forbid the in-class initialization of constant integral types, which is required to, for example, declare an array of that size, you could do the "enum hack". Like this
```cpp
class GamePlayer {
private:
  enum { NumTurns = 5 };        // "the enum hack" — makes
                                // NumTurns a symbolic name for 5

  int scores[NumTurns];         // fine

  ...

};
```
The enum hack can also be used to forbid your client caller from taking the address or a reference of 'NumTurns', or to enforce that compiler does not allocate memory for 'NumTurns' (due to its being unnecessary).
And enum hack is fundamental for TMP.

Another common misuse of \#define is to implement macros that look like functions but don't incur the cost of a function call.
This misuse can be confusing to reason, e.g.
```cpp
#define CALL_WITH_MAX(a, b) f((a) > (b) ? (a) : (b))

int a = 5, b = 0;

CALL_WITH_MAX(++a, b);          // a is incremented twice
CALL_WITH_MAX(++a, b+10);       // a is incremented once
```
Here, the number of times that a is incremented before calling f depends on what it is being compared with!

Do this instead with a regular inline function using templates.
```cpp
template<typename T>                               // because we don't
inline void callWithMax(const T& a, const T& b)    // know what T is, we
{                                                  // pass by reference-to-
  f(a > b ? a : b);                                // const — see Item 20
}
```

Given the availability of consts, enums, and inlines, your need for the preprocessor (especially \#define) is reduced, but not eliminated.
\#include, \#ifdef, \#ifndef continue to play important roles in controlling compilation.

**Takeaways**
* For simple constants, prefer const objects or enums to #defines.
* For function-like macros, prefer inline functions to #defines.


Snippet:
```cpp
// header_with_static_const.h
#ifndef INCLUDED_CONST_OBJECT
#define INCLUDED_CONST_OBJECT

#include <string>
#include <iostream>

class ConstObject {
  public:
    ConstObject() : d_c(10) {
        std::cout << "ConstObject default ctor\n";
    };

    int d_c;

    void print() const;
};

class MyClass {
  public:
    static const int d_x = 5; // fine until you ask for its address,
                              // in which case, define it like d_obj in impl file, leave the initialization here
                              // and only do "const int MyClass::d_x" in the impl file
    static const ConstObject d_obj; // needs definition, correct way to define it is inside the impl file
    static const std::string d_s; // does not need definition due to no usage
};

//ConstObject MyClass::d_obj; // wrong, double definition

#endif
// impl_with_static_const.cpp
#include <header_with_static_const.h>

#include <iostream>
#include <string>

const ConstObject MyClass::d_obj; // fine, invokes default ctor before main

const int MyClass::d_x = 5;

void ConstObject::print() const {
    std::cout << d_c << "\n";
}
// prefer_const_enum_inline_to_define.m.cpp
#include <iostream>
#include <string>

#include <header_with_static_const.h>

int main() {
    std::cout << "invoking main\n";
    // When replacing #define with consts
    // correct specification of const pointer and const pointed to
    const char* name = "z";
    const char* const name2 = "h";
    const int* const i1 = 0;
    int const * const i2 = 0;

    // the second const does not matter
    const char const* name3 = "e"; // duplicate 'const' declaration specifier
    int const const * i3 = 0; // duplicate 'const' declaration specifier

    // To test class member static const definitions
    MyClass mc;
    mc.d_obj.print();
    std::cout << mc.d_x << "\n";
    //const int* const addrOfStaticConst = &mc.d_x;
    return 0;
}

```
