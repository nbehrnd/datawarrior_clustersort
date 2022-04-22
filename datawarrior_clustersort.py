#!/usr/bin/env python3

# name:    datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2022.
# date:    <2022-04-22 Fri>
# edit:
"""Provide a sort on DataWarrior clusters by popularity of the cluster.

For context and motivation, see DataWarrior's discussion board after mcmc's
post 'Assign cluster name based on cluster size' by April 7, 2022
(https://openmolecules.org/forum/index.php?t=msg&th=586&goto=1587&#msg_1587).

The script uses only functions of Python's standard library."""

import argparse
import csv
import os
import sys


def get_args():
    """Get the arguments from the command line."""
    parser = argparse.ArgumentParser(
	description=
	"""Sort DataWarrior's cluster list, begin with the most populated.
	For an input file 'example.txt', a new record 'example_sort.txt'
	is written DataWarrior may access directly (Ctrl + O).""")

    parser.add_argument("source_file",
			metavar="FILE",
			help="DataWarrior's cluster export as .txt file.")

    parser.add_argument(
	"-r",
	"--reverse",
	action="store_false",
	help="""Override the default; sort in the permanent record starts
	with the cluster least populated and ends with the cluster containing
	the most molecules.""")

    return parser.parse_args()


def access_raw_data(input_file=""):
    """Access DW's exported cluster list."""
    raw_data = []

    try:
	with open(input_file, encoding="utf-8", mode="r") as source:
	    raw_data = source.readlines()
    except OSError:
	print(f"Input file {input_file} was not accessible.  Exit.")
	sys.exit()

    return raw_data


def read_header(raw_data=[]):
    """Extract the headline of DW's table."""
    table_header = ""
    table_header = str(raw_data[0]).strip()

    return table_header


def read_dw_list(raw_data=[]):
    """Establish a frequency list based on DW's exported cluster list."""
    dw_cluster_labels = []

    source = csv.reader(raw_data, delimiter="\t")
    for row in source:
	cluster_label_on_molecule = row[1]
	dw_cluster_labels.append(cluster_label_on_molecule)
    del dw_cluster_labels[0]  # do not consider the table header

    # build and report a dictionary:
    count = {}
    for label in dw_cluster_labels:
	count.setdefault(label, 0)
	count[label] = count[label] + 1

    for key, value in count.items():
	print("cluster: ", key, "\t molecules: ", value)

    return count


def entry_sorter(count={}, reversed_order=False):
    """Sort the popularity of the clusters either way."""
    if reversed_order:
	sorted_list = sorted(count, key=count.__getitem__, reverse=True)
    else:
	sorted_list = sorted(count, key=count.__getitem__, reverse=False)
    return sorted_list


def scrutin_by_label(raw_data=[], population_list=[]):
    """Sort the molecules according to the cluster popularity."""
    reporter_list = []
    new_cluster_label = 1

    for entry in population_list:
	source = csv.reader(raw_data, delimiter="\t")

	for row in source:
	    if row[1] == entry:
		retain = "\t".join([row[0], str(new_cluster_label), row[2]])
		reporter_list.append(retain)

	new_cluster_label += 1

    return reporter_list


def permanent_report(input_file="", topline="", listing=[]):
    """Provide a permanent record DW may access."""
    stem_input_file = os.path.splitext(input_file)[0]
    report_file = "".join([stem_input_file, str("_sort.txt")])

    try:
	with open(report_file, encoding="utf-8", mode="w") as newfile:
	    newfile.write("".join([topline, "\n"]))
	    for entry in listing:
		newfile.write("".join([entry, "\n"]))
    except OSError:
	print(f"Error to export record into {report_file}.  Exit.")
	sys.exit()
    return report_file


def main():
    """Join the functions."""
    args = get_args()
    input_file = args.source_file
    sort_option = args.reverse  # .true. == start by the least popular cluster

    # work on old data:
    print("Preview, sort by DataWarrior's cluster labels:")
    raw_data = access_raw_data(input_file)
    headline = read_header(raw_data)
    popularity = read_dw_list(raw_data)

    sorted_population_list = entry_sorter(popularity, sort_option)
    report_list = scrutin_by_label(raw_data, sorted_population_list)
    report_file = permanent_report(input_file, headline, report_list)

    # work on new data:
    print("\nclusters newly sorted and labeled:")
    raw_data = access_raw_data(report_file)
    headline = read_header(raw_data)
    popularity = read_dw_list(raw_data)


if __name__ == "__main__":
    main()
