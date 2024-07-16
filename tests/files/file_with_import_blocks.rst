This is my rst file, which will have some more complex
import blocks.

.. |bing| replace:: bong

.. code-block:: python
    import os

    print(
        f"Hi! This is some info about the current directory:\n"
        f" - Current directory: {os.getcwd()}\n"
    )

Now, let's import something else.

.. code-block:: python
    import sys

    print(f"Python version: {sys.version}")
