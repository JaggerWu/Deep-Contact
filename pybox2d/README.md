pybox2d*
-------
This is a modified version of pybox2D. The original can be found at:

https://github.com/pybox2d/pybox2d

What has changed:
-----------
It is now possible to manually specify a threshold for when the iterative
constraint solver might stop iterating, rather than simply always doing the
maximum number of iterations. This is done through two new parameters,
specified on a per-world basis.
The first new parameter, 'velocityThreshold', determines what threshold to
use for early stopping when solving the velocity constraints, and the second
new parameter, 'positionThreshold', similarly determines what threshold to
use for early stopping when solving the position constraints.
These two new parameters does not need to be set manually, and will by default
be set such that the simulator behaves in the same way as the unmodified version.
Note that the thresholds only consider positions and velocities. Angles and
angular velocities are currently not considered.

Another change is that the b2Profile class, of which an instance is created
after each step, now has three additional attributes.
'velocityIterations' is the total number of iterations performed solving the
velocity constraints.
'positionIterations' is the total number of iterations performed solving the
position constraints.
'contactsSolved' is the total number of contacts considered when solving the
constraints. Note that this number will often be different from the total
number of contacts in the world, and might even be different from the total
number of contacts in the world for which 'touching' is true.