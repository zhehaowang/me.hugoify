# Item 9: prefer alias declarations to `typedefs`

Alias is easier to swallow when dealing with types involving function pointers
```cpp
// FP is a synonym for a pointer to a function taking an int and
// a const std::string& and returning nothing
typedef void (*FP)(int, const std::string&);      // typedef

// same meaning as above
using FP = void (*)(int, const std::string&);     // alias
                                                  // declaration
```

A more compelling reason to use alias is that they work with having templates inside

```cpp
// alias (C++11)
template<typename T>                           // MyAllocList<T>
using MyAllocList = std::list<T, MyAlloc<T>>;  // is synonym for
                                               // std::list<T,
                                               //   MyAlloc<T>>

MyAllocList<Widget> lw;                        // client code

// And to use MyAllocList within another template

template<typename T>
class Widget {
private:
  MyAllocList<T> list;                         // compared with below
                                               // no "typename",
  …                                            // no "::type"
};

// typedef (C++03)
template<typename T>                     // MyAllocList<T>::type
struct MyAllocList {                     // is synonym for
  typedef std::list<T, MyAlloc<T>> type; // std::list<T,
};                                       //   MyAlloc<T>>

MyAllocList<Widget>::type lw;            // client code

// It gets worse. If you use typedef inside a template for the purpose
// of creating a linked list holding objects of a type specified by a
// template parameter, you have to precede the typedef name with typename,
// because MyAllocList<T>::type is now a dependent type (nested dependent name).
//
// Compiler doesn't know for sure MyAllocList<T>::type is a type. There might be
// a specialization of MyAllocList<T> somewhere that has ::type not as a type,
// but as a data member. Compiler doesn't know for sure.)

template<typename T>
class Widget {                         // Widget<T> contains
private:                               // a MyAllocList<T>
  typename MyAllocList<T>::type list;  // as a data member
  …
};
```

C++11 has type traits to perform type transformation, in C++11, it's implemented with enclosing structs (C++03 typedef), and in C++14 it's done with alias. So we have

```cpp
std::remove_const<T>::type           // C++11: const T → T
std::remove_const_t<T>               // C++14 equivalent

std::remove_reference<T>::type       // C++11: T&/T&& → T
std::remove_reference_t<T>           // C++14 equivalent

std::add_lvalue_reference<T>::type   // C++11: T → T&
std::add_lvalue_reference_t<T>       // C++14 equivalent
```

**Takeaways**
* `typedef`s don’t support templatization, but alias declarations do.
* Alias templates avoid the `::type` suffix and, in templates, the `typename` prefix often required to refer to typedefs.
* C++14 offers alias templates for all the C++11 type traits transformations.


Snippet:
```cpp
// alias.m.cpp
#include <iostream>
#include <string>
#include <list>

// demonstrates typedefs can't work with templates while 'using' aliases can

template <typename T>
using MyList = std::list<T>;

//template <typename T>
//typedef std::list<T> MyListType;
// compiler error: a typedef cannot be a template!

int main() {
  MyList<int> list1;
  //MyList<int> list2;
  return 0;
}

```
