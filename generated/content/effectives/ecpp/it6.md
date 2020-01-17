# Explicitly disallow the use of compiler generated functions you don't want

As of C++03, the key to the solution is that all the compiler generated functions are public.
To prevent these functions from being generated, you must declare them yourself, but there is nothing that requires that you declare them public. Instead, declare the copy constructor and the copy assignment operator private.
By declaring a member function explicitly, you prevent compilers from generating their own version, and by making the function private, you keep people from calling it.
And you don't implement it, so that member functions or friends cannot call these private functions.
(Or, you could declare a base class Uncopyable whose copycon and assignment opr are made private, and make your class private inherit from Uncopyable, in which case, when trying to call your class's copycon or assignment opr within a friend, you'd get compiler error instead of linker error, which is preferable.)

This would be obsolete by EMC++ item 11.

**Takeaways**
* To disallow functionality automatically provided by compilers, declare the corresponding member functions private and give no implementations. Using a base class like Uncopyable is one way to do this.


