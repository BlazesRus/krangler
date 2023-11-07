from io import TextIOWrapper
from tkinter import INSIDE
import pandas as pd
import numpy as np
import glob
import subprocess
import os
import platform
import pathlib

NOTHINGNESS = [
    '            [\"icon\"] = \"Art/2DArt/SkillIcons/passives/MasteryBlank.png\",\n',
    '            [\"name\"] = \"Nothingness\",\n',
    '            [\"stats\"] = {},\n']

NOTHINGNESS_ASCENDANCY = [
    '            [\"icon\"] = \"Art/2DArt/SkillIcons/passives/MasteryBlank.png\",\n',
    '            [\"name\"] = \"Unknown Ascendancy\",\n',
    '            [\"ascendancyName\"] = \"None\",\n',
    '            [\"stats\"] = {},\n']

ASCENDANCY_ERROR = [
    '            [\"icon\"] = \"Art/2DArt/SkillIcons/passives/MasteryBlank.png\",\n',
    '            [\"name\"] = \"Ascendancy Replacement Error\",\n',
    '            [\"ascendancyName\"] = \"None\",\n',
    '            [\"stats\"] = {},\n']

class LuaSubNode:
    def __init__(self, name:str, topLevelKey:str='', hasSubNodes:bool=False, hasListInfo:bool=False, nodeContent:str='', subnodes:dict[str,str]={} ):
        #If name is starts with '{' and ends with number of index in parentnode, then is using {} grouping (such as for mastery node)  
        #   use name[1,-1] to extract information about index
        self.name = name
        #Keynames based on (parent's topLevelKey or subnode's name if parent is in subnodes)+_+name (can't use lists as key so using string instead)
        self.topLevelKey = topLevelKey
        self.hasSubNodes = hasSubNodes
        self.hasListInfo = hasListInfo
        self.nodeContent = nodeContent
        #Actual subnodes stored inside the parent LuaNode
        self.subnodes = subnodes
  
	def get_name(self):
		return self.name
		
	def get_subNodeKey(self, name):
		return self.topLevelKey+'_'+name

class LuaNode:
    def __init__(self, name:str, hasSubNodes:bool, nodeContent:str='', subnodes:dict[str, LuaSubNode]={}, recursiveSubNodes:dict[str, LuaSubNode]={}):
        self.name = name
        self.hasSubNodes = hasSubNodes
        self.nodeContent = nodeContent
        #Node ID data stored at this level
        self.subnodes = subnodes
		#["name"] and other fields stored here (access via self.subnodes[NodeId]
        self.recursiveSubNodes:dict[str, LuaSubNode] = recursiveSubNodes
    
    def get_name(self):
        return self.name
    
    def get_childNode(self, subNodeName, childNodeName):
        childKey:str = self.subnodes[subNodeName].get_subNodeKey(childNodeName)
		self.recursiveSubNodes[childKey]
	
    def add_SubNodeFromTopLevel(self, name:str, hasSubNodes:bool=False, hasListInfo:bool=False, nodeContent:str=''):
        self.subnodes[name] = LuaSubNode(name, '', hasSubNodes, hasListInfo, nodeContent)
    
    
    def add_SubNodeToSubnode(self, name:str, parentKey:str, SubNodes:bool=false, hasListInfo:bool=false, nodeContent:str=''):
    #if size is one, then parent key is stored inside subnodes
        #parentKey+_+name
        topLevelKey:str = parentKey+'_'+name
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(name, topLevelKey, SubNodes, hasListInfo, nodeContent)
    
class TreeStorage:
    def __init__(self, RootStart='', topLevelStorage:dict[str, LuaNode]={}):
        #Lines starting from top of file until first top level node group start stored here
        self.RootStart = RootStart
        #top level nodes such as "nodes" and "max_x" initialized here (topLevelStorage['"nodes"'] to access skill node data)
        self.topLevelStorage = topLevelStorage
    
    def get_name(self):
        return self.name

    def recursiveNodeOutput(self, f:TextIOWrapper, currentTopLevelNode:LuaNode, parentNode:LuaSubNode, recursiveLevel=1):
        # # Left Padding of the string(based on https://www.geeksforgeeks.org/fill-a-python-string-with-spaces/)
        # whitespacePaddedOutput = ('{: >recursiveLevel*4}'.format(string))
        # print(f'\"{whitespacePaddedOutput}\"')
        # alternatives can use '    '*recursiveLevel
        whitespacePaddedOutput:str
        if(parentNode.hasListInfo):
            if(parentNode.nodeContent==''):
                f.write('\"]= {}\n')
            else:
                f.write('\"]= {\n')
                f.write(parentNode.nodeContent)
                f.write('\n}')
        elif(parentNode.hasSubNodes):#{
            whitespacePaddedOutput = ('{: >recursiveLevel*4}'.format('['))
            f.write(f'\"{whitespacePaddedOutput}\"')
            f.write(parentNode.name)#[240]= { #skillTree ID is outputted at this level for first instance of this function if skillTree nodes
            f.write('\"]= {')
            actualSubNode:LuaSubNode;
            #separate variable to prevent needing to reduce level after exit for loop
            nodeLevel:int = recursiveLevel+1
            for i, node in enumerate(parentNode.subnodes):
            #{#Need to retrieve actual subNode info from topLevelNode
                if i:#Every element but the first element in list
                    f.write(',\n')
                if(node.name[0]=='{'):#{
                    #for use for subobject of ["masteryEffects"] node for {} grouping for effects
                    whitespacePaddedOutput = ('{: >nodeLevel*4}'.format('{'))
                    f.write(f'\"{whitespacePaddedOutput}\"')
                    self.recursiveNodeOutput(f, currentTopLevelNode, parentNode, nodeLevel+1)
                    whitespacePaddedOutput = ('{: >nodeLevel*4}'.format('}'))
                    f.write(f'\"{whitespacePaddedOutput}\"')
                #}
                else:
                    whitespacePaddedOutput = ('{: >nodeLevel*4}'.format('['))
                    f.write(f'\"{whitespacePaddedOutput}\"')
                    actualSubNode = currentTopLevelNode.recursiveSubNodes[node]
                    f.write(node.name)# ["name"]= at this level for first instance of this function if skillTree nodes
                    f.write('\"]= ')
                    self.recursiveNodeOutput(f, currentTopLevelNode, parentNode, nodeLevel+1)
            #}
            whitespacePaddedOutput = ('{: >recursiveLevel*4}'.format('['))
            f.write(f'\"{whitespacePaddedOutput}\"')
        else:
            whitespacePaddedOutput = ('{: >recursiveLevel*4}'.format('['))
            f.write(f'\"{whitespacePaddedOutput}\"')
            f.write(parentNode.name)
            f.write('\"]= ')
            f.write(parentNode.nodeContent)

    def reconstructAndSave_Tree(self, outputDirectory, fname='tree.lua'):
        fullPath = outputDirectory+fname
    #   print('Saving edited tree to '+fullPath+'. \n')

        nodeWhitespace = 4;
        with open(fullPath,'w') as f:
            f.write(self.RootStart)
            for topLevelNode in self.topLevelStorage:#{
                f.write('    [\"')
                f.write(topLevelNode.name)#outputs ["nodes"]= { at this level
                f.write('\"]= ')
				if skillTreeNode.hasListInfo:#["imageZoomLevels"] has information at this level
					print('Placeholder')
                elif topLevelNode.hasSubNodes==False:
                    f.write(topLevelNode.nodeContent)
                    f.write(',\n')
                else:#if(topLevelNode.hasSubNodes):
                    for i, skillTreeNode in enumerate(self[topLevelNode].subnodes):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')
                        f.write('        [')
                        f.write(skillTreeNode.name)#[240]= { #skillTree ID is outputted at this level
                        f.write('\"]= ')
                        if(skillTreeNode.hasListInfo):#{
                            if(skillTreeNode.nodeContent==''):
                                f.write('\"]= {},\n')
                            else:
                                f.write('\"]= {\n')
                                f.write(skillTreeNode.nodeContent)
                                f.write('\n        },n')
                        #}
						elif topLevelNode.hasSubNodes==False:
							print('Placeholder')
                        else:
                            self.recursiveNodeOutput(f, self[topLevelNode].subnodes, skillTreeNode)
                    #}
            #}
            f.write(skillTreeNode.RootEnd)
            f.close();

    def recursivelyLoadNodeInput(self, recursiveLevel=1):
        print('Loading Data lua data deeper into scope--placeholder command')
        
    def generateNodeTree(self, fileData):
        topLevel_luaNodeLineNumber = -1
        topLevel_luaNodeName = ''
        lineNumber = -1
        scanLevel = ''
        scanBuffer = ''

        topLevelStorage:dict[str, LuaNode] = {}
        #store nodes here for easy editing of nodes
        nodeSubgroup:dict[str, LuaNode] = {}
        otherSubgroup:dict[str, LuaNode] = {}
        #(indentation level for topLevel nodes are at 1 indentation,actual data for nodes starts at 2 indentation)
        indentationLevel = 2;

        for line in fileData:#{
            ++lineNumber;
            if(topLevel_luaNodeLineNumber==-1):#Add to root level before actual node info starts
            #{
                if(line.contains('[')):#{
                    topLevel_luaNodeLineNumber = lineNumber;
                #}
                else:#{
                    RootStart += line;
                #}
            #}
            #Start scanning actual info(indentation level for topLevel nodes are at 1 indentation,)
            if topLevel_luaNodeLineNumber!=-1:#{
                for lineChar in line:#{
                    if topLevel_luaNodeName=='':#{
                        if scanLevel=='' and lineChar=='[':
                            scanLevel = 'insideTopLevelNodeName'
                            scanBuffer = ''
                        elif lineChar==']':
                            topLevel_luaNodeName = scanBuffer
                            scanBuffer = ''
                            scanLevel = ''
                            if(line.contains(',')):
                                topLevelStorage[topLevel_luaNodeName] = topLevel_luaNodeName, False
                            else:
                                topLevelStorage[topLevel_luaNodeName] = topLevel_luaNodeName, True
                        elif scanLevel=='scanLevel':
                            scanBuffer += lineChar;
                    #}
                    else#{
                        if indentationLevel==2:#Scanning for NodeId now (node added to subnodes once scanned)
                            if scanLevel=='':
                                if lineChar=='{':
                                    scanLevel = '{'
                                elif(lineChar=='}'):#Exiting topLevelNode (ignoring the comma that might be after)
                                    topLevel_luaNodeName = ''
                                #elif lineChar is not ' ':#start extracting node content
                                #	scanLevel = 'nodeContent'
                                #	scanBuffer = lineChar
                            elif scanLevel=='{' and lineChar=='[':
                                scanLevel = '['
                            elif scanLevel=='[':
                                if lineChar==']':
                                    if topLevel_luaNodeName=='nodes'
                                        nodeSubgroup.add_SubNodeFromTopLevel(scanBuffer)#Add node to Tree
                                    else:
                                        nodeSubgroup.add_SubNodeFromTopLevel(scanBuffer)#Add node to Tree
                                    
                                    scanLevel = 'nextOrContent'#Search for either node content or subnodes(should only need to find subnodes for skilltree nodes). 
                                    scanBuffer = ''
                                else
                                    scanBuffer+=lineChar;
                            elif scanLevel=='nextOrContent':#Searching for subnodes like ["name"] or in rare cases search for node content value 
                                if lineChar=='{':
                                    indentationLevel = 3
                                    nodeSubgroup[-1].hasSubNodes = true
                                    scanLevel = ''
                                #elif lineChar is not ' ':#start extracting node content
                                #	scanLevel = 'nodeContent'
                                #	scanBuffer = lineChar
                            #elif scanLevel=='nodeContent':#points group is only topLevelGroup that will reach this(only single nodes with content value)
                            #	if lineChar==',' or lineChar=='\n':
                        elif indentationLevel==3)#Scanning for things like ["name"] now (node added to subnodes once scanned)
                            print('Placeholder');
                        else:#recursivelyLoadNodeInput will likely be needed for this part
                        
                    #}
                    else:#non-nodes level code here
                        if indentationLevel==2:#Scanning for NodeId now (node added to subnodes once scanned)
                            if scanLevel=='':
                                if lineChar=='{':
                                    scanLevel = '{'
                                elif(lineChar=='}'):#Exiting topLevelNode (ignoring the comma that might be after)
                                    topLevel_luaNodeName = ''
                            elif scanLevel=='{' and lineChar=='[':
                                scanLevel = '['
                            elif scanLevel=='[':
                                if lineChar==']':
                                    otherSubgroup.add_SubNodeFromTopLevel(scanBuffer)#Add node to Tree
                                    scanLevel = 'content'#Search for either node content or subnodes(should only need to find subnodes for skilltree nodes). 
                                    scanBuffer = ''
                                else
                                    scanBuffer+=lineChar;
                            else:#Searching for subnodes like ["name"] or in rare cases search for node content value 
                                print('Placeholder');
                        elif indentationLevel==3)#Scanning for things like ["name"] now (node added to subnodes once scanned)
                            print('Placeholder');
                        else:#recursivelyLoadNodeInput will likely be needed for this part
                        
                    #}
            #}
        #}
        
    def nullifyAllSkillTreeNodes(self, fileData):
        print('Remove all stats and art from tree--placeholder command')

def load_tree(outputDirectory, fname='tree.lua'):
    fullPath = outputDirectory+fname
 #   print('Loading tree from '+fullPath+'. \n')
    return open(outputDirectory+'/tree.lua','r').readlines()

def replace_all_nodes(inputDirectory, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
    originalFileData = load_tree(inputDirectory)
    #Parsing lines into nodes instead
    original_tree:TreeStorage
    original_tree.generateNodeTree(originalFileData)
    modified_tree:TreeStorage = original_tree
    if len(all_jsons) < 1:
    #{
        print('No JSON files found in data directory...Converting all nodes into nothing instead \n')
        modified_tree.nullifyAllSkillTreeNodes()
    #}
    else:
    #{
        #Files need to follow stringify 4 space format with 2 spaces on bracket or similar format or will fail to read json files (minify format will most likely fail)
        all_node_data = pd.concat([pd.read_json(json_file, typ='series', dtype='dict', encoding_errors='ignore') for json_file in all_jsons])
        #print('node_df stage starting \n')
        node_df = pd.DataFrame(all_node_data).reset_index().rename(columns = {'index':'original', 0:'new'})
        #print('dropping duplicates \n')
        node_df = node_df.drop_duplicates()
        #print('removing duplicated nothingness \n')
        nothingness_dupes = node_df[node_df['original'].duplicated(keep=False)]
        #print('indexing duplicated nothingness \n')
        node_df = node_df.drop(nothingness_dupes[nothingness_dupes['new']==-1].index)

        if any(node_df['original'].duplicated()):
            print('WARNING: mismatched duplicate nodes found:')
            for node_id in np.where(node_df['original'].duplicated())[0]:
                print('mismatch original node: '+str(node_df.iloc[node_id]['original'])) #+', new: '+str(node_df.iloc[node_id]['new']))

        for line in range(len(node_df)):
            #Sending information of node group passed to make sure don't replace any important nodes
            #replace_node(modified_tree, original_tree, int(node_df.iloc[line]['original']), int(node_df.iloc[line]['new']))
    #}
    save_tree(modified_tree, outputDirectory)

#Use breakpoints at error message prints in Visual Studio to find bugs in json file

def get_pob_dir():
    # open the text file for reading and read the first line of the file, which contains the directory path
    POB_DIR = ""
    pob_location = open("pob_location.txt", "r")
    POB_DIR = pob_location.readline().rstrip()
    pob_location.close()

    # check if the file is empty, and get directory from user input if it is empty
    if POB_DIR == "":
        POB_DIR = input("Please enter the directory where your Path of Building is located: ")
        file = open("pob_location.txt", "w")
        file.write(POB_DIR)
        file.close()

    return POB_DIR

def main():
    POBInstallLocation = get_pob_dir()
    #Edit dataFolderInputOverride.txt file to override OrigTree_DIR default pathing
    OrigTreeOverrideData = open("pob_location.txt", "r")
    OrigTreeOverride = pob_location.readline().rstrip()
    OrigTreeOverrideData.close()
    OrigTree_DIR:str
    POB_DIROverride:str
    if OrigTreeOverride == "":
        #detect if using Path of Building Source instead of using compiled code
        if os.path.isdir("POB_DIR/src/"):
            OrigTree_DIR = POBInstallLocation+'/src/TreeData/3_22/'
        else:
            OrigTree_DIR = POBInstallLocation+'/TreeData/3_22/'
    else:
        OrigTree_DIR = OrigTreeOverride
    #Edit dataFolderOutputOverride.txt file to override OrigTree_DIR default pathing
    OrigTreeOverrideData = open("pob_location.txt", "r")
    POB_DIROverride = pob_location.readline().rstrip()
    OrigTreeOverrideData.close()
    if POB_DIROverride == "":
        if os.path.isdir("POB_DIR/src/"):
            POBData_DIR = POBInstallLocation+'/src/TreeData/Krangled3_22/'
        else:
            POBData_DIR = POBInstallLocation+'/TreeData/Krangled3_22/'
    else:
        POBData_DIR = POB_DIROverride

    replace_all_nodes(OrigTree_DIR, POBData_DIR)
    #Editing copied file instead of replacing file in directory

if __name__ == "__main__":
    main()
