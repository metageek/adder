#!/bin/bash

PATH=$PATH:/home/francis/local/bin

parent=`dirname $PWD`
grandparent=`dirname $parent`

$grandparent/adder.py --cache w.+
