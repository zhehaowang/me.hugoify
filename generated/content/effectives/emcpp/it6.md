# Use the explicitly typed initializer idiom when auto deduces undesired types

As a general rule, "invisible" proxy classes don't play well with auto.
Objects of such classes are often not designed to live longer than a single statement, so creating variables of those types tends to violate fundamental library design assumptions.

For example, consider this code using `vector<bool>`
```cpp
Widget w;
bool highPriority = features(w)[5];  // is w high priority?
                                     // (features call returns a vector<bool>)
processWidget(w, highPriority);      // process w in accord
                                     // with its priority
```
Works just fine. Yet if we do
```cpp
Widget w;
auto highPriority = features(w)[5];
processWidget(w, highPriority);      // undefined behavior
```
Reason is in the type of `highPriority`, it's now `std::vector<bool>::reference`.

`std::vector<T>` `[] operator` returns a T&, except in the case of `vector<bool>` where it returns a `vector<bool>::reference` that can be implicitly casted to `bool`.
Reason for having this `::reference` is that the underlying uses a compact bit-storage for `vector<bool>`. You can't return a reference to a bit in C++, so a proxy class `::reference` is used instead.

So what happened instead is `highPriority` will be a reference to a temporary, and when we use it in processWidget the temporary is already destroyed and it causes undefined behavior.

Solution is to use explicitly typed initializer. Like
```cpp
auto highPriority = static_cast<bool>features(w)[5];
```

So when do we use explicitly typed initializer with `auto`?
* when `auto` will look at invisible proxy types.
(another common example is a `Matrix` class where the sum of 3 matrices is of type `Sum<Sum<Matrix, Matrix>, Matrix>` for performance reasons, and `Sum<T, U>` is a proxy class within `Matrix`) 
* when you intend to do a conversion. (e.g. `double` -> `float`)

**Takeaways**
* "Invisible" proxy types can cause auto to deduce the "wrong" type for an initializing expression.
* The explicitly typed initializer idiom forces auto to deduce the type you want it to have.

Snippet:
```cpp
// explicitly_typed_initializer.m.cpp
#include <iostream>
#include <string>
#include <vector>
#include <boost/type_index.hpp>

using namespace std;

// demonstrate a case working with proxy classes (vector<bool>) where auto might
// cause undefined behavior while bool is fine.

vector<bool> buildVector() {
  vector<bool> bs;
  bs.push_back(false);
  bs.push_back(false);
  bs.push_back(false);
  bs.push_back(false);
  bs.push_back(false);
  bs.push_back(true);
  return bs;
}

int main() {
  auto highPriority = buildVector()[5];
  cout << "type: " << boost::typeindex::type_id_with_cvr<decltype(highPriority)>() << "\n";
  
  if (highPriority) {     // undefined behavior: reference to deleted temporary
    cout << "high priority\n";
  } else {
    cout << "low priority\n";
  }

  // instead, do (explicitly typed initializer idiom)
  auto highPriorityGood = static_cast<bool>(buildVector()[5]);
  if (highPriorityGood) {     // all good
    cout << "high priority\n";
  } else {
    cout << "low priority\n";
  }

  return 0;
}

```
