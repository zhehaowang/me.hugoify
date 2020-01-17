# Use const whenever possible

const is how you can communicate to the compiler and other programmers that a value should not be altered and the compiler will enforce it. Use it whenever this constraint holds.

Using const with pointers:
```cpp
char greeting[] = "Hello";

char *p = greeting;                    // non-const pointer,
                                       // non-const data

const char *p = greeting;              // non-const pointer,
                                       // const data

char * const p = greeting;             // const pointer,
                                       // non-const data

const char * const p = greeting;       // const pointer,
                                       // const data
```
If the word const appears to the left of the asterisk, what's pointed to is constant; if the word const appears to the right of the asterisk, the pointer itself is constant; if const appears on both sides, both are constant.
If a const appears on the left of the asterisk, whether it's "const type" or "type const" makes no difference.

An STL iterator is modeled on a pointer, declaring an iterator itself const will be analogous to declaring the pointer const.
If with STL you want to declare the data const, use const\_iterator.

```cpp
std::vector<int> vec;
...

const std::vector<int>::iterator iter =     // iter acts like a T* const
  vec.begin();
*iter = 10;                                 // OK, changes what iter points to
++iter;                                    // error! iter is const

std::vector<int>::const_iterator cIter =   //cIter acts like a const T*
  vec.begin();
*cIter = 10;                               // error! *cIter is const
++cIter;                                  // fine, changes cIter
```

const can be used to specify a function return value, its parameters, and the function itself if it is a member function.

Having a function return a constant value is generally inappropriate, but sometimes doing so can reduce the incidence of client errors without giving up safety or efficiency. For example,
```cpp
class Rational { ... };

const Rational operator*(const Rational& lhs, const Rational& rhs);

// why should the operator* for Rationals return const?
// because if not, clients can inadvertently, do

Rational a, b, c;

(a * b) = c;                           // invoke operator= on the
                                       // result of a*b!

// and all it takes is a typo for the above code to happen

if (a * b = c) ...                     // oops, meant to do a comparison!
```
One of the hallmarks of good user-defined types is that they avoid gratuitous incompatibilities with the built-ins.
The above where the product of two can be assigned is to is pretty gratuitous.

const member functions are important as they make the interface easier to understand (which functions can change the object in question), and they make it possible to work with const objects.

Member functions differing only in their constness can be overloaded. E.g.
```cpp
class TextBlock {
  public:
    ...
    const char&                                       // operator[] for
    operator[](const std::size_t position) const      // const objects
    { return text[position]; }
 
    char&                                             // operator[] for
    operator[](const std::size_t position) const      // non-const objects
    { return text[position]; }
  
  private:
    std::string text;
};
```

It's never legal to modify the return value of a function that returns a built-in type. (and when modify the return value of a function, note that it'd be done on a copy of the source inside that function)

Semantics-wise, there is bitwise constness and logical constness.
C++ uses bitwise constness, where a const member function is not allowed to modify any of the bits inside the object.

Bitwise const would mean if the object's data member is a pointer, inside a const member function where the pointer looks at cannot be changed, but the content of what it points to can be. For example,
```cpp
class CTextBlock {
public:
  ...

  char& operator[](std::size_t position) const   // inappropriate (but bitwise
  { return pText[position]; }                    // const) declaration of
                                                 // operator[]
private:
  char *pText;
};
// this compiles without issues.

const CTextBlock cctb("Hello");        // declare constant object

char *pc = &cctb[0];                   // call the const operator[] to get a
                                       // pointer to cctb's data

*pc = 'J';                              // cctb now has the value "Jello"
// in the book this should allow you to change the value, though in my code
// sample the assignment call results in 'bus error'
```

Logical constness suggest that a const member function may modify parts of the object only if its clients cannot detect.
This notion can be achieved with 'mutable' keyword. E.g.
```cpp
class CTextBlock {
public:

  ...

  std::size_t length() const;

private:
  char *pText;

  mutable std::size_t textLength;         // these data members may
  mutable bool lengthIsValid;             // always be modified, even in
};                                        // const member functions

std::size_t CTextBlock::length() const
{
  if (!lengthIsValid) {
    textLength = std::strlen(pText);      // now fine
    lengthIsValid = true;                 // also fine
  }

  return textLength;
}
```

Now suppose you have boundary check, logging, etc in TextBlock's operator[].
These logic would be duplicated in both the const and the non-const version.
To avoid the duplication, we could do a cast instead (which is usually a bad idea in other circumstances) like this
```cpp
class TextBlock {
public:
  const char& operator[](std::size_t position) const     // same as before
  {
    ... // some shared operations
    return text[position];
  }

  char& operator[](std::size_t position)         // now just calls const op[]
  {
    return
      const_cast<char&>(                         // cast away const on
                                                 // op[]'s return type;
        static_cast<const TextBlock&>(*this)     // add const to *this's type;
          [position]                             // call const version of op[]
      );
  }
};
```
This is safe as when we are given a non-const TextBlock, we can safely invoke the const version and then cast its result.
The other way round of having the const version call the non-const version is not something you want to do.

**Takeaways**
* Declaring something const helps compilers detect usage errors. const can be applied to objects at any scope, to function parameters and return types, and to member functions as a whole.
* Compilers enforce bitwise constness, but you should program using conceptual constness.
* When const and non-const member functions have essentially identical implementations, code duplication can be avoided by having the non-const version call the const version.


Snippet:
```cpp
// use_const_whenever_possible.m.cpp
#include <iostream>
#include <string>

class StringWrapper {
  public:
    StringWrapper(const char *in) : d_data(in) {}

    const char& operator[](std::size_t idx) const {
        std::cout << "call on const version\n";
        return d_data[idx];
    }
    char& operator[](std::size_t idx) {
        std::cout << "call on non-const version\n";
        return d_data[idx];
    }
  private:
    std::string d_data;
};

class CTextBlock {
  public:
    CTextBlock(char *in) : d_data(in) {}

    char& operator[](std::size_t position) const   // inappropriate (but bitwise
    { return d_data[position]; }                   // const) declaration of
                                                   // operator[]
    char *d_data;
};

class TextBlock {
  public:
    TextBlock(const char *in) : d_data(in) {}
    const char& operator[](std::size_t position) const     // same as before
    {
        std::cout << "const version of operator[]\n";
        return d_data[position];
    }

    char& operator[](std::size_t position)         // now just calls const op[]
    {
    return
      const_cast<char&>(                         // cast away const on
                                                 // op[]'s return type;
        static_cast<const TextBlock&>(*this)     // add const to *this's type;
          [position]                             // call const version of op[]
      );
    }

    std::string d_data;
};

int main() {
    StringWrapper sw("Hello");
    std::cout << sw[0] << "\n";                   // calls non-const

    const StringWrapper csw("World");
    std::cout << csw[0] << "\n";                  // calls const

    sw[0] = 'Y';
    std::cout << sw[0] << "\n";                   // calls non-const

    char* content = "Hello";

    const CTextBlock cctb(content);        // declare constant object
    std::cout << cctb.d_data << "\n";      // calls non-const

    char *pc = &cctb[0];                   // call the const operator[] to get a
                                           // pointer to cctb's data

    //*pc = 'J';                             // cctb now has the value "Jello"
                                           // this results in 'bus error' on OSX
    //std::cout << cctb.d_data << "\n";

    TextBlock textBlock("Good");
    textBlock[0] = 'f';
    std::cout << textBlock.d_data << "\n";
    return 0;
}

```
