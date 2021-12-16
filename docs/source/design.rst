Design
=======================================================================================================================

High Level Overview
-----------------------------------------------------------------------------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Inputs

     - Processes
     - Storage
     - Outputs
   * - Dependency Name

     - Build and Traverse Dependency Tree
     - Maybe some form of caching? This is risky since the data likely isn't
       deterministic.
     - Some form of image visualisation (e.g. image file, terminal output)
   * - Package Manager

     - Detect cycles in the tree
     - 
     - Text-based API output
   * - Number of levels to traverse

     - Visualising tree
     -
     -
   * - 

     - Other user API processes (e.g. building dependency priority queue)
     -
     -

Please see the :ref:`API Reference` for a more detailed code-based overview of the project.

Description of Data Structures
-----------------------------------------------------------------------------------------------------------------------

Directed Graph
***********************************************************************************************************************

A directed graph is required to store what projects each program depends on. At first, an adjacency graph was
considered since it is very easy to implement and it represents directed graphs well.

However, an adjacency list is likely to be better suited since the dependency graph is likely to be quite sparse, and
so a list will provide a better space complexity. It's also easy to build depending on the repository's API.

Priority Queue
***********************************************************************************************************************

depythel aims to be an API first and foremost, so that endusers can design their own interfaces based on the tools we
provide. To do so effectively, a priority queue showing the order of dependencies in a tree should be provided.

This will be done via bredth-first traversal down the dependency tree, so that the dependencies of dependencies can be
placed in the correct ordering. See below for more details.

Description of Algorithms
-----------------------------------------------------------------------------------------------------------------------

Breadth-First Traversal
***********************************************************************************************************************

Since dependency trees can be extremely large, the user can enter how far down the tree they want to generate. So as to
implement this level functionality, the tree/priority queue will be built using a breadth-first approach.

Cyclic-Dependency Checking
***********************************************************************************************************************

This can be done whilst building the tree. Based on the `following
<https://trykv.medium.com/algorithms-on-graphs-directed-graphs-and-cycle-detection-3982dfbd11f5>`_, we can mark certain
nodes as *visited* if we have visited all of their children, and *exploring* if it's on our current path. Whilst
traversing, if we reach an *exploring* node, that means we have reached an earlier point on our trail and we have a
cycle.

.. figure:: art/Cyclic-Flowchart.png
   :width: 400
   :align: center
   :alt: Cyclic Dependency Algorithm Flowchart

   Flowchart demonstrating the intended functionality of the cyclic dependency algorithm.

Codebase Design
-----------------------------------------------------------------------------------------------------------------------

For each package repository, there should be the option to retrieve the dependencies from online of locally (or both).
By implementing this in a modular fashion, this should make it easier to support different package managers.

Online
***********************************************************************************************************************

If the package manager provides an online API, the dependencies can be retrieved via the requests package.

Benefits:

* It does not require that the user has installed the package manager locally. This therefore leads to greater
  OS/machine independency.
* The API should be the more up-to-date that local installation records, and so the dependency graph is more likely to
  be correct.
* Fewer security concerns since we are not interacting with the user's package manager.

Local
***********************************************************************************************************************

Most likely, this will involve calling the package manager via the subprocess library and extracting its output. Since
the majority of package managers do not provide a simple API, this is likely to be the most common option.

Benefits:

* In some scenarios (dependending on the implementation), this should be quicker than the online approach since
  everything is done locally.
* Wifi access is not required.
* Increased reproducibility.

Design of User Interface
-----------------------------------------------------------------------------------------------------------------------

Command Line Interface
***********************************************************************************************************************

As discussed in the :ref:`Analysis`, although the depythel API is the main priority, it would also be useful to provide
some form of a command line interface. Preferably, `typer <https://github.com/tiangolo/typer>`_ would have been used to
provide this. This is since depythel takes `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_ compatability very
seriously, and typer provides many additional benefits for this.

However, as of the time of writing, it seems to be unmaintained. Therefore, `click
<https://palletsprojects.com/p/click/>`_ has been chosen instead for the following reasons:

* It generates help page documentation automatically
* Integrates very well with `rich <https://rich.readthedocs.io/en/stable/introduction.html>`_, which can allow for
  improved formatting of the user interface.
* Very readable and well documented

Data Validation
***********************************************************************************************************************

`Beartype <https://github.com/beartype/beartype>`_ has been chosen to help validate user inputs, which is particularly
important considering that a public API will be made available. This library has been chosen for the following reasons:

* It provides O(1) runtime type checking.
* No runtime dependencies
* It allows defining custom types, such as an integer that has to be exactly two to six digits long.

As such, it should provide more than enough functionality so that a user does not accidentally break a function
depending on their input.
