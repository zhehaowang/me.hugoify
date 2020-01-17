# Know what functions C++ silents writes and calls

If you don't declare a copy constructor, copy assignment operator, or destructor, C++ declares and defines one for you.
If you don't declare any constructors, C++ declares a default constructor for you.
Note that the generated dtor is not virtual, unless the class is derived from a class with a virtual dtor.

Consider this example
```cpp
template<typename T>
class NamedObject {
public:
  NamedObject(const char *name, const T& value);
  NamedObject(const std::string& name, const T& value);

  ...

private:
  std::string nameValue;
  T objectValue;
};

NamedObject<int> no1("Smallest Prime Number", 2);

NamedObject<int> no2(no1); // calls compiler-supplied copy constructor
                           // this calls copycon of string to copy
                           // nameValue, and copies the bits of int
                           // (instantiated type, in this case a primitive
                           // type) to copy objectValue.
no2 = no1;                 // copy assignment, calls the copy assignment of
                           // string, and copies over the bits of int

// in fact, compiler generated copy assignment behaves as described above
// only when resulting code is both legal and has a reasonable chance of
// making sense.

// suppose we have this instead

template<class T>
class NamedObject {
public:
  // this ctor no longer takes a const name, because nameValue
  // is now a reference-to-non-const string. The char* constructor
  // is gone, because we must have a string to refer to.
  NamedObject(std::string& name, const T& value);

  ...                               // as above, assume no
                                    // operator= is declared
private:
  std::string& nameValue;           // this is now a reference
  const T objectValue;              // this is now const
};

// then consider this code
std::string newDog("Persephone");
std::string oldDog("Satch");

NamedObject<int> p(newDog, 2);

NamedObject<int> s(oldDog, 36);

p = s;                                       // what should happen to
                                             // the data members in p?
// Should the reference in p itself be modified, to refer to s instead?
// C++ doesn't allow that.
// Should the referred-to string be modified?
// In this case, C++ refuses to compile the code.
// Similarly, if the class contains const members, copy assignment opr
// won't be generated. Or if the class derives from a base class whose
// copy assignment is made private, the class's copy assignment won't
// work. 
```

**Takeaways**
* Compilers may implicitly generate a class's default constructor, copy constructor, copy assignment operator, and destructor


Snippet:
```cpp
// default_ctor_dtor_assignment.m.cpp
#include <iostream>
#include <string>

// demonstrates a case where compiler will not generate copy assignment operator for you
class MyClass {
  public:
    MyClass(int x, int y) : d_x(x), d_y(y) {}

    MyClass& operator=(const MyClass& rhs) = default;
    // this would still compile but does nothing, it appears
  private:
    const int d_x;
    int d_y;
};

int main() {
    MyClass m1(3, 4);
    MyClass m2(5, 6);
    //m1 = m2; // implicit copy assignment opr not defined 
    return 0;
}

```
