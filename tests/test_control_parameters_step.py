#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `control_parameters_step` package."""

import pytest  # noqa: F401
import control_parameters_step  # noqa: F401


def test_construction():
    """Just create an object and test its type."""
    result = control_parameters_step.ControlParameters()
    assert str(type(result)) == (
        "<class 'control_parameters_step.control_parameters.ControlParameters'>"  # noqa: E501
    )


# ---- variables defined with only some items (seamm-flowchart, the MCP server) -----


def _partial():
    return {
        "structure": {"type": "file", "default": "nacl.extxyz", "help": "The cell"},
        "T": {"type": "float", "optional": "Yes", "default": "298.15"},
    }


def test_partial_definitions_are_completed():
    """A definition giving only some items is completed when the parameters are
    read: submitting a job read 'nargs' and stopped with only "nargs" (science,
    2026-10-20)."""
    from control_parameters_step import ControlParametersParameters

    P = ControlParametersParameters(
        data={"variables": {"value": _partial(), "units": None}}
    )
    variables = P["variables"].value
    for data in variables.values():
        assert data["nargs"] == "a single value"
        assert data["overwrite"] == "No"
        assert data["choices"] == []
        assert data["optional"] == "Yes"
    # What was given is kept
    assert variables["structure"]["type"] == "file"
    assert variables["T"]["default"] == "298.15"
    assert P.problems() == []


def test_invalid_items_are_problems():
    from control_parameters_step import ControlParametersParameters

    variables = _partial()
    variables["T"]["nargs"] = "two values"
    variables["structure"]["type"] = "path"
    P = ControlParametersParameters(
        data={"variables": {"value": variables, "units": None}}
    )
    problems = P.problems()
    assert any("'T' has 'nargs' 'two values'" in p for p in problems)
    assert any("'structure' has 'type' 'path'" in p for p in problems)


def test_a_flowchart_with_partial_definitions_reads_complete():
    """Through seamm's own reader, as submit_job and run_flowchart read it."""
    import seamm
    from seamm import format3

    text = (
        "format: MolSSI flowchart 3.0\nsteps:\n- step: Parameters\n  parameters:\n"
        "    variables:\n"
        "      smiles: {type: str, default: CCO, help: A SMILES string}\n"
    )
    flowchart = seamm.Flowchart()
    format3.from_text(flowchart, text)
    step = flowchart.get_nodes()[1]
    data = step.parameters["variables"].value["smiles"]
    assert data["nargs"] == "a single value"
    assert data["optional"] == "Yes" and data["overwrite"] == "No"


# ---- defaults of one or more values keep their backslashes ------------------------


def test_default_list_keeps_backslashes():
    """A default list of SMILES kept its Z double bonds only when quoted: shlex.split
    dropped the backslash of C/C=C\\C (Paul; thermo, ChemAI 5523, 2026-10-30)."""
    from control_parameters_step.control_parameters import default_value

    data = {"type": "str", "nargs": "one or more values"}
    data["default"] = r"C=C(C)C C/C=C/C C/C=C\C 'O/C=C\O' C#N"
    assert default_value(data) == [
        "C=C(C)C",
        "C/C=C/C",
        r"C/C=C\C",
        r"O/C=C\O",
        "C#N",
    ]
    data = {"type": "str", "nargs": "a single value", "default": r"C/C=C\C"}
    assert default_value(data) == r"C/C=C\C"
    data = {"type": "int", "nargs": "one or more values", "default": "1 2 3"}
    assert default_value(data) == [1, 2, 3]


# ---- names reserved for SEAMM's own job options (mlff, 2026-11-19) ----------------


def _variables(*names):
    return {
        name: {
            "type": "float",
            "optional": "Yes",
            "nargs": "a single value",
            "overwrite": "No",
            "default": "1",
            "choices": [],
            "help": "",
        }
        for name in names
    }


@pytest.mark.parametrize(
    "name", ["memory", "ncores", "title", "log_level", "log-level", "--root", "resume"]
)
def test_reserved_names_are_refused(name):
    from control_parameters_step.reserved import reserved_problem

    problem = reserved_problem(name)
    assert problem is not None
    assert f"'{name}'" in problem and "Rename it" in problem


@pytest.mark.parametrize("name", ["cores", "hours", "time", "queue", "Memory", "T"])
def test_ordinary_names_are_fine(name):
    from control_parameters_step.reserved import reserved_problem

    assert reserved_problem(name) is None


def test_reserved_names_cover_seamm_options():
    """Every job option seamm_util defines is in the static list, which the editor
    and the flowchart checks use."""
    import seamm_util
    from control_parameters_step.reserved import RESERVED_NAMES, normalize

    parser = seamm_util.seamm_parser(name="test-reserved-names")
    for args, kwargs in parser._parsers["SEAMM"]["arguments"]:
        for option in args:
            assert normalize(option) in RESERVED_NAMES, option
        if kwargs.get("dest"):
            assert normalize(kwargs["dest"]) in RESERVED_NAMES, kwargs["dest"]


def test_reserved_names_from_the_parser():
    """At run time the parser's own options count too, e.g. one a newer SEAMM adds."""
    import seamm_util
    from control_parameters_step.reserved import reserved_problem

    parser = seamm_util.seamm_parser(name="test-reserved-parser")
    parser.add_argument("SEAMM", "--brand-new-option", dest="brand_new")
    assert reserved_problem("brand-new-option") is None
    assert reserved_problem("brand_new_option", parser=parser) is not None
    assert reserved_problem("brand_new", parser=parser) is not None


def test_check_flowchart_reports_reserved_names():
    node = control_parameters_step.ControlParameters()
    node.parameters["variables"].value = _variables("memory", "cores", "title")
    problems = node.check_flowchart([])
    assert len(problems) == 2
    assert any("--memory" in p for p in problems)
    assert any("--title" in p for p in problems)

    node.parameters["variables"].value = _variables("cores", "hours")
    assert node.check_flowchart([]) == []


def test_create_parser_stops_clearly():
    """The run-time backstop: a clear message rather than argparse's conflict."""
    import seamm
    import seamm_util

    seamm_util.seamm_parser()
    flowchart = seamm.Flowchart()
    node = control_parameters_step.ControlParameters(flowchart=flowchart)
    node.parameters["variables"].value = _variables("memory")
    with pytest.raises(ValueError, match="'--memory'"):
        node.create_parser()


class _Entry:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class _Dialog:
    def __init__(self):
        self.closed = False

    def deactivate(self, result=None):
        self.closed = True

    def interior(self):
        return None


def _gui_with(name, existing=None):
    """A TkControlParameters with only what the variable dialogs' handlers use."""
    from control_parameters_step.tk_control_parameters import TkControlParameters

    gui = TkControlParameters.__new__(TkControlParameters)
    gui._variables = dict(existing or {})
    gui._new_variable_dialog = _Dialog()
    gui._edit_variable_dialog = _Dialog()
    fields = {
        "name": _Entry(name),
        "type": _Entry("float"),
        "nargs": _Entry("a single value"),
        "optional": _Entry("Yes"),
        "overwrite": _Entry("No"),
        "default": _Entry("1"),
        "choices": _Entry(""),
        "help": _Entry(""),
    }
    gui._new = dict(fields)
    gui._edit = dict(fields)
    gui.reset_table = lambda: None
    return gui


@pytest.fixture
def errors(monkeypatch):
    """The messages the dialogs would show."""
    from control_parameters_step import tk_control_parameters

    shown = []
    monkeypatch.setattr(
        tk_control_parameters.messagebox,
        "showerror",
        lambda title, message, **kwargs: shown.append((title, message)),
    )
    return shown


def test_gui_refuses_reserved_name(errors):
    gui = _gui_with("memory")
    gui.handle_new_variable_dialog("OK")
    assert "memory" not in gui._variables
    assert not gui._new_variable_dialog.closed  # left up to change the name
    assert errors and errors[0][0] == "Reserved name" and "--memory" in errors[0][1]


def test_gui_accepts_ordinary_name(errors):
    gui = _gui_with("cores")
    gui.handle_new_variable_dialog("OK")
    assert "cores" in gui._variables
    assert gui._new_variable_dialog.closed
    assert errors == []


def test_gui_refuses_renaming_to_reserved_name(errors):
    gui = _gui_with("title", existing=_variables("label"))
    gui.handle_edit_variable_dialog("label", "OK")
    assert "label" in gui._variables and "title" not in gui._variables
    assert not gui._edit_variable_dialog.closed
    assert "--title" in errors[0][1]


def test_gui_refuses_duplicate_name(errors):
    gui = _gui_with("cores", existing=_variables("cores"))
    gui.handle_new_variable_dialog("OK")
    assert not gui._new_variable_dialog.closed
    assert errors[0][0] == "Duplicate name"
