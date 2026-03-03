#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:    [2026-03-03 Tue]

"""pytest script of datawarrior_clustersort.py

Tests from the outside are marked as `blackbox`.  Tests based on
the import of a function of the main script are marked `imported`.
"""

import io
import os
import shlex

import pytest

from app.datawarrior_clustersort import (
    file_reader,
    get_args,
    identify_cluster_column,
    label_sorter,
    main,
    permanent_report,
    read_dw_list,
    update_cluster_labels,
)


@pytest.mark.imported
def test_file_reader() -> None:
    """Check recognizing headline, table body, DW's lowest cluster label."""
    probe_data = r"""Structure [idcode]	Cluster No	Is Representative	record_number
edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3
"""
    mock_file = io.StringIO(probe_data)
    headline, table_body, old_cluster_label = file_reader(mock_file)
    assert (
        headline == "Structure [idcode]\tCluster No\tIs Representative\trecord_number"
    )
    assert table_body == [
        r"edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1",
        r"elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2",
        r"elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3",
    ]
    # implicitly test function `identify_cluster_column`:
    assert old_cluster_label == 1


@pytest.mark.imported
def test_identify_cluster_column() -> None:
    """Check identification of the cluster column."""
    input_string = "Structure [idcode]	Cluster No	Is Representative	record_number"
    expected_column = 1
    test_column = identify_cluster_column(input_string)
    assert test_column == expected_column, "wrong column index"


@pytest.mark.imported
def test_read_dw_list() -> None:
    """Perform a frequency analysis on DW assigned cluster labels.

    This checks if DW assigned cluster labels are used to build a
    dictionary where DW labels indicate (as key) to the number of
    times they are assigned by DW (as value)."""
    # some records of DW cluster 1, 5, and 8 of `100Random_Molecules.txt`
    mock_table_body = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	5	No	7",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	5	No	17",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	8	Yes	18",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	5	No	19",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	8	No	67",
    ]
    old_cluster_label = 1
    expected_dictionary = {
        "1": 4,
        "5": 3,
        "8": 2,
    }
    test_dictionary = read_dw_list(mock_table_body, old_cluster_label)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_label_sorter_default_sort() -> None:
    """Check the normal sort of a new frequency dictionary.

    By default, the lowest key (label) describes the cluster with the
    most structures (value)."""
    mock_dictionary = {"1": 4, "5": 3, "8": 2}
    reversed_order = False
    expected_dictionary = {"1": 1, "5": 2, "8": 3}
    test_dictionary = label_sorter(mock_dictionary, reversed_order)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_label_sorter_reverse_sort() -> None:
    """Check the reverse sort of a new frequency dictionary.

    By default, the lowest key (label) describes the cluster with the
    least number of structures (value)."""
    mock_dictionary = {"1": 4, "5": 3, "8": 2}
    reversed_order = True
    expected_dictionary = {"1": 3, "5": 2, "8": 1}
    test_dictionary = label_sorter(mock_dictionary, reversed_order)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_update_cluster_labels() -> None:
    """Check the reassignment of cluster labels."""
    # some of DW clusters 1, 5, and 8
    mock_table_body = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	5	No	7",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	5	No	17",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	8	Yes	18",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	5	No	19",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	8	No	67",
    ]
    old_cluster_label = 1
    label_dictionary = {"1": 1, "5": 2, "8": 3}
    expected_reporter_list = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	2	No	7",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	2	No	17",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	2	No	19",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	3	Yes	18",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	3	No	67",
    ]
    test_reporter_list = update_cluster_labels(
        mock_table_body, old_cluster_label, label_dictionary
    )
    assert test_reporter_list == expected_reporter_list


@pytest.mark.imported
def test_permanent_report(tmp_path) -> None:
    """Probe the generation of a permanent record."""
    # prepare data to write
    input_file = "test_input.txt"
    headline = "Structure [idcode]	Cluster No	Is Representative	record_number"
    listing = [
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	3	Yes	18",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	3	No	67",
    ]

    # simulate a temporary input file
    input_file_path = tmp_path / input_file
    input_file_path.write_text("\n".join([headline] + listing))

    report_file = permanent_report(str(input_file_path), headline, listing)

    # probe output file
    output_file_path = tmp_path / report_file
    assert output_file_path.exists(), "creation output file failed"

    expected_content = "\n".join([headline] + listing) + "\n"
    assert (
        output_file_path.read_text() == expected_content
    ), "incorrect content in output file"


@pytest.fixture
def dummy_file():
    """Provide a dummy file to eventually check get_args."""
    dummy = "input_file.txt"
    content = r"""Structure [idcode]	Cluster No	Is Representative	record_number
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3
eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	2	No	4
fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	4	No	5
fbma`@@`PKHihdhdXdierWhirt@QPAE@`@@	3	No	11
fnsQ`@CE@cJSK\l{]kLeNCdkTA@PQTrD@@	3	No	12
fmwAR@KNBeXICHhddeDeDhXedTjLejNYj`HfjjjjAPZ^P@	4	No	14
eg`TN@@LD`DBjecklbbVbbTTrbrbTjvbcegfWSUTBQETuUSPhTHq@@	4	No	21
fak@r@HHe[qPAFRPjIJKJJI[QHRgAjuZ@Hjjjja\Zahe@@	4	No	25"""

    with open(dummy, mode="w", encoding="utf-8") as new:
        new.write(content)
    yield dummy
    os.remove(dummy)


@pytest.mark.imported
def test_shlex_selfcheck() -> None:
    """Probe proper running of shlex of Python's standard library."""
    command = "file.txt -r"
    as_list = ["file.txt", "-r"]


@pytest.mark.imported
@pytest.mark.parametrize(
    "command, reverse",
    [
        ("input_file.txt", False),
        ("input_file.txt -r", True),
        ("input_file.txt --reverse", True),
    ],
)
def test_get_args(command, reverse, dummy_file):
    """Check faithful transfer of optional parameter -r."""
    args = get_args(shlex.split(command))
    assert (args.reverse) == (reverse)


test_cases = [
    ("input_file.txt", False),
]


@pytest.mark.imported
@pytest.mark.parametrize("command, reverse", test_cases)
def test_main(command, reverse, dummy_file):
    """Probe the main function."""
    main(shlex.split("input_file.txt"))
    assert (reverse) == False
    os.remove("input_file_sort.txt")
