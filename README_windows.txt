Here is how to compile C extensions using Microsoft Visual C++ Compiler for Python 2.7:

    Install Microsoft Visual C++ Compiler for Python from http://www.microsoft.com/en-us/download/details.aspx?id=44266

    Launch MSVC for Python command prompt

        (go to start menu > Microsoft Visual C++ Compiler Package for Python 2.7 > Visual C++ 2008 32-bit or 64-bit Command Prompt)

    Enter the following commands:

        SET DISTUTILS_USE_SDK=1

        SET MSSdk=1

    You can then "cd X:yourpath" to navigate to your Python app and then build your C extensions by entering:

        python.exe setup.py build_ext --inplace --compiler=msvc

    Install the modul by
    	python.exe setup.py install --user