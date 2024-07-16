This file will contain code blocks that import and use function/method
decorators. For example,

.. code-block:: python

    from functools import cache as my_decorator

    @my_decorator
    def my_function():
        pass

    @my_decorator
    def my_other_function():
        pass

    @my_decorator
    def my_final_function():
        pass

These can also be applied to methods:

.. code-block:: python

    class MyClass:
        @my_decorator
        def my_method(self):
            pass

        @my_decorator
        def my_other_method(self):
            pass

        @my_decorator
        def my_final_method(self):
            pass

And finally, trying a new block importing one used by methods and functions:

.. code-block:: python

    from functools import lru_cache

    @lru_cache
    def my_function():
        pass

    class MyClass:
        @lru_cache
        def my_method(self):
            pass

These should:

- Be included in the output
- Be formatted correctly
- Not raise any errors
