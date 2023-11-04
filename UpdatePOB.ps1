# get the first argument as the POB_directory
$POB_directory = $args[0]

# check if the POB_directory exists
if (Test-Path $POB_directory) {
    # get the current date and time in YYYY-MM-DD_HH-MM-SS format
    #$datetime = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

    # Don't need to rename the current tree.lua because creating alternative tree instead of replacing current tree
    #Rename-Item -Path "$POB_directory\tree.lua" -NewName "tree_$datetime.lua"

    # move the newly generated tree.lua
    Copy-Item -Path ".\data\tree_edit.lua" -Destination "$POB_directory\tree.lua"
}
else {
    # display an error message
    Write-Error "Invalid POB_directory: $POB_directory"
}
