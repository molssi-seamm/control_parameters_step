# -*- coding: utf-8 -*-
"""Control parameters for the Control Parameters step in a SEAMM flowchart"""

import logging
import seamm
import pprint  # noqa: F401

logger = logging.getLogger(__name__)

#: The items of a variable's definition, with the values the dialog starts with. A
#: definition made elsewhere -- by seamm-flowchart or the MCP server, or by hand --
#: may give only some; the rest are filled in when the parameters are read, since
#: the step, the job dialog and job submission all read every item.
VARIABLE_DEFAULTS = {
    "type": "str",
    "nargs": "a single value",
    "optional": "Yes",
    "default": "",
    "choices": [],
    "overwrite": "No",
    "help": "",
}

#: The allowed values of the items with a fixed set of them
VARIABLE_CHOICES = {
    "type": ("file", "str", "int", "float", "choice", "bool", "list"),
    "nargs": (
        "a single value",
        "an optional value",
        "zero or more values",
        "one or more values",
    ),
    "optional": ("Yes", "No"),
    "overwrite": ("Yes", "No"),
}


def complete_variables(variables):
    """Fill in the items a variable's definition does not give.

    Parameters
    ----------
    variables : dict
        The definitions, by variable name, changed in place.

    Returns
    -------
    dict
        The same definitions.
    """
    if not isinstance(variables, dict):
        return variables
    for data in variables.values():
        if not isinstance(data, dict):
            continue
        for item, value in VARIABLE_DEFAULTS.items():
            if item not in data:
                data[item] = list(value) if isinstance(value, list) else value
    return variables


class ControlParametersParameters(seamm.Parameters):
    """
    The control parameters for Control Parameters.

    The developer will add a dictionary of Parameters to this class.
    The keys are parameters for the current plugin, which themselves
    might be dictionaries.

    You need to replace the 'time' example below with one or more
    definitions of the control parameters for your plugin and application.

    Parameters
    ----------
    parameters : {'kind', 'default', 'default_units', 'enumeration',
    'format_string', description', help_text'}
        A dictionary containing the parameters for the current step.
        Each key of the dictionary is a dictionary that contains the
        the following keys: kind, default, default_units, enumeration,
        format_string, description and help text.

    parameters['kind'] : custom
        Specifies the kind of a variable. While the 'kind' of a variable might
        be a numeric value, it may still have enumerated custom values
        meaningful to the user. For instance, if the parameter is
        a convergence criterion for an optimizer, custom values like 'normal',
        'precise', etc, might be adequate. In addition, any
        parameter can be set to a variable of expression, indicated by having
        '$' as the first character in the field. For example, $OPTIMIZER_CONV.

    parameters['default'] : 'integer' or 'float' or 'string' or 'boolean' or
        'enum' The default value of the parameter, used to reset it.

    parameters['default_units'] : str
        The default units, used for resetting the value.

    parameters['enumeration'] : tuple
        A tuple of enumerated values.

    parameters['format_string'] : str
        A format string for 'pretty' output.

    parameters['description'] : str
        A short string used as a prompt in the GUI.

    parameters['help_text'] : tuple
        A longer string to display as help for the user.

    See Also
    --------
    ControlParameters, TkControlParameters, ControlParameters
    ControlParametersParameters, Control ParametersStep
    """

    parameters = {
        "variables": {
            "default": {},
            "kind": "dictionary",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "variables",
            "help_text": "The variables to handle, with defaults, etc.",
        },
    }

    def __init__(self, defaults={}, data=None):
        """
        Initialize the parameters, by default with the parameters defined above

        Parameters
        ----------
        defaults: dict
            A dictionary of parameters to initialize. The parameters
            above are used first and any given will override/add to them.
        data: dict
            A dictionary of keys and a subdictionary with value and units
            for updating the current, default values.

        Returns
        -------
        None
        """

        logger.debug("ControlParametersParameters.__init__")

        super().__init__(
            defaults={**ControlParametersParameters.parameters, **defaults}, data=data
        )

    def update(self, data):
        """Update the values, completing each variable's definition."""
        super().update(data)
        if "variables" in self:
            complete_variables(self["variables"].value)

    def problems(self, values=None):
        """The checks of the base class, and that each variable's definition is
        complete and uses the allowed values."""
        result = super().problems(values)
        if values is None:
            values = self.current_values()
        variables = values.get("variables")
        if not isinstance(variables, dict):
            return result
        for name, data in variables.items():
            if not isinstance(data, dict):
                result.append(f"The variable '{name}' has no definition.")
                continue
            for item, allowed in VARIABLE_CHOICES.items():
                value = data.get(item, VARIABLE_DEFAULTS[item])
                if value not in allowed:
                    result.append(
                        f"The variable '{name}' has '{item}' {value!r}; it must be "
                        "one of " + ", ".join(repr(a) for a in allowed) + "."
                    )
        return result
