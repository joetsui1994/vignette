#!/bin/env/python3

import os
import json
import argparse
from ete3 import Tree

## parse command-line options
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--infile', type=str, required=True, help='Input JSON file from Nextstrain DTA')
parser.add_argument('-a', '--attributes', type=str, required=True, nargs='+', dest='attribute_list', help='A space-delimited list of attributes to be extracted from input JSON file')
parser.add_argument('-o', '--outfile', type=str, required=False, default='output.annotated.formatted.nexus', help='Output file name for the annotated nexus tree')
args = parser.parse_args()

# read in json file
with open(args.infile, 'r') as infile:
    json_dat = json.load(infile)

# extract tree
data_tree = json_dat['tree']

# construct tree
tree = Tree(name=data_tree['name'])
tree.dist = 0
tree.add_features(Country=data_tree['node_attrs']['Country']['value'],
                  num_date=data_tree['node_attrs']['num_date']['value'])

# recursive function to add children
def add_children(node_obj, node):
    for child_obj in node_obj['children']:
        child_node = node.add_child(name=child_obj['name'])
        child_node.dist = child_obj['node_attrs']['div']
        for attribute in args.attribute_list:
            child_node.add_features(**{attribute: child_obj['node_attrs'][attribute]['value']})
        if 'children' in child_obj and len(child_obj['children']) > 0:
            add_children(child_obj, child_node)

# build
add_children(data_tree, tree)

# get output file name with extension
output_filename = args.outfile

# export tree as annotated nexus (with annotations)
pre_output_filename = '%s.annotated.nexus' % os.path.splitext(output_filename)[0]
tree.write(outfile=pre_output_filename, format=1, features=args.attribute_list, format_root_node=True)

# fix formatting issues
# read in exported tree
with open(pre_output_filename, 'r') as infile:
    tree_str = infile.read().strip()

# replace &&NHX with &
tree_str = tree_str.replace('&&NHX:', '&')
# replace :num_date with ,num_date
tree_str = tree_str.replace(':num_date', ',num_date')
# add #NEXUS\nbegin trees;\ntree one = at the beginning of the file
tree_str = '#NEXUS\nbegin trees;\ntree one = ' + tree_str
# add end; at the end of the file
tree_str += ' end;'

# export fixed tree
# remove file extension and add .formatted
post_output_filename = os.path.splitext(pre_output_filename)[0] + '.formatted.nexus'
with open(post_output_filename, 'w') as outfile:
    outfile.write(tree_str)