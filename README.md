# krangler

Python tool to convert `.json` node pairs into a `tree.lua` file for Path of Building in the Path of Exile Krangled Passives event.

## How to Use

- Need to make sure json files are properly formatted in order for code not to error out with Value Error (minified json will not work; 4 space stringify with 2 space indentation in brackets tested to work)
- Install any modern Python (e.g. [Anaconda](https://www.anaconda.com/download) - we only use Pandas and Numpy libraries which should be installed automatically)
- download this repository with `git` or just click `Code > Download ZIP` on github
- place your node pair `.json` file(s) into `./data` (to generate these, use [krangle-viewer](https://github.com/efunn/krangle-viewer) tool)
- download a [portable installation of Path of Building](https://github.com/PathOfBuildingCommunity/PathOfBuilding/releases/download/v2.34.1/PathOfBuildingCommunity-Portable.zip)
 if don't already have installed

- Copy 3_22 folder and rename as Krangled3_22

-Add:
	["Krangled3_22"] = {
		display = "Krangled3_22",
		num = 3.22,
		url = "https://www.pathofexile.com/passive-skill-tree/3.22.0/",
	},
	to GameVersions.lua
-Add "Krangled3_22", inside treeVersionList list in front of 3_22 entry

- open your terminal of choice (e.g. Powershell) and navigate to the `krangler` folder (e.g. `cd C:/Users/yourname/Downloads/krangler`)
- run `python krangler.py`
  - If this is the first time running the krangler, you will be prompted to enter the directory where you extracted the portable path of building (`[...]/PathOfBuilding-Community/`).
  - TreeData/3_22 (or TreeData/Krangled3_22) is Auto appended to end of directory entered (with /src prefix added for source version of path of building)
- the old tree data will be copied to a new file with the current datetime in the file name in `[...]/PathOfBuilding-Community/TreeData/3_22` and `tree.lua` will be replaced with your newly generated tree.
- run Path of Building from the `[...]/PathOfBuilding-Community/` folder and your new krangled tree should appear!

## Features

- includes list of all nodes in `./data/all_nodes_nothingness.json` to null out the ones that haven't been scouted yet
- includes automatic nulling out the ones that haven't been scouted yet if data folder is empty as well
- supports any number of `.json` files from multiple users
- duplicate nodes (same entry from multiple users) will work as long as replaced node is of same type
- will warn you when running `replace_all_nodes_wrapper()` if there are duplicate nodes that conflict with each other (i.e. one node mapped to different new nodes by different users)

- Auto detection of Source version of Path of Building and auto-appending path (should work with source code of path of building)
- No longer requires shellscript to run

## Limitations
- future versions require a rewrite of `krangler.py` to properly parse nodes instead of doing hacky string editing
