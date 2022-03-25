Evaluation
============

Assessment of Requirements
-----------------------------------------------------------------------------------------------------------------------

#. *API*

    #. *User-orientated*

        #. *The API must function on all supported python versions. As of the time of
           writing, this is Python 3.7 up to 3.10.*

            Through the use of GitHub actions, the tests are run on all these Python versions, and they appear to work
            successfully. It has also been tested locally on different Python versions, and so the PyPi packages officially
            support the specified versions.

            * *This allows more people to be able to run depythel, helping to make it more accessible.*

            This is difficult to test currently since the project is still private, and so not many people
            can currently run the code. However, support for more Python versions is always a bonus, and following
            the publication of the project, I aim to inspect the installation statistics to see which Python
            versions are being used with depythel.

        #. *There must be help documentation available for all public modules and attributes.*

            Docstrings were written for every public method, attribute and module. As part of testing, the documentation was tested
            against `pydocstyle <http://www.pydocstyle.org/en/stable/>`_.

            * *This helps to make depythel easier to use. Without adequate documentation, it would be difficult for new users
              to use depythel effectively.*

            The :ref:`API Reference` provides thorough documentation with examples and various type hints.

        #. *The module must comply with PEP 561 - Distributing and Packaging Type Information*

            To comply with PEP 561, a basic ``py.typed`` `marker file <https://typing.readthedocs.io/en/latest/source/libraries.html#library-interface>`_
            is created in each python module to indicate support for type checking.

            #. *depythel should be fully type-checked, and the types of various attributes/parameters/etc. should be
               available to the user. This can then be used by autocomplete tools such as PyCharm.*

            #. *Its compliance can be checked using mypy. It will be a success if there are no
               errors after running ``mypy --strict`` on the code base.*

            There are indeed no errors after running ``mypy --strict`` on the code base. This test is automated
            as part of GitHub Actions. One thing I didn't appreciate when writing this requirement is that no mypy errors
            doesn't necessarily mean that there are no typing errors whatsoever. However, it is a reasonably good indicator.

        #. *It must be installable via PyPi.*

            * *The user should be able to install the API easily without having to fetch dependencies and build from source.*


            Both the API + CLT and just the API can be installed via PyPi using pip. Building from source will also be available
            when the code is publicised.

    #. *Functionality*

        #. *No third-party dependencies should be required during runtime.*

            The API doesn't require any third-party dependencies to function. The only dependencies used are those that are provided
            with Python itself. Plans are in place to account for changes with the provided Python modules in different Python
            versions (e.g. ``CacheType`` in :ref:`Client-Side Caching` ).

            * *There are all sorts of potential security risks from this, since we don't own the code. However, if
              this API is going to be used by other developers, it needs to be suitably stable and battle tested.*

            * *Security is a particularly important consideration for tools that manage dependencies. See the System Security and Integrity of Data section`
              for more information.*

            * *On a separate note, the command line tool is more likely to be used in less security-intensive environments.
              For this reason, and to help reduce development costs, this policy will not be enforced for the CLT.*

        *To be a success, the modules below should pass a series of fabricated scenarios via unit testing.*

            With ~96% test coverage, a series of test cases were used to check certain edge cases and general usage
            for the various modules described below.

        #. *It must be able to detect cycles in a dependency tree.*

            * *If A and B are dependencies, and A requires B to build and vice versa, that's going to break during
              buildtime.*

            * *depythel aims to detect errors in dependency trees. Since trees are acyclic, cycles count as an error.*

            * *Out of all the features of the proposed solution, this one is likely to be one of the most time
              consuming. This is since circular dependencies break the standard layout of a dependency tree. However,
              it should still be feasible.*

            A ``cycle_check`` module is provided that is able to detect cyclic dependencies. A change was made
            to mark cycles as warnings rather than straight up errors since the depythel program should still
            aim to complete its task to the best of its abilities.

        #. *It must be able to perform topological sorting.*

            * *Dependency trees are normally used to determine what dependencies to install when building a project.
              depythel should be able to determine the correct order to install these dependencies.*

            This is also complete. Warnings are outputted if the dependency tree is incomplete, but depythel will
            output what it considers to be an appropriate topological sorting. At the time of writing, I didn't realise
            that there could be many different valid topological sorting outputs for a given tree. This is accounted
            for in testing by using test cases with only one valid solution.

        #. *depythel must be able to retrieve information from at least three different online repositories.*


            As a start, MacPorts, Homebrew and the AUR are supported. However, it should be easy to add support for
            additional repositories so this could be a future improvement.

            * *Dependency hell can occur in a variety of different environments. depythel should therefore be able
              to work with different repos (e.g. MacPorts, NPM, etc.)*

            * *This is especially important, since the majority of existing implementations only support one repository/language.*

            *"Dependency hell is not technology specific either. I've run into it in the Ruby/Rails ecosystem, in the Clojure
            ecosystem, and in the NodeJS ecosystem. I know folks who have run into it in C++ and Python, too. You name the \
            language, operating system, framework...it's going to happen."*

            -- `John Bintz, Software Engineer at Tidelift
            <https://dev.to/tidelift/dependency-hell-is-inevitable-and-that-s-ok-and-you-re-ok-too-5594>`_

            * *Modular language support is not only important as a USP for depythel, but also since Dependency Hell can happen
              in any language.*

        #. *User-generated trees should be able to use the same modules as trees from online repositories.*


            This was solved by the local tree class inheriting the methods of the online tree class. Since all the different types
            of trees are adjacency lists in the form of dictionaries, this worked quite well.

            * *As part of the API, a third-party developer might want to run the depythel modules on custom dependency trees.*

            * *This feature also allows for depythel to work without internet access, which is useful for reproducibility.*

            * *The user should be able to enter their own tree in as part of both the CLT and the API. The majority of depythel modules
              should then function as if the online repositories were used.*

        #. *There must be some form of dependency visualisation available.*

            JSON was chosen since not only is it very parsable, but this format is what is returned by the online repositories.
            Less work is then required to feed this back to the user.

            * *This might be in the form of parsable JSON output (or some other format). The added benefit of this is that the
              end user can then use the data more efficiently compared to an image.*

        #. *Large dependency trees should have additional fallbacks in place.*

            This is only supported for trees from online repositories. This is since the methods originally thought of below only make
            sense in the context of fetching a tree from online. As a potential improvement, some different requirements could have
            been set for trees created locally. This might have included storing large trees in more memory-efficient data structures.

            * *In reality, dependency trees for large projects can be extremely large and take a long time to generate. Measures
              should be in place to account for this. This should include:*

            * *Generate dependency trees to a depth specified by the user*


            A generator module was implemented to continually generate the dependency tree until the specified depth is met. Since large dependency
            trees would require a lot of memory, generators were chosen over iterators due to their memory efficiency.

                * *The user might only be interested in the first few dependencies. Too many projects in a tree can make it
                  hard to extract information from it.*

            * *Support for caching*

            Only the API calls were cached. It seemed unlikely that the client would run the same methods on the same tree, and
            so caching didn't make much sense anywhere else. Caching the API was done using ``functools.cache``, as anticipated below.

                * *For large projects, cycles are likely to occur. Instead of refetching information about a project from the
                  online repository, some basic caching can speed up the tree generation.*

                * *Reducing the number of API calls also helps to reduce the strain on the servers of the online repositories.*

                * *Efficient solutions exist natively in Python, such as from ``functools.cache``. It therefore seems unnecessary
                  to reinvent the wheel and implement a custom caching function.*

                * *It should be client-side caching and not server-side since the data is not deterministic. Dependencies can be
                  updated frequently and so it would not be wise to cache incorrect information in a database.*

#. *Command Line Tool*

    *Although the Python API is being developed first, a command line tool should still be available for general
    usage. This is especially important for continuous testing integration, where a CLT can be easily added.*

    #. *It should provide at least the same feature set as the API.*

        We went a bit further and actually expanded on the feature set of the API. Since we were allowed to use third party
        dependencies here, this allowed us to add some additional functionality.

        * *Although the CLT is designed with more novice users in mind, it should not be a watered down version of the API.
          They should both have the same core functionality.*

    #. *Similar to the API, some form of dependency visualisation should be available.*

        Since the CLT is essentially a user-friendly wrapper of the API, supporting JSON visualisation was straightforward. In addition,
        an interactive HTML file was provided that allowed users to have a better understanding of the dependency tree.

        * *For the CLT, where the end users are less experienced, an interactive tree might be a more beneficial form of
          visualisation.*

        * *To be a success, there should be at least two forms of possible output available, so as to give the users choice.*

#. *Unit Testing*

    *Unit tests provide a useful way of determining whether the code base works as intended. To pass this criteria,
    there must be the following*

        The below requirements were both thoroughly described in :ref:`Testing` . Automated testing was provided via GitHub Actions,
        with a Makefile helping to simplify this process. Codecov and pytest were used to test for >= 95% test coverage.

    * *Automated Testing*

        * *This would provide a useful way to determine whether recent changes work as expected.*

        * *This could be in the form of a GitHub actions workflow, which could test newly uploaded commits.*

    * *>= 95% Test Coverage*

        * *A high test coverage is essential for making sure the code is properly tested and functions as expected.*

        * *In terms of being a success, this is pretty self-explanatory. It must pass this percentage in terms of coverage.*

Some of the feedback received during the analysis stage included the following:

* Provide an interactive form of visualisation.
  
    * This was part of our original set of requirements, and has been implemented as part of the commnd line tool.

* Fully document the API.

      * Again, this also inspired a section in the original set of requirements. Through the use of docstrings, which allows
        us to generate HTML/PDF documentation, this has also been completed.

* Separate the API and the CLT into two separate Python packages.

     * This wasn't part of the requirements, but was considered when planning out the file structure during the design stage.
       As such, they are indeed now two different modules so that the third-party dependencies of the CLT don't need to be installed
       to run the API.

Improvements
--------------

Although I wasn't able to contact the same MacPorts members as I had during the :ref:`Analysis` , I was able to get in touch
with two different members. One of them mentioned that it would have been useful if JSON files could be read and parsed, rather than just JSON text.
This would make depythel more flexible in the types of input it could accept. The feature would, in theory, be
relatively straightforward to implement. The file could be read using either a dedicated json module, or
it could be manually converted into a dictionary by treating it as a text file.

When re-reading the `pyvis documentation <https://pyvis.readthedocs.io/en/latest/tutorial.html#example-visualizing-a-game-of-thrones-character-network>`_,
I noticed that one of the example projects set the size and colour of the nodes depending on how far away it is from the root
project.

.. image:: art/docs_graph.png

This would be a nice feature to have to make it clearer which dependencies are further down the tree. Since the source code
for this feature is available in the documentation, it shouldn't be too difficult to implement.

Another member mentioned that they would've liked support for some more online repositories, and that the currently implemented
set had a very macOS focus. Fortunately, thanks to the modular repository support as described in :ref:`Fetching Dependencies`, this
shouldn't be too difficult to do. The focus should be on more Linux-based package managers.

Finally, they also mentioned that they would've liked a progress bar for the command line tool when generating the JSON.
Fortunately, the ``rich`` library used in the CLT has a progress display module that can be used to complete this task.

.. code-block:: python

    # From https://rich.readthedocs.io/en/stable/progress.html

    from rich.progress import track

    for n in track(range(n), description="Processing..."):
        do_work(n)

Conclusion
------------

This project has been a great success, and has managed to reach the vast majority of the requirements specification. With some
further support for more online repositories, and some additional tree analysing modules, it could hopefully be a useful tool for many developers and general
users alike.
