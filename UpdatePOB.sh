#!/bin/bash
POB_directory="$1"

if [ -d "$POB_diectory" ]; then
    #datetime=$(date +%F_%H-%M-%S)

    # Don't need to rename the current tree.lua because creating alternative tree instead of replacing current tree
    #mv $POB_directory/tree.lua $POB_directory/tree_$datetime.lua

    # move the newly generated tree.lua
    cp ./data/tree_edit.lua $POB_directory/tree.lua
else
    echo "Invalid POB_directory: $POB_directory"
fi
