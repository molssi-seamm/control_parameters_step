.. _user-guide:

**********
User Guide
**********
The Control Parameters plug-in allows you to define parameters that control steps in the
flowchart, such as the temperature for dynamics. You can change these parameters when
you run the flowchart. From the command-line the parameters are added as arguments after
the flowchart. If submitting from the SEAMM GUI, there is a table of the parameters
where you can change their values.

Names you cannot use
====================
Each parameter becomes a command-line option of the job, ``--<name>``, beside SEAMM's
own options for the job. A parameter therefore cannot have the name of one of them:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Name
     - SEAMM's option
   * - ``memory``, ``ncores``, ``parallelism``
     - The memory and cores any step may use, and whether steps run in parallel.
   * - ``title``, ``description``, ``project``, ``projects``
     - The job's title, description and project.
   * - ``root``, ``datastore``, ``database``, ``database-timeout``, ``read-only``,
       ``dashboards``, ``job-id-file``, ``standalone``, ``force``
     - Where the job and its data are kept, and how it runs.
   * - ``log-level``, ``executor``, ``resume``, ``help``
     - Logging, how programs are run, resuming a stopped job, and help.

A dash and an underscore count as the same (``log_level`` is ``log-level``). The
editor refuses these names, and so do checking a flowchart (``seamm-flowchart
validate``) and submitting it. A flowchart made earlier with one of them stops at
the start with a message naming the parameter; rename it, e.g. ``memory_per_task``
for ``memory``, and use the new name where its value is used (``$memory_per_task``).
Names such as ``cores``, ``hours``, ``time`` and ``queue`` are fine.

..
   The following sections cover accessing and controlling this functionality.

   .. toctree::
      :maxdepth: 2
      :titlesonly:

Index
=====

* :ref:`genindex`
