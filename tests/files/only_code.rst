.. code-block:: python

    import math


    STANDARD_DEVIATION = 3.14

    def gaussian(*args, std=STANDARD_DEVIATION):
        """Funciton that executes a gaussian function on all of its argument,
        using the Python math library.
        """
        gaussian_values = [math.exp((x/std)**-2) for x in args]

        return gaussian_values
