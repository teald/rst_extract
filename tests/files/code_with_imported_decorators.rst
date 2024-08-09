This file will contain code blocks that import and use function/method
decorators. For example,

.. code-block:: python

    from functools import cache as my_decorator

    @my_decorator
    def my_function():
        return True

    @my_decorator
    def my_other_function():
        return True

    @my_decorator
    def my_final_function():
        return True

    for func in [my_function, my_other_function, my_final_function]:
        print(f"{func.__name__}() -> {func()}")
        # For testing the wrapping occurred appropriately
        print(
            f"{func.__name__}.__wrapped__.__name__ -> "
            f"{func.__wrapped__.__name__}"
        )

        assert func() is True


These can also be applied to methods:

.. code-block:: python

    class MyClass:
        @my_decorator
        def my_method(self):
            return True

        @my_decorator
        def my_other_method(self):
            return True

        @my_decorator
        def my_final_method(self):
            return True

    # Same testing as above
    my_instance = MyClass()
    for method in [
        my_instance.my_method,
        my_instance.my_other_method,
        my_instance.my_final_method,
    ]:
        print(f"{method.__name__}() -> {method()}")
        print(
            f"{method.__name__}.__wrapped__.__name__ -> "
            f"{method.__wrapped__.__name__}"
        )

        assert method() is True

And finally, trying a new block importing one used by methods and functions:

.. code-block:: python

    from functools import lru_cache

    @lru_cache
    def my_function():
        return True

    class MyClass:
        @lru_cache
        def my_method(self):
            return True

    my_instance = MyClass()
    for func in [my_function, my_instance.my_method]:
        print(f"{func.__name__}() -> {func()}")
        print(
            f"{func.__name__}.__wrapped__.__name__ -> "
            f"{func.__wrapped__.__name__}"
        )

        assert func() is True

These should:

- Be included in the output
- Be formatted correctly
- Not raise any errors
