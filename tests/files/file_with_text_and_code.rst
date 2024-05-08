..
    This more complicated file contains comments, code, and code in comments.

    The final comment of this file, which has the label "#~END~#", is the
    solution expected for this file, per the library standard. For more
    details, see TESTING.md.

This is an example file with a few different things going on. Firstly, there's
this text, but there's actually some other nuances too:

1. There's an enumerated list here
    + with a sub-item
    + and another sub-item
2. And another item here
3. And a final item here

There's also some code here:
.. code-block:: python

    def some_function():
        # This is a comment
        return "This is a string"

And there's some code in a comment here:

..
    .. code-block:: python

        def some_other_function():
            # This is a comment
            return "This is a string"

Ideally, the comment above will not be included in the output, but the code
block that's uncommented will be. That is, unless comments are meant to be
included in output.

There's a final code block here, which has an option:

.. code-block:: python
    :linenos:

    def some_final_function():
        # This is a comment
        return "This is a string"


..
    Below this line is the expected output for this file.
    #~END~#

    # Block 1
    def some_function():
        # This is a comment
        return "This is a string"

    # Block 2
    def some_final_function():
        # This is a comment
        return "This is a string"
