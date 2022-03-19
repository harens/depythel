Analysis
=======================================================================================================================

Problem Area
-----------------------------------------------------------------------------------------------------------------------

Dependency resolution is a particularly important consideration in package management and distribution. Users simply
want programs to build and run as expected, and build failures due to conflicting dependencies can cause them a great
frustration. Not only does it waste the user's time, but also that of the maintainers, since they are then required to
deal with the resulting issue ticket requests.

An example of this is from the open-source text editor `lite-xl <https://lite-xl.github.io/>`_, which this document was
(partly) written in. Some users were `having trouble with its lua dependency <https://github.com/lite-xl/lite-xl/issues/3>`_,
since it required specifically version 5.2. It would then fail to build if it wasn't found:

.. code-block:: console

    meson.build:7:0: ERROR: Dependency "lua5.2" not found, tried pkgconfig, framework and cmake

Another example of dependency conflicts are circular dependencies. If dependency *A* depends on *B*, and *B* depends on
*A*, this can cause errors during buildtime. Alternatively, maybe there are so many dependencies, that the user is fed
up of waiting for them to finish downloading.

This problem area is something most developers don't even think about. As important as developing a good project is,
it's arguably even more useful to make sure that users can even run it in the first place. That's where depythel comes
in.

Client/End User
-----------------------------------------------------------------------------------------------------------------------

The majority of existing implementations for dependency resolution are end user orientated. As an example, package
managers will alert the user when a project fails to build.

depythel will instead take the approach of focusing on the developer, and acting as an easy-to-use continuous testing
tool. It will be developed as a Python API first, so that programmers can configure the tool as they see fit. This would
require a higher level of expertise in the area, and so for more novice users, a pre-configured command line tool will
also be provided. This can then be easily integrated into existing workflows.

Research methodology
-----------------------------------------------------------------------------------------------------------------------

The idea to choose a dependency conflict management project came from my experience in package managers. As a project
member at `MacPorts <https://www.macports.org/>`_, one of the issues we face is how to deal with things such as
circular dependencies. A language-agnostic tool to check for this would therefore be very beneficial. As a result, part
of my research comes from real world experience with trying to deal with this problem on a platform with thousands of
users.

I also did some online research on existing solutions for dependency conflicts, and determined some of their advantages
and drawbacks:

Poetry
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. figure:: art/poetry-logo.jpg
  :width: 70
  :align: right
  :alt: Poetry package manager logo

`Poetry <https://python-poetry.org/>`_ is a Python package manager, which depythel ironically uses itself behind the
scenes to manage its own dependencies. If there exists a solution to a dependency conflict, it will find it. In this regard, it
is a much more stable and polished tool than depythel.

However, it is Python-specific, whilst depythel aims to support a variety of languages and package managers in a
simple, modular fashion. Poetry is also a general package manager, and doesn't focus specifically on aspects like
dependency visualisation. In this regard, if all you're looking for is generic dependency management, depythel aims to be a more apt tool.

.. figure:: art/poetry-tree.png

    The dependency tree of depythel CLT, generated via poetry.

System Package Managers
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Virtually all mature package managers provide some form of dependency conflict management. They are then able
to warn you as the user why it was not able to install a program.

depythel aims instead to be a tool predominantly for developers, rather than the end user. As such, it's built in such
a way to allow configurability and easy adoption into workflows.

Visualisation Tools
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. figure:: https://raw.githubusercontent.com/naiquevin/pipdeptree/master/docs/twine-pdt.png

   Visualising the dependency tree of a project using ``pipdeptree``.

Visualisation tools, such as the one present in the `Haskell Tool Stack
<https://docs.haskellstack.org/en/stable/dependency_visualization/>`_, provide a visual way of showing a developer the
dependencies of their project.

With minor exceptions, like `pipdeptree <https://github.com/naiquevin/pipdeptree>`_, they don't normally warn the user
or errors in the dependency tree itself. They also usually support only one language. Depythel aims to not only warn of
potential misconfigurations, but also to support a variety of online language repos.

Features of proposed solution / Requirements specification
-----------------------------------------------------------------------------------------------------------------------

#. **Modular Language Support**

    * It should be simple to add support for different language repositories (e.g. MacPorts, NPM)...

        * This is especially important, since the majority of existing implementations only support one repository/language.

    * This will be a success if data can be successfully extracted out of at least three different language
      repos.

    * Modular language support is not only important as a USP for depythel, but also since Dependency Hell can happen
      in any language.

    "Dependency hell is not technology specific either. I've run into it in the Ruby/Rails ecosystem, in the Clojure
    ecosystem, and in the NodeJS ecosystem. I know folks who have run into it in C++ and Python, too. You name the \
    language, operating system, framework...it's going to happen."

    -- `John Bintz, Software Engineer at Tidelift
    <https://dev.to/tidelift/dependency-hell-is-inevitable-and-that-s-ok-and-you-re-ok-too-5594>`_

#. **Command Line Tool**

    * Although the Python API is being developed first, a command line tool should still be available for general
      usage. This is especially important for continuous testing integration, where a CLT can be easily added.

    * Although the CLT is designed with more novice users in mind, it should not be a watered down version of the API.
      Therefore, it will be a success if it has the same or an improved feature set compared to the API (i.e. it shares the same core
      functionality).

#. **Detect possible conflicts to a dependency depth specified by the user**

    * To be a success, it should be able to detect at least the following conflicts to a dependency depth specified by
      the user:

        * Circular dependencies

            * If *A* and *B* are dependencies, and *A requires B* to build and vice versa, that's going to break during
              buildtime.

            * Out of all the features of the proposed solution, this one is likely to be one of the most time
              consuming. This is since circular dependencies break the standard layout of a dependency tree. However,
              it should still be feasible.

        * Incompatible versions


            * If *A.1* and *A.2* are both required somewhere in the dependency tree, they can't be installed at the
              same time. This can be detected by noting the number on the end of the dependency.

      * Long dependency chains/Too many dependencies


            * Although not an error, this can result in a lot of disk space being required to install the program, and
              it can take a long time to install.

#. **Support user-generated trees**

    * As part of the API, a third-party developer might want to run the depythel modules on custom dependency trees.

    * This also allows for depythel to work without internet access, which is useful for reproducibility.

    * The user should be able to enter their own tree in as part of both the CLT and the API. The majority of depythel modules
      should then function as if the online repositories were used.

#. **Implement contingency plans for large dependency trees**

    * In reality, dependency trees for large projects can be extremely large and take a long time to generate. Measures
      should be in place to account for this. This should include:

        * **Generate dependency trees to a depth specified by the user**

            * The user might only be interested in the first few dependencies. Too many projects in a tree can make it
              hard to extract information from it.

        * **Support for caching**

            * For large projects, cycles are likely to occur. Instead of refetching information about a project from the
              online repository, some basic caching can speed up the tree generation.

                * Reducing the number of API calls also helps to reduce the strain on the servers of the online repositories.

            * Efficient solutions exist natively in Python, such as from ``functools.cache``. It therefore seems unnecessary
              to reinvent the wheel and implement a custom caching function.

            * It should be client-side caching and not server-side since the data is not deterministic. Dependencies can be
              updated frequently and so it would not be wise to cache incorrect information in a database.

#. **Provide some form of dependency visualisation**

    * This might be in the form of parsable JSON output (or some other format). The added benefit of this is that the
      end user can then use the data more efficiently compared to an image.

    * For the CLT, where the end users are less experienced, an interactive tree might be a more beneficial form of
      visualisation.

    * To be a success, there should be at least two forms of possible output available, so as to give the users choice.

#. **Unit Testing**

    Unit tests provide a useful way of determining whether the code base works as intended. To pass this criteria,
    there must be the following

    * **Automated Testing**

        * This would provide a useful way to determine whether recent changes work as expected.

        * This could be in the form of a GitHub actions workflow, which could test newly uploaded commits.

    * **>= 95% Test Coverage**

        * A high test coverage is essential for making sure the code is properly tested and functions as expected.

        * In terms of being a success, this is pretty self-explanatory. It must pass this percentage in terms of coverage.

Critical Path
-----------------------------------------------------------------------------------------------------------------------

Although many of the tasks can be carried out in conjunction with each other, some tasks need to be completed before
others can begin. The diagram shows a critical path with a general overview of the jobs to complete.

.. figure:: art/critical_path.png

Initialising the repository modules is especially important since it provides the foundation for building the
dependency tree. Following this, various tree-orientated functionality can be written.

The command line tool acts as a frontend for the API, and so can only be implemented following the API's completion.

Throughout the process, unit tests should be written to ensure that the code base works as expected.
