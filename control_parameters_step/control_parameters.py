# -*- coding: utf-8 -*-

"""Non-graphical part of the Control Parameters step in a SEAMM flowchart
"""

import configargparse
import logging
import pprint  # noqa: F401

import control_parameters_step
import seamm
from seamm import data  # noqa: F401
from seamm_util import ureg, Q_  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: 'job' and 'printer'. 'job' send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# 'printer' sends output to the file 'step.out' in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter('Control Parameters')


class ControlParameters(seamm.Node):
    """
    The non-graphical part of a Control Parameters step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : ControlParametersParameters
        The control parameters for Control Parameters.

    See Also
    --------
    TkControlParameters,
    ControlParameters, ControlParametersParameters
    """

    def __init__(
        self,
        flowchart=None,
        title='Control Parameters',
        extension=None,
        logger=logger
    ):
        """A step for Control Parameters in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug('Creating Control Parameters {}'.format(self))

        # Argument/config parsing
        self.parser = configargparse.ArgParser(
            auto_env_var_prefix='',
            default_config_files=[
                '/etc/seamm/control_parameters_step.ini',
                '/etc/seamm/seamm.ini',
                '~/.seamm/control_parameters_step.ini',
                '~/.seamm/seamm.ini',
            ]
        )

        self.parser.add_argument(
            '--seamm-configfile',
            is_config_file=True,
            default=None,
            help='a configuration file to override others'
        )

        # Options for this plugin
        self.parser.add_argument(
            "--control-parameters-step-log-level",
            default=configargparse.SUPPRESS,
            choices=[
                'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
            ],
            type=string.upper,
            help="the logging level for the Control Parameters step"
        )

        self.options, self.unknown = self.parser.parse_known_args()

        # Set the logging level for this module if requested
        if 'control_parameters_step_log_level' in self.options:
            logger.setLevel(self.options.control_parameters_step_log_level)

        super().__init__(
            flowchart=flowchart,
            title='Control Parameters',
            extension=extension,
            module=__name__,
            logger=logger
        )  # yapf: disable

        self.parameters = control_parameters_step.ControlParametersParameters()

    @property
    def version(self):
        """The semantic version of this module.
        """
        return control_parameters_step.__version__

    @property
    def git_revision(self):
        """The git version of this module.
        """
        return control_parameters_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.
        Returns
        -------
        str
            A description of the current step.
        """
        if not P:
            P = self.parameters.values_to_dict()

        text = (
            'Please replace this with a short summary of the '
            'Control Parameters step, including key parameters.'
        )

        return self.header + '\n' + __(text, **P, indent=4 * ' ').__str__()

    def run(self):
        """Run a Control Parameters step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)
        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Print what we are doing
        printer.important(__(self.description_text(P), indent=self.indent))

        # Temporary code just to print the parameters. You will need to change
        # this!
        for key in P:
            print('{:>15s} = {}'.format(key, P[key]))
            printer.normal(
                __(
                    '{key:>15s} = {value}',
                    key=key,
                    value=P[key],
                    indent=4 * ' ',
                    wrap=False,
                    dedent=False
                )
            )

        # Analyze the results
        self.analyze()

        # Since we have succeeded, add the citation.

        self.references.cite(
            raw=self._bibliography['control_parameters_step'],
            alias='control_parameters_step',
            module='control_parameters_step',
            level=1,
            note='The principle citation for the control parameters step in SEAMM.'
        )
        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return next_node

    def analyze(self, indent='', **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        'printer'.

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        printer.normal(
            __(
                'This is a placeholder for the results from the '
                'Control Parameters step',
                indent=4 * ' ',
                wrap=True,
                dedent=False
            )
        )
