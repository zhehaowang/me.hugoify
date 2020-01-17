# Prevent exceptions from leaving dtors

Consider this code.
```cpp
class Widget {
public:
  ...
  ~Widget() { ... }            // assume this might emit an exception
};

void doSomething()
{
  std::vector<Widget> v;
  ...
}                                // v is automatically destroyed here
```
If an exception is thrown when the first element in v is destroyed, C++ has to finish destroying all the remaining Widgets in v, say another exception is thrown then, we'll have two exceptions at the same time, which is not allowed in C++ and causes undefined behavior or program termination.

What if your dtor needs to perform an action that might fail and cause an exception to be thrown?
Suppose you have this class for DBConnection
```cpp
class DBConnection {
public:
  ...

  static DBConnection create();        // function to return
                                       // DBConnection objects; params
                                       // omitted for simplicity

  void close();                        // close connection; throw an
                                       // exception if closing fails
  
  // and you want to have an RAII class that closes connection on dtor
  ~DBConn()                            // make sure database connections
  {                                    // are always closed
    db.close();
  }
};
```
There are two primary ways to solve this issue:
One is to terminate the program if close throws, by calling abort
```cpp
DBConn::~DBConn() {
  try {
    db.close();
  } catch (...) {
    // make log entry that the call to close failed;
    std::abort();
  }
}
```
This is reasonable if the program cannot continue to run after an exception is encountered during destruction.
Calling abort forestalls undefined behavior.

The other is to swallow it.
```cpp
DBConn::~DBConn() {
  try {
    db.close();
  } catch (...) {
    // make log entry that the call to close failed;
  }
}
```
In general, suppressing exception is a bad idea, since it suppresses the important information that something failed.
However, in this case this would still be preferable to undefined behavior or premature termination.
For this to be viable, the program must be able to continue execution even if an error occurred and has been ignored.

Neither way is ideal.
In this case we could expose close to clients so that they have a chance of handling exceptions from close operation.
And if the client doesn't do it, we still fall back to aborting or swallowing.
```cpp
class DBConn {
public:
  ...

  void close()                                     // new function for
  {                                                // client use
    db.close();
    closed = true;
  }

  ~DBConn() {
    if (!closed) {
      try {                                            // close the connection
        db.close();                                    // if the client didn't
      } catch (...) {                                    // if closing fails,
        make log entry that call to close failed;      // note that and
        ...                                            // terminate or swallow
      }
    }
  }

private:
  DBConnection db;
  bool closed;
};
```

Does this violate the principle of making interfaces easy to use?
We would argue not as in this example, telling clients to call close themselves gives them an opportunity to deal with errors they would otherwise have no chance to react to.
And if they don't want to deal with it, they'd still fall back on the dtor's default action.

**Takeaways**
* Destructors should never emit exceptions. If functions called in a destructor may throw, the destructor should catch any exceptions, then swallow them or terminate the program
* If class clients need to be able to react to exceptions thrown during an operation, the class should provide a regular (i.e., non-destructor) function that performs the operation


Snippet:
```cpp
// prevent_exceptions_from_leaving_dtor.m.cpp
#include <iostream>
#include <string>

// demonstrates an RAII class design where dtor may call an operation that throws
// but dtor handles it by swallowing. That is, only if client does not first call
// this operation that could throw in order to handle the exception.

class DBConn {
  public:
    DBConn() : d_handle(-1), d_isOpen(false) {}
    
    void open(int handle) {
      d_handle = handle;
      d_isOpen = true;
    }

    void close() {
      if (d_isOpen && d_handle > 10) {
        throw std::runtime_error("blow up");
      }
      d_isOpen = false;
    }

    ~DBConn() {
      if (d_isOpen) {
        try {
          close();
        } catch (...) {
          std::cout << "exception swallowed in dtor\n";
        }
      }
    }
  private:
    int  d_handle;
    bool d_isOpen;
};

int main() {
    DBConn conn;
    conn.open(11);
    const bool clientCares = true;

    if (clientCares) {
      // client is given the opportunity to handle this exception
      try {
        conn.close();
      } catch (const std::exception& e) {
        std::cout << "Client handles: " << e.what() << "\n";
      }
    } else {
      // or if client does not care, exception won't leave dtor
    }
    return 0;
}

```
