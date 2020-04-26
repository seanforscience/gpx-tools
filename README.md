# GPX Tools

This is my toolkit for using the GPX file format. It's under development as needed. Presently VERY lightweight.

## Requirements

These objects only really use basic Pandas (pd) functionality  and Regular Expressions (re).

## Current Offerings

1. Import a GPX file as a GPXFile python object and access relevant track point data as a pandas dataframe.
2. Combine multiple GPX files into a single one.
3. Use Seaborn to plot the multi GPX file tracks as a scatterplot of latitude / longitude.

## TODO

1. Try to be more specific about treatment of times
2. explore possibilities around multiple trip segments
