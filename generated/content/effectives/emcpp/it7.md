# Item 7: distinguish between () and {} when creating objects

Different ways of initializing

```cpp
int x(0);             // initializer is in parentheses
int y = 0;            // initializer follows "="
int z{ 0 };           // initializer is in braces
int z = { 0 };        // initializer uses "=" and braces, generally the same as braces
```

First differentiate assignment operator and copy constructor

```cpp
Widget w1;            // call default constructor
Widget w2 = w1;       // not an assignment; calls copy ctor
w1 = w2;              // an assignment; calls copy operator=
```

C++11 introduces the concept of **uniform initialization** using braces.

```cpp
std::vector<int> v{ 1, 3, 5 }; // v's initial content is 1, 3, 5, not possible in c++03

class Widget {
  …

private:
  int x{ 0 };         // fine, x's default value is 0
  int y = 0;          // also fine
  int z(0);           // error!
};

// Uncopiable objects can use {}, (), but not = to initialize
std::atomic<int> ai1{ 0 };     // fine
std::atomic<int> ai2(0);       // fine
std::atomic<int> ai3 = 0;      // error!

// braced initialization prohibits implicit narrowing conversions among built-in types
double x, y, z;
int sum1{ x + y + z };       // error! sum of doubles may
                             // not be expressible as int
int sum2(x + y + z);         // okay (value of expression
                             // truncated to an int)
int sum3 = x + y + z;        // ditto

// C++ parse says anything that can be interpretted as a declaration must be interpretted as one, thus
Widget w1(10);     // call Widget ctor with argument 10
Widget w2();       // most vexing parse! declares a function
                   // named w2 that returns a Widget!
Widget w3{};       // calls Widget ctor with no args
```

Why not always use braced initialization then?

There can be unexpected behaviors due to the tangled relationship among initializers, `std::intializer_lists`, and constructor overload resolution.

E.g. in [item 2](it1-4-deducing-types.md#understand-auto-type-deduction), deduced type for auto using braced initialization is `std::initializer_list`.
(The more you like auto, the less you may like braced initialization)

```cpp
// Braced initialization always prefers a constructor overload that takes in
// std::initialization_list, and what would normally be copy and move
// construction can be hijacked by std::initialization_list ctors

class Widget {
public:
  Widget(int i, bool b);
  Widget(int i, double d);

  Widget(std::initializer_list<long double> il);

  operator float() const;                          // convert
};

Widget w1(10, true);     // uses parens and, as before,
                         // calls first ctor

Widget w2{10, true};     // uses braces, but now calls
                         // std::initializer_list ctor
                         // (10 and true convert to long double)

Widget w3(10, 5.0);      // uses parens and, as before,
                         // calls second ctor

Widget w4{10, 5.0};      // uses braces, but now calls
                         // std::initializer_list ctor
                         // (10 and 5.0 convert to long double)

Widget w5(w4);               // uses parens, calls copy ctor

Widget w6{w4};               // uses braces, calls
                             // std::initializer_list ctor
                             // (w4 converts to float, and float
                             // converts to long double)

Widget w7(std::move(w4));    // uses parens, calls move ctor

Widget w8{std::move(w4)};    // uses braces, calls
                             // std::initializer_list ctor
                             // (for same reason as w6)

// Compiler will even block calling other matched ctors, if
// std::initializer_list ctor exists + braced initialization,
// but the braced initialization requires narrowing
// conversions. (no conversions is fine)

// And if you have a default ctor and a initializer_list ctor
Widget w1;            // calls default ctor
Widget w2{};          // also calls default ctor
Widget w3();          // most vexing parse! declares a function!
Widget w4({});        // calls std::initializer_list ctor
                      // with empty list
```

Why does this matter?
Consider `std::vector`, it has a (length, value) ctor and a `std::initializer_list` ctor.
And the difference could be such.
```cpp
std::vector<int> v1(10, 20);  // use non-std::initializer_list
                              // ctor: create 10-element
                              // std::vector, all elements have
                              // value of 20

std::vector<int> v2{10, 20};  // use std::initializer_list ctor:
                              // create 2-element std::vector,
                              // element values are 10 and 20
```
That means as a class designer, don't do what `std::vector` does.

It's best to design your constructors so that the overload called isn't affected by whether clients use parentheses or braces.

And if you need to add a `std::initializer_list` ctor, do so with great deliberation.

The second lesson is that as a class client, you must choose carefully between parentheses and braces when creating objects.

**Takeaway**
* Braced initialization is the most widely usable initialization syntax, it prevents narrowing conversions, and it’s immune to C++’s most vexing parse.
* During constructor overload resolution, braced initializers are matched to `std::initializer_list` parameters if at all possible, even if other constructors offer seemingly better matches.
* An example of where the choice between parentheses and braces can make a significant difference is creating a `std::vector<numeric type>` with two arguments.
* Choosing between parentheses and braces for object creation inside templates can be challenging. One could do braces only when necessary; or instead, always do `{}` but understand when semantically `()` is desirable



Snippet:
```cpp
// braced_initialization.m.cpp
#include <iostream>
#include <string>
#include <vector>

using namespace std;

// demonstrates {} initialization always picks the ctor taking
// std::initializer_list when multiple matches are present. This can be
// undesirable

// as a class designer, be careful about providing a ctor taking
// std::initializer_list. Anything using {} initialization will be matched!
class Widget {
  public:
    Widget(long double a, bool b) { cout << "ctor1\n"; };
    Widget(std::initializer_list<float> list) {
      cout << "ctor initializer_list\n";
    }
  private:
};

int main() {
  Widget w1(12.0, true);
  Widget w2{12.0, true};
  long double x = 0;
  //Widget w3{x, true};
  // compiler would complain about long double narrowing, as opposed to trying
  // ctor1

  // std::initializer_list ctor in action, don't make the same mistake as a
  // class designer. And be careful as a client.
  std::vector<int> vec1(1, 2);
  std::vector<int> vec2{1, 2};
  
  cout << "\n";
  for (auto p: vec1) {
    cout << "vec1:" << p << "\n";
  }
  
  cout << "\n";
  for (auto p: vec2) {
    cout << "vec2:" << p << "\n";
  }
  return 0;
}

```
