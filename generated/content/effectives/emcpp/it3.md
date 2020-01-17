# Understand decltype

decltype rules differ from template deduction: it doesn't potentially drop referenceness, have special handling for universal reference or pass by value, instead it always spits back the type of the expression given to it.

In a typical use case where we use decltype to declare the return type of a function which is dependent upon template parameter types, we do

```cpp
template<typename Container, typename Index>    // C++11, works, but
auto authAndAccess(Container& c, Index i)       // requires
  -> decltype(c[i])                             // refinement
{
  authenticateUser();
  return c[i];
}
// the auto and -> indicates C++11's trailing return type to
// account for the fact that the types of c and i aren't known
// when we see the first auto. 


template<typename Container, typename Index>    // C++14;
auto authAndAccess(Container& c, Index i)       // not quite
{                                               // correct
  authenticateUser();
  return c[i];                  // return type deduced from c[i]
                                // using template type deduction rules
                                // (in this case by-value)
}
// Not quite right in the following sense:
std::deque<int> d;
authAndAccess(d, 0) = 10;  // return d[0], then assign 10 to it;
                           // this won't compile as referenceness
                           // is dropped


template<typename Container, typename Index>   // C++14; works,
decltype(auto)                                 // but still
authAndAccess(Container& c, Index i)           // requires
{                                              // refinement
  authenticateUser();
  return c[i];
}
// This works in the sense that the compiler is told to use decltype
// rules in lieu of template deduction rules for return type deduction.
// Needs refinement in the sense that c can only be lvalue ref.

// Similarly,
Widget w;

const Widget& cw = w;

auto myWidget1 = cw;             // auto type deduction:
                                 // myWidget1's type is Widget

decltype(auto) myWidget2 = cw;   // decltype type deduction:
                                 // myWidget2's type is
                                 //   const Widget&


template<typename Container, typename Index>       // final
decltype(auto)                                     // C++14
authAndAccess(Container&& c, Index i)              // version
{
  authenticateUser();
  return std::forward<Container>(c)[i];
}
// c can now be universal reference.


template<typename Container, typename Index>       // final
auto                                               // C++11
authAndAccess(Container&& c, Index i)              // version
  -> decltype(std::forward<Container>(c)[i])
{
  authenticateUser();
  return std::forward<Container>(c)[i];
}
```

decltype have few surprises, including the following
```cpp
int x = 0;
decltype(x)   // yields int
decltype((x)) // yields int&, expr (x) is an lvalue expression, 
              // (not just a name) whose type is int&

// Expanding on this:
// In C++14, this is the kind of code that puts you on the
// express train to UB
decltype(auto) f1()
{
  int x = 0;
  return x;        // decltype(x) is int, so f1 returns int
}

decltype(auto) f2()
{
  int x = 0;
  return (x);      // decltype((x)) is int&, so f2 returns int&
}
```

**Takeaways**

* decltype almost always yields the type of a variable or expression without any modifications.
* For lvalue expressions of type T other than names, decltype always reports a type of T&.
* C++14 supports decltype(auto), which, like auto, deduces a type from its initializer, but it performs the type deduction using the decltype rules.


Snippet:
```cpp
// decltype.m.cpp
#include <iostream>
#include <string>
#include <vector>

// demonstrates the behaviors of decltype(auto) and using it to deduct function
// return type

// test 1: type of (expr) is a reference
decltype(auto) f1()
{
  int x = 0;
  return x;        // decltype(x) is int, so f1 returns int
}

decltype(auto) f2()
{
  int x = 0;
  return (x);      // decltype((x)) is int&, so f2 returns int&
                   // this emits a compiler warning
}

// test 2: using perfect forwarding and decltype(auto) to achieve function
// return type deduction
template<typename Container, typename Index>    // C++14;
auto authAndAccess(Container& c, Index i)       // not quite
{                                               // correct
  return c[i];                  // return type deduced from c[i]
                                // using template type deduction rules
                                // (rule 3, by value)
}

template<typename Container, typename Index>
auto& authAndAccess1(Container& c, Index i)
{
  return c[i];                  // return type deduced from c[i]
                                // using template type deduction rules
                                // (rule 1, non-universal reference / pointer)
}

template<typename Container, typename Index>
decltype(auto) authAndAccess2(Container&& c, Index i)
{
  return std::forward<Container>(c)[i]; // The correct version
}

int main() {
  // test 1
  f2() = 4;        // this would result in undefined behavior

  // test 2
  std::vector<int> v;
  v.push_back(1);
  //authAndAccess(v, 0) = 1; // would not compile
  authAndAccess1(v, 0) = 1;
  authAndAccess2(v, 0) = 1;
  return 0;
}

```
