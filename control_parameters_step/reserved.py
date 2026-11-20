# -*- coding: utf-8 -*-

"""Names a Parameters step cannot use.

The parameters of a Parameters step become command-line options of the job
(``--<name>``) in the same "SEAMM" section as SEAMM's own job options, such as
``--memory`` and ``--title``. argparse refuses a second option with the same name,
and two options with the same destination overwrite each other, so a parameter with
one of these names stops the job before its first step.
"""

# The job options of seamm_util.seamm_parser() and seamm_exec, plus argparse's
# --help, by their destination (dashes as underscores). The parser in use is also
# asked at run time (see `reserved_names`), so options added later are caught there
# even before they are added here.
RESERVED_NAMES = {
    "dashboards": "--dashboards",
    "database": "--database",
    "database_timeout": "--database-timeout",
    "datastore": "--datastore",
    "description": "--description",
    "executor": "--executor",
    "force": "--force",
    "help": "--help",
    "job_id_file": "--job-id-file",
    "log_level": "--log-level",
    "memory": "--memory",
    "ncores": "--ncores",
    "parallelism": "--parallelism",
    "project": "--project",
    "projects": "--project",
    "read_only": "--read-only",
    "resume": "--resume",
    "root": "--root",
    "standalone": "--standalone",
    "title": "--title",
}


def normalize(name):
    """The destination argparse gives the option for a parameter name."""
    return name.strip().lstrip("-").replace("-", "_")


def reserved_names(parser=None):
    """The reserved names, each with the job option it belongs to.

    Parameters
    ----------
    parser : seamm_util.ArgumentParser = None
        The parser the job's options are in. Its "SEAMM" section's options are
        added to the known ones, so options a newer SEAMM adds are caught too.

    Returns
    -------
    {str: str}
        The destination of each reserved option, and its option string.
    """
    result = dict(RESERVED_NAMES)
    if parser is None:
        return result
    # seamm_util's ArgumentParser keeps the arguments until it parses them
    section = getattr(parser, "_parsers", {}).get("SEAMM")
    if section is None:
        return result
    for args, kwargs in section.get("arguments", []):
        options = [a for a in args if isinstance(a, str) and a.startswith("-")]
        if not options:
            continue
        long = [a for a in options if a.startswith("--")]
        option = long[0] if long else options[0]
        result.setdefault(normalize(option), option)
        if kwargs.get("dest"):
            result.setdefault(normalize(kwargs["dest"]), option)
    return result


def reserved_problem(name, parser=None, reserved=None):
    """Why a parameter cannot have this name, or None if it can.

    Parameters
    ----------
    name : str
        The name of the parameter.
    parser : seamm_util.ArgumentParser = None
        The parser the job's options are in, if any (see `reserved_names`).
    reserved : {str: str} = None
        The reserved names, if already known.

    Returns
    -------
    str or None
    """
    if reserved is None:
        reserved = reserved_names(parser)
    dest = normalize(name)
    if dest not in reserved:
        return None
    return (
        f"The parameter '{name}' has the same name as SEAMM's own job option "
        f"'{reserved[dest]}', so the job could not start. Rename it, e.g. "
        f"'{dest}_per_task' or 'my_{dest}'."
    )


def reserved_problems(names, parser=None):
    """The problems with the names of the parameters: see `reserved_problem`."""
    reserved = reserved_names(parser)
    problems = []
    for name in names:
        problem = reserved_problem(name, reserved=reserved)
        if problem is not None:
            problems.append(problem)
    return problems


def sorted_reserved_options():
    """The reserved option strings, for documentation and help text."""
    return sorted(set(RESERVED_NAMES.values()))
