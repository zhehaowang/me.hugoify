# Know how to view deduced types

Some IDE tells type.

Compiler diagnostics. Could rely on dummy code like this (trigger a compiler error to make it tell the types)
```cpp
// To view the types of x and y
template<typename T>       // declaration only for TD;
class TD;                  // TD == "Type Displayer"

TD<decltype(x)> xType;     // elicit errors containing
TD<decltype(y)> yType;     // x's and y's types
```

At runtime
```cpp
std::cout << typeid(x).name() << '\n';    // display types for x
// This approach relies on the fact that invoking typeid on an object
// such as x yields a std::type_info object, and std::type_info has a
// member function, name, that produces a C-style string
// (i.e., a const char*) representation of the name of the type.

// It may show something like a PKi, pointer to const integer (this
// display can be demangled)

// std::type_info::name could be incorrect, because the specification
// for std::type_info::name mandates that the type be treated as if it
// had been passed to a template function as a by-value parameter.
```

Where IDE and std::type_info::name could be wrong, Boost.TypeIndex is designed to be correct.

**Takeaways**
* Deduced types can often be seen using IDE editors, compiler error messages, and the Boost TypeIndex library
* The results of some tools may be neither helpful nor accurate, so an understanding of C++’s type deduction rules remains essential


Snippet:
```cpp
// view_deduced_types.m.cpp
#include <iostream>
#include <string>
#include <vector>
#include <boost/type_index.hpp>

// demonstrates different ways to check deduced types at compiler / run time

// test 1
class Widget {
  public:
    int x;
};

std::vector<Widget> createVec() {    // factory method
  return std::vector<Widget>();
}

// to trigger a compiler error to display type
template<typename T>       // declaration only for TD;
class TD;                  // TD == "Type Displayer"


template<typename T>
void f(const T& param)
{
  std::cout << "T =     " << typeid(T).name() << '\n';     // show T

  std::cout << "param = " << typeid(param).name() << '\n'; // show
                                                           // param's
                                                           // type
  // at runtime both are reported as PK6Widget, pointer to const
  // Widget (character-length-6): const Widget*
  // which could be incorrect as it should be const (const Widget*)&.

  //TD<T> p1;
  //TD<decltype(param)> p1;
  // TD spits the right type "const Widget *const &"

  using boost::typeindex::type_id_with_cvr;
  // show T
  std::cout << "T =     "
            << type_id_with_cvr<T>().pretty_name()
            << '\n';

  // show param's type
  std::cout << "param = "
            << type_id_with_cvr<decltype(param)>().pretty_name()
            << '\n';
  // at runtime boost::typeindex spits the right types
}

int main() {
  const auto vw = createVec();         // init vw w/factory return

  f(&vw[0]);                           // call f
  return 0;
}

```
