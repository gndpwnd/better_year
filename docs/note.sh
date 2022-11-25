#!/bin/bash

# change to the directory do docs
# cd docs

dependencies=[
    "webpack"
    "webpack-cli"
    "webpack-dev-server"
    "mini-css-extract-plugin"
    "sass"
]

for dependency in "${dependencies[@]}"; do
    npm install -g $dependency
    npm install --save-dev $dependency
    npm link $dependency
done