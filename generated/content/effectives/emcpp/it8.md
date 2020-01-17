# Item 8: prefer nullptr to 0 and NULL

Neither `0` or `NULL` has a pointer type.
In C++98, the primary implication of this was overloads on pointer and integral types could be surprising.

```cpp
void f(int);        // three overloads of f
void f(bool);
void f(void*);

f(0);               // calls f(int), not f(void*)

f(NULL);            // might not compile (if NULL is 0L, since
                    // the conversion from long to int, to bool
                    // is equally good), but typically calls
                    // f(int) if NULL is 0. Never calls f(void*)

f(nullptr);         // calls f(void*) overload
```

`nullptr` does not have an integral type.
It does not suffer from overload resolution surprises that `0` and `NULL` are susceptible to.
It doesn't have a pointer type either, but you can think of it as a pointer of all types.
Its actual type is `std::nullptr_t`, which implicitly converts to all pointer types.

`nullptr` improves code clarity. Consider
```cpp
auto result = findRecord( /* arguments */ );
if (result == nullptr) { ... }

// vs
auto result = findRecord( /* arguments */ );
if (result == 0) { ... }
```

`nullptr` shines even more in template specialization.

**Takeaways**
* Prefer `nullptr` to `0` and `NULL`.
* Avoid overloading on integral and pointer types.


Snippet:
```cpp
// nullptr.m.cpp
#include <iostream>
#include <string>
#include <mutex>

using namespace std;

// demonstrates how nullptr is a pointer type, while neither 0 nor NULL is a
// pointer type

int    f1(std::shared_ptr<int> spw) { return 0; };    // call these only when
double f2(std::unique_ptr<int> upw) { return 0.0; };  // the appropriate
bool   f3(int* pw) { return true; };                  // mutex is locked

template<typename FuncType,
         typename MuxType,
         typename PtrType>
auto lockAndCall(FuncType func,
                 MuxType& mutex,
                 PtrType ptr) -> decltype(func(ptr)) // C++11, in 14, do
                                                     // decltype(auto)
{
  using MuxGuard = std::lock_guard<MuxType>;
  MuxGuard g(mutex);
  return func(ptr);
}


int main() {
  std::mutex fm;

  //auto result1 = lockAndCall(f1, fm, 0);        // error: no known conversion
                                                  // from int to shared_ptr!
  //auto result2 = lockAndCall(f2, fm, NULL);     // error: no known conversion
                                                  // from long to unique_ptr!
  auto result3 = lockAndCall(f3, fm, nullptr);    // fine
  auto result4 = lockAndCall(f2, fm, nullptr);    // fine
  auto result5 = lockAndCall(f1, fm, nullptr);    // fine
  return 0;
}

```
