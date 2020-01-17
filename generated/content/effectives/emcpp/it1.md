# Understand type deduction

```cpp
template<typename T>
void f(T& param);       // param is a reference (same case goes for param is a pointer)

int x = 27;             // x is an int
const int cx = x;       // cx is a const int
const int& rx = x;      // rx is a reference to x as a const int

f(x);                   // T is int, param's type is int&

f(cx);                  // T is const int,
                        // param's type is const int&

f(rx);                  // T is const int,
                        // param's type is const int&, the refness of rx is dropped
```

```cpp
template<typename T>
void f(T&& param);       // param is now a universal reference

int x = 27;              // as before
const int cx = x;        // as before
const int& rx = x;       // as before

f(x);                    // x is lvalue, so T is int&,
                         // param's type is also int&

f(cx);                   // cx is lvalue, so T is const int&,
                         // param's type is also const int&

f(rx);                   // rx is lvalue, so T is const int&,
                         // param's type is also const int&

f(27);                   // 27 is rvalue, so T is int,
                         // param's type is therefore int&&
```

```cpp
template<typename T>
void f(T param);         // param is now passed by value

int x = 27;          // as before
const int cx = x;    // as before
const int& rx = x;   // as before

f(x);                // T's and param's types are both int

f(cx);               // T's and param's types are again both int

f(rx);               // T's and param's types are still both int
```

```cpp
// Array declaration in function params decays into pointer

void myFunc(int param[]);
void myFunc(int* param);         // same function as above
```

```cpp
template<typename T>
void f(T param);         // param is now passed by value

const char name[] = "J. P. Briggs";  // name's type is
                                     // const char[13]
f(name);          // name is array, but T deduced as const char*

// If instead

template<typename T>
void f(T& param);      // template with by-reference parameter

f(name);               // pass array to f, and T is actually deduced to be an array (const char [13])!
```

```cpp
// Functions, too, can decay into pointer

void someFunc(int, double);   // someFunc is a function;
                              // type is void(int, double)

template<typename T>
void f1(T param);             // in f1, param passed by value

template<typename T>
void f2(T& param);            // in f2, param passed by ref

f1(someFunc);                 // param deduced as ptr-to-func;
                              // type is void (*)(int, double)

f2(someFunc);                 // param deduced as ref-to-func;
                              // type is void (&)(int, double)
```

**Takeaway**

* During template type deduction, arguments that are references are treated as non-references, i.e., their reference-ness is ignored.
* When deducing types for universal reference parameters, lvalue arguments get special treatment.
* When deducing types for by-value parameters, const and/or volatile arguments are treated as non-const and non-volatile.
* During template type deduction, arguments that are array or function names decay to pointers, unless they’re used to initialize references.


Snippet:
```cpp
// type_deduction.m.cpp
#include <iostream>
#include <string>

// demonstates rule 1 and rule 2 in template type deduction, and that a function
// template parameter expecting an lvalue (reference) cannot work with a given
// rvalue

template <typename T>
void func_lvalue_reference(T& param) {
    std::cout << param << "\n";
}

template <typename T>
void func_universal_reference(T&& param) {
    std::cout << param << "\n";
}

int main() {
    int x = 42;
    
    // cannot pass compile: template expects a lvalue reference
    //func_lvalue_reference(27);

    // works fine
    func_lvalue_reference(x);
    func_universal_reference(27);
    func_universal_reference(x);

    const int& crx = x;
    func_lvalue_reference(crx);
    func_universal_reference(crx);
    
    return 0;
}

```
