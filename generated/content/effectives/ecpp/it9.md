# Never call virtual functions during ctor or dtor

Suppose you have this code.
```cpp
class Transaction {                               // base class for all
public:                                           // transactions
  Transaction();

  virtual void logTransaction() const = 0;       // make type-dependent
                                                 // log entry
  ...
};

Transaction::Transaction()                        // implementation of
{                                                 // base class ctor
  ...
  logTransaction();                               // as final action, log this
}                                                 // transaction

class BuyTransaction: public Transaction {        // derived class
public:
  virtual void logTransaction() const;          // how to log trans-
                                                // actions of this type
  ...
};
class SellTransaction: public Transaction {      // derived class
public:
virtual void logTransaction() const;            // how to log trans-
                                                // actions of this type
  ...
};

// consider what happens when this is executed:
BuyTransaction b;
```
Base class ctor would have to be called first:
The version of logTransaction that's called is the one in Transaction, not the one in BuyTransaction — even though the type of object being created is BuyTransaction.

During base class construction, virtual functions never go down into derived classes. Instead, the object behaves as if it were of the base type.
The reason for such is that while base class ctor is being called, derived class members aren't initialized yet. If we do call into derived class's overriden functions then we'd run into undefined behavior when those functions refer to members of the derived class.

Actually, during base class construction of a derived class object, the type of object is that of the base class.
Not only do virtual functions resolve to those of the base class, but also parts of the language using runtime type information (e.g., dynamic_cast and typeid) treat the object as a base class type: during base class ctor, the derived part does not exist yet, so it's best to treat the object's type as that of the base.
An object doesn't become a derived class object until execution of a derived class constructor begins.

The same reasoning applies during destruction.
Once a derived class destructor has run, the object's derived class data members assume undefined values, so C++ treats them as if they no longer exist.
Upon entry to the base class destructor, the object becomes a base class object, and all parts of C++ — virtual functions, dynamic_casts, etc., — treat it that way.

In the above example code's case, it shouldn't link as logTransaction in base class is pure virtual.
Some compilers would also issue warnings about this.

This more insidious version, however, will likely compile and link:
```cpp
class Transaction {
public:
  Transaction()
  { init(); }                                      // call to non-virtual...

  virtual void logTransaction() const = 0;
  ...

private:
  void init()
  {
    ...
    logTransaction();                              // ...that calls a virtual!
  }
};
```
The only way to avoid this problem is to make sure that none of your constructors or destructors call virtual functions on the object being created or destroyed and that all the functions they call obey the same constraint.

How do we achieve what we wanted to do then?
One way is to not make logTransaction virtual, but rather parameterize the information it needs.
Like this
```cpp
class Transaction {
public:
  explicit Transaction(const std::string& logInfo);

  void logTransaction(const std::string& logInfo) const;   // now a non-
                                                           // virtual func
  ...
};

Transaction::Transaction(const std::string& logInfo)
{
  ...
  logTransaction(logInfo);                                // now a non-
}                                                         // virtual call

class BuyTransaction: public Transaction {
public:
BuyTransaction( parameters )
: Transaction(createLogString(parameters ))             // pass log info
  { ... }                                               // to base class
   ...                                                  // constructor

private:
  static std::string createLogString( parameters );
};
```
Note the private static function createLogString, using a helper function like this is often more readable, and making it avoids accidentally using the data members of BuyTransaction in createLogString, whose uninitialized state is the reason why we parameterize the message in the first place.

**Takeaways**
* Don't call virtual functions during construction or destruction, because such calls will never go to a more derived class than that of the currently executing constructor or destructor


Snippet:
```cpp
// never_call_virtual_functions_inside_ctor_dtor.m.cpp
#include <iostream>
#include <string>
#include <sstream>

// demonstrates a way to avoid calling virtual functions in ctor

class Transaction {
public:
  Transaction(const std::string& msg) {
    // you may be tempted to make logTransaction virtual and overridden
    // in both children below, to print their corresponding messages!
    // Don't! As if you do, here it'll always call the base class's
    // logTransaction!
    logTransaction(msg);
  }

  virtual ~Transaction() = 0;
private:
  void logTransaction(const std::string& msg) {
    std::cout << msg << "\n";
  }
};

Transaction::~Transaction() {}

class BuyTransaction : public Transaction {
public:
  BuyTransaction() : Transaction(getTypeMessage()) {}
private:
  static std::string getTypeMessage() {
    return "one buy transaction";
  }
  int d_size;
};

class SellTransaction : public Transaction {
public:
  SellTransaction(int size) : Transaction(getTypeMessage(size)) {}
private:
  static std::string getTypeMessage(int size) {
     std::stringstream ss;
     ss << "one sell transaction of size " << size;
     return ss.str();
  }
  int d_size;
};

int main() {
  BuyTransaction  bt;
  SellTransaction st(20);
  return 0;
}

```
