# Declare dtors virtual in polymorphic base classes

Declare a virtual destructor in a class if and only if that class contains at least one virtual function. (if it does not, it usually indicates the class is not meant to be inherited from)

The bottom line is that gratuitously declaring all destructors virtual is just as wrong as never declaring them virtual.

It is possible to get bitten by the non-virtual destructor problem even in the complete absence of virtual functions. For example, the standard string type contains no virtual functions, but misguided programmers sometimes use it as a base class anyway:
```cpp
class SpecialString: public std::string {   // bad idea! std::string has a
  ...                                       // non-virtual destructor
};

std::string* ptr = new SpecialString(...);
...
// undefined behavior
delete ptr;
```
The same analysis applies to any class lacking a virtual destructor, including all the STL container types (e.g., vector, list, set, std::unordered\_map.)
Don't inherit from STL container types!

Occasionally it can be convenient to give a class a pure virtual destructor: if you want an abstract class (one that cannot be instantiated) but you don't have any pure virtual functions for it. You could give it a pure virtual dtor, but remember you have to provide a definition for this pure virtual dtor.

```cpp
class AWOV {                            // AWOV = "Abstract w/o Virtuals"
public:
  virtual ~AWOV() = 0;                  // declare pure virtual destructor
};

AWOV::~AWOV() {}                     // definition of pure virtual dtor
```
Reason for needing a definition being when destroying an object of a derived class, the base class's dtor will be called after that of the derived class, and you provide a definition to base class's dtor since otherwise the linker would complain. 

Some classes are designed to be used as base classes, yet are not designed to be used polymorphically.
Such classes — examples include Uncopyable from Item 6, are not designed to allow the manipulation of derived class objects via base class interfaces.
As a result, they don't need virtual destructors.

**Takeaways**
* Polymorphic base classes should declare virtual destructors. If a class has any virtual functions, it should have a virtual destructor
* Classes not designed to be base classes or not designed to be used polymorphically should not declare virtual destructors


Snippet:
```cpp
// declare_dtor_virtual_polymorphic_base_class.m.cpp
#include <iostream>
#include <string>

// demonstrates pure virtual dtors (a minor use case), and undefined behavior 
// in deleting ChildClass object using a BaseClass pointer whose dtor is not
// virtual

class PureVirtualBase {
  public:
    virtual ~PureVirtualBase() = 0;
};

PureVirtualBase::~PureVirtualBase() {}

class ChildPureVirtualBase : public PureVirtualBase {
  public:
    void print() const { std::cout << "ChildPureVirtualBase\n"; }
};

class PolymorphicBase {
  public:
    PolymorphicBase() : d_x(10) {}
    ~PolymorphicBase() { std::cout << "base class dtor\n"; }
    
    virtual void print() { std::cout << d_x << "\n"; }
  private:
    int d_x;
};

class Child : public PolymorphicBase {
  public:
    Child() : d_y(20) {}
    ~Child() { std::cout << "child class dtor\n"; }

    virtual void print() { std::cout << d_y << "\n"; }
  private:
    int d_y;
};

int main() {
    PureVirtualBase* cp = new ChildPureVirtualBase();
    delete cp;

    PolymorphicBase* c = new Child();
    c->print();
    // undefined behavior, dtor of child will not be called
    delete c;
    // it would appear that nothing happens but expect heap to be corrupted
    return 0;
}

```
