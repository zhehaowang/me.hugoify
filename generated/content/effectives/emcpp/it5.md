# Prefer auto to explicit type declarations

Upsides:
* Avoids variable uninitalized issue: auto variables have their type deduced from the initializer, so they must be initialized
* Avoids verbose variable declarations
* Can hold a closure in lieu of `std::function`
* Avoids potential implicit conversion you don't want: like `::size_type` to `int`, and the pairs in `unordered_map<K, V>` who are actually `pair<const K, V>` instead of `pair<K, V>` (unnecessary copycon calls!)
* Potentially can make refactoring easier

`std::function` is a template in C++11 that generalizes the idea of a function pointer (who can only point to functions), a `std::function` can refer to any callable object.
You specify the type (signature) of function you refer to when creating a std::function object.
Since lambda expressions yield callable objects, closures can be stored in `std::function` objects.

`std::function` object (comes at a fixed size, and if not big enough, heap allocate additional memory) typically uses more memory than the auto-declared object (takes as much space as the closure requires).
invoking a closure via a std::function object is almost certain to be slower than calling it via an auto-declared object. (implementation details that restrict inlining and yield indirect function calls)

Downsides:
* auto may deduce unexpected types. E.g. [item-2](it1-4-deducing-types.md#understand-auto-type-deduction)
```cpp
int x = 5;
auto y = (x);
```
* code readability. The counter argument would be that type inference is sufficiently understood, and IDE can always help.

**Takeaways**
* auto variables must be initialized, are generally immune to type mismatches that can lead to portability or efficiency problems, can ease the process of refactoring, and typically require less typing than variables with explicitly specified types.
* auto-typed variables are subject to the pitfalls described in Items 2 and 6.


Snippet:
```cpp
// prefer_auto.m.cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <boost/type_index.hpp>

using namespace std;

// demonstrates small missteps in declaring a type by hand (pair of a map) could
// lead to inefficiency in code, whereas auto avoids such issues

// test 1
class KeyClass {
  public:
    explicit KeyClass() { std::cout << "ctor1\n"; }
    explicit KeyClass(int x) : d_x(x) { std::cout << "ctor2\n"; }
    KeyClass(const KeyClass& rhs) { std::cout << "copycon\n"; }
    
    bool operator==(const KeyClass& rhs) const {
      return d_x == rhs.x();
    }
    
    int x() const { return d_x; }
  private:
    int d_x;
};

namespace std {
  template <>
  struct hash<KeyClass> {
    std::size_t operator()(const KeyClass& k) const {
      return hash<int>()(k.x());
    }
  };
}

int main() {
  std::unordered_map<KeyClass, int> map;
  map.insert(make_pair(3, 4));
  map.insert(make_pair(4, 5));
  map.insert(make_pair(5, 6));

  // note how copycon is called 3 times here
  // (also 'explicit' on copycon will cause compiler error)
  for (const std::pair<KeyClass, int>& p : map) {
    // p here is a compiler constructed temporary, if you get its address, it's not gonna
    // pointer to an element in map
    cout << "elem: " << p.second << "\n";
  }

  // note how copycon is not called here, since
  // p is std::pair<const KeyClass, int>
  for (auto p : map) {
    cout << "type of p: " << boost::typeindex::type_id_with_cvr<decltype(p)>() << "\n";
    cout << "elem: " << p.second << "\n";
  }

  // cout << "type of map iterator: " << boost::typeindex::type_id_with_cvr<std::unordered_map<KeyClass, int>::iterator>() << "\n";
  // cout << "type of map iterator: " << boost::typeindex::type_id_with_cvr<decltype(map.begin())>() << "\n";
  return 0;
}

```
