#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2022, 2023
# date:    [2022-04-22 Fri]
# edit:    [2025-02-28 Fri]
"""Provide a sort on DataWarrior clusters by popularity of the cluster.

DataWarrior can recognize structure similarity in a set of molecules.  The
more similar molecules are then grouped in clusters labeled by integers, a
result DataWarrior can store as .dwar, or export as .sdf file.  However so
far, the program however does not provide to report the molecules in a sort
based on the popularity of their corresponding clusters.
For context and motivation, see DataWarrior's discussion board after mcmc's
post 'Assign cluster name based on cluster size' by April 7, 2022
(https://openmolecules.org/forum/index.php?t=msg&th=586&goto=1587&#msg_1587).

The script uses only functions of Python's standard library as checked with
Python in version 3.11.2."""

import argparse
import csv
import logging
import os
import re
import sys


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("error.log"), logging.StreamHandler(sys.stderr)],
)


def get_args():
    """Get the arguments from the command line."""
    parser = argparse.ArgumentParser(
        description="""Sort DataWarrior's cluster list based on the number of
        molecules per cluster.  The triage by frequency reports the cluster
        most populous first.  After processing input file `example.txt`, the
        newly written record `example_sort.txt` can be accessed directly by
        DataWarrior by the short cut `Ctrl + O`.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        metavar="file",
        type=argparse.FileType("rt"),
        help="DataWarrior's cluster list which was exported as .txt file",
    )

    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="""override the default sort sequence; i.e. assign the least
        populous cluster the lowest label""",
    )

    return parser.parse_args()


def file_reader(input_file):
    """access the data as provided by DataWarrior's .txt file

    Assuming DW's file is less than half of the (remaining) available
    RAM of the computer used, the whole content of input file is read."""
    try:
        raw_table = input_file.read().splitlines()
        raw_table = [i.strip() for i in raw_table if len(i) > 1]
        if len(raw_table) < 3:
            logging.error(
                "Only %s non-empty line(s) instead of 3 in the input file.",
                len(raw_table),
            )
            sys.exit(1)
        return raw_table
    except OSError as e:
        logging.error("Error while reading %s: %s", input_file.name, e)
        sys.exit(1)


def identify_cluster_column(table_header):
    """Identify the column with DW's assigned cluster labels.

    The first occurrence of 'Cluster No' identified by a regular expression is
    assumed to indicate the column of interest.  For this, the split has to be
    an explicit separator (tabulator)."""
    column_heads = table_header.split("\t")
    list_of_matches = [
        i for i, item in enumerate(column_heads) if re.search("Cluster No", item)
    ]
    column_number = int(list_of_matches[0])

    return column_number


def read_dw_list(raw_data, cluster_label):
    """Establish a frequency list based on DW's exported cluster list."""
    dw_cluster_labels = []

    source = csv.reader(raw_data, delimiter="\t")
    for row in source:
        cluster_label_on_molecule = row[cluster_label]
        dw_cluster_labels.append(cluster_label_on_molecule)

    # build and report a dictionary:
    count = {}
    for label in dw_cluster_labels:
        count.setdefault(label, 0)
        count[label] = count[label] + 1

    #    print("\nDataWarrior's assignment of clusters:")
    for key, value in count.items():
        print(f"cluster: {key:>8} molecules: {value:>8}")

    return count


def cluster_sorter(count=None, reversed_order=None):
    """sort the popularity of the clusters either way."""
    if reversed_order:
        sorted_list = sorted(count, key=count.__getitem__, reverse=False)
    else:
        sorted_list = sorted(count, key=count.__getitem__, reverse=True)
    return sorted_list


def update_cluster_labels(table_body, population_list, old_cluster_label):
    """Update the molecules' labels according to the cluster popularity."""
    reporter_list = []
    new_cluster_label = 1

    for entry in population_list:
        source = csv.reader(table_body, delimiter="\t")

        for row in source:
            if row[old_cluster_label] == entry:
                cell_entries = row
                del cell_entries[old_cluster_label]
                cell_entries.insert(old_cluster_label, str(new_cluster_label))
                retain = "\t".join(cell_entries)
                reporter_list.append(retain)

        new_cluster_label += 1

    return reporter_list


def permanent_report(input_file, topline, listing=None):
    """Provide a permanent record DW may access."""
    stem_input_file = os.path.splitext(input_file)[0]
    report_file = "".join([stem_input_file, str("_sort.txt")])

    try:
        with open(report_file, encoding="utf-8", mode="w") as newfile:
            newfile.write("".join([topline, "\n"]))
            for entry in listing:
                newfile.write("".join([entry, "\n"]))
    except OSError as e:
        logging.error("Error to export record into %s (%s).  Exit.", report_file, e)
        sys.exit()

    return report_file


def main():
    """Join the functions."""
    args = get_args()

    # read the old data:
    raw_table = file_reader(args.file)
    head_line = raw_table[0]
    table_body = raw_table[1:]

    cluster_label = identify_cluster_column(head_line)
    print("\nDataWarrior's assignment of clusters:")
    popularity = read_dw_list(table_body, cluster_label)

    # reorganize the data:
    sorted_population_list = cluster_sorter(popularity, args.reverse)
    report_list = update_cluster_labels(
        table_body, sorted_population_list, cluster_label
    )
    permanent_report(args.file.name, head_line, report_list)

    # read the new data:
    print("\nclusters newly sorted and labeled:")
    read_dw_list(report_list, cluster_label)


if __name__ == "__main__":
    main()
