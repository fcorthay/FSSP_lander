#! /bin/bash
# Ltarts the lander environment

WORK_DIRECTORY='/home/francois/Documents/FabLab/FSSP_lander/Python'
PIPES_DIRECTORY='/tmp/lander'

cat $WORK_DIRECTORY/cartesian.txt > $PIPES_DIRECTORY/controlToCalculator &
cat < $PIPES_DIRECTORY/calculatorToControl > /dev/null &
cat < $PIPES_DIRECTORY/calculatorToAxes

