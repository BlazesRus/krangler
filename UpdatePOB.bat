@echo off
set POB_directory=%1

if exist %POB_directory% (
    rem get the current date and time in YYYY-MM-DD_HH-MM-SS format
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set datetime=%%a
    set datetime=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

    rem rename the current tree.lua
    ren %POB_directory%\tree.lua tree_%datetime%.lua

    rem move the newly generated tree.lua
    copy .\data\tree_edit.lua %POB_directory%\tree.lua
) else (
    echo Invalid POB_directory: %POB_directory%
)
