#!/bin/bash
POB_diectory="$1"

if [ -d "$POB_diectory" ]; then
    datetime=$(date +%F_%H-%M-%S)

    # rename the current tree.lua
    mv $POB_diectory/tree.lua $POB_diectory/tree_$datetime.lua

    # move the newly generated tree.lua
    cp ./data/tree_edit.lua $POB_diectory/tree.lua
else
    echo "Invalid POB_diectoryyyyy: $POB_diectory"
fi
