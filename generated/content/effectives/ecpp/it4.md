# Make sure objects are initialized before they are used

If you see this
```cpp
int x;
// in some contexts, x will be initialized with 0, in others, x won't

class Point { int x, y; }
Point point;
// in some contexts, point will be initialized with 0s, in others, point won't
```
Reading uninitialized values yields undefined behavior. More often, reading them will result in semi-random bits.

The rules for when they are and when they aren't could be too complicated to be worth remembering: in general, if you're in the C part of C++ (see Item 1) and initialization would probably incur a runtime cost, it's not guaranteed to take place. If you cross into the non-C parts of C++, things sometimes change. This explains why an array (from the C part of C++) isn't necessarily guaranteed to have its contents initialized, but a vector (from the STL part of C++) is.

The best way to deal with this seemingly indeterminate state of affairs is to always initialize your objects before you use them.
For non-member objects of built-in types, do this manually:
```cpp
int x = 0;                                // manual initialization of an int

const char * text = "A C-style string";   // manual initialization of a
                                          // pointer (see also Item 3)

double d;                                 // "initialization" by reading from
std::cin >> d;                            // an input stream
```
For almost everything else, do this in ctors.
Don't confuse member initialization list with assignments.
Member initialization list will often be more efficient as they do a default ctor call (wasted) + copy assignment, as opposed to just one copycon call.
Also sometimes member initialization list has to be used, e.g. data members that are const or references.
Sometimes when multiple ctors have to duplicate the same member initialization lists and are undesirable, in which case we could use the assignment approach and make them call one function that does the assignment. But in general, always prefer the member initialization list.

The order in which an object's data is initialized is defined: base class before derived class, and within a class, data members are initialized in the order they are declared. This is true even if member initialization list has a different order.
To avoid confusion, always list the declaration and the member initialization list in the same order.

And now on to the order of initialization of non-local static objects defined in different translation units.

Firstly, a static object is one that exists from the time it's constructed until the end of the program.
Stack and heap-based objects are thus excluded. Included are global objects, objects defined at namespace scope, objects declared static inside classes, objects declared static inside functions, and objects declared static at file scope.

Static objects inside functions are known as local static objects (because they're local to a function), and the other kinds of static objects are known as non-local static objects. Static objects are automatically destroyed when the program exits, i.e., their destructors are automatically called when main finishes executing.

The relative order of initialization of non-local static objects defined in different translation units is undefined.
What if you want to control the order of their initialization then? Make them local instead: have a function call that instantiates them and return the static objects (like a singleton pattern). E.g.
```cpp
// we used to have two global static variables in different translation units:
// file system, and a temp directory.
// the temp directory depends on the file system global static variable being
// instantiated first.
// now since the sequence would be undefined, we make both function-local static
// instead, and make sure file system function is always called before temp directory
// function.  

class FileSystem { ... };           // as before

FileSystem& tfs()                   // this replaces the tfs object; it could be
{                                   // static in the FileSystem class

  static FileSystem fs;             // define and initialize a local static object
  return fs;                        // return a reference to it
}

class Directory { ... };            // as before

Directory::Directory( params )      // as before, except references to tfs are
{                                   // now to tfs()
  ...
  std::size_t disks = tfs().numDisks();
  ...
}

Directory& tempDir()                // this replaces the tempDir object; it
{                                   // could be static in the Directory class

  static Directory td;              // define/initialize local static object
  return td;                        // return reference to it
}

// tempDir() and tfs() are both good candidates for inlining.
// another concern is as-is there is the possibility of multi-threaded call on
// functions that instantiate static variables.
// to avoid this, we could call both functions in main first.
```

Thus, to avoid using objects before they are initialized, you need to do
* first, manually initialize non-member objects of built-in types
* then, use member initialization lists to initialize all parts of an object
* finally, design around the initialization order uncertainty that afflicts non-local static objects defined in separate translation units

**Takeaways**
* Manually initialize objects of built-in type, because C++ only sometimes initializes them itself
* In a constructor, prefer use of the member initialization list to assignment inside the body of the constructor. List data members in the initialization list in the same order they're declared in the class
* Avoid initialization order problems across translation units by replacing non-local static objects with local static objects

Snippet:
```cpp
// depends_on_my_class.cpp
#include <my_class.h>

DependsOnMyClass& getGlobalDependsOnMyClass() {
    static DependsOnMyClass dependsOnMyClass(getGlobalMyClass().d_x);
    return dependsOnMyClass;
}

// my_class.h
#ifndef INCLUDED_MY_CLASS
#define INCLUDED_MY_CLASS

#include <iostream>
#include <string>

// we want a translation-unit scope instance of MyClass and DependsOnMyClass, and 
// we want to make sure MyClass is always instantiated first

class MyClass {
  public:
    MyClass() : d_x(10) {
        std::cout << "MyClass ctor\n";
    }

    int d_x;
};

class DependsOnMyClass {
  public:
    DependsOnMyClass(int y) : d_y(y) {
        std::cout << "DependsOnMyClass ctor\n";
    }

    int d_y;
};


DependsOnMyClass& getGlobalDependsOnMyClass();

MyClass& getGlobalMyClass();

#endif
// my_class.cpp
#include <my_class.h>

MyClass& getGlobalMyClass() {
    static MyClass myClass;
    return myClass;
}

// initialize_object_before_use.m.cpp
#include <iostream>
#include <string>
#include <my_class.h>

// demonstrates enforcing certain order in initializing non-local static variables in different translation units

int main() {
  std::cout << "main called\n";
  std::cout << getGlobalDependsOnMyClass().d_y << "\n";
  return 0;
}

```
