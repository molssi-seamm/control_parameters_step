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
