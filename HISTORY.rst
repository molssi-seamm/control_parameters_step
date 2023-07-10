=======
History
=======

2023.7.10: Bugfix handling parameters with 0+ values

   * The default was not correctly handled for control parameters with 0+ arguments,
     where they need to be a list.
     
2023.1.23: Fixed issue with  parameters with '_'
------------------------------------------------

* Fixed issue with '-' and '_' in parameter/variable names

* Revamped documentation to the new MolSSI style and diátaxis layout.

* (internal) Moved from LGTM to GitHub CodeQL for code quality analysis

2022-6-6: Fixed bugs when editing parameters
--------------------------------------------

* Also added button to remove a parameter.

2022.2.9: Added 'files' to parameter types
------------------------------------------

* Added 'files' to parameter types. Needed for job submission

2021.10.13: Cleaned up the GUI
------------------------------

* Made the dialog larger

* Show all parameters

* Made appropriate comboboxes read only

2021.6.3: Update for internal change in argument parsing
--------------------------------------------------------

* Updated for the SEAMM argument parser moving to seamm_util

2021.2.9: Improved description for the installer
------------------------------------------------

* Added to the README text, and made it conform to the standard style

2020.12.4: First working release
--------------------------------

Adds functionality to SEAMM for specifying key control parameters, items such as the
structure, temperature, and pressure, and use them as command-line parameters. In the
future, we will also provide the ability to set them when submitting a flowchart from
the Python or web interfaces.

0.1 (2020-10-06)
------------------

* First release on PyPI.
