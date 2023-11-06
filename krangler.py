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

def load_tree(outputDirectory, fname='tree.lua'):
    fullPath = outputDirectory+fname
 #   print('Loading tree from '+fullPath+'. \n')
    return open(outputDirectory+'/tree.lua','r').readlines()

class LuaSubNode:
  def __init__(self, name:str, topLevelKey:list<str>, SubNodes:bool=false, hasListInfo:bool=false, nodeContent:str='', subnodes:dict[str,str]={} ):
    self.name = name
    #Keynames based on (parent's topLevelKey or subnode's name if parent is in subnodes)+_+name
    self.topLevelKey = topLevelKey
    self.hasSubNodes = hasSubNodes
    self.hasListInfo = hasListInfo
    self.nodeContent = nodeContent
    #Actual subnodes stored inside the parent LuaNode
    self.subnodes = subnodes
  
  def get_name(self):
    return self.name

class LuaNode:
    def __init__(self, name:str, hasSubNodes:bool, originalLineNumber=-1, nodeContent:str='', subnodes:dict[str, LuaSubNode]={}, 
        recursiveSubNodes:dict[list<str>, LuaSubNode]={}):
        self.name = name
        self.hasSubNodes = hasSubNodes
        #orginalLineNumber for sending info when debugging
        self.originalLineNumber = originalLineNumber
        self.nodeContent = nodeContent
        self.subnodes = subnodes
        self.recursiveSubNodes = recursiveSubNodes
    
    def get_name(self):
        return self.name
    
    def add_SubNodeFromTopLevel(self, name:str, SubNodes:bool=false, hasListInfo:bool=false, nodeContent:str=''):
        subnodes[name] = LuaSubNode(name, {}, SubNodes, hasListInfo, nodeContent)
    
    
    def add_SubNodeToSubnode(self, name:str, parentKey:list<str>, SubNodes:bool=false, hasListInfo:bool=false, nodeContent:str=''):
    #if size is one, then parent key is stored inside subnodes
        #parentKey+,+name
        topLevelKey:list<str> = parentKey
        topLevelKey.append(name)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(name, topLevelKey, SubNodes, hasListInfo, nodeContent)
    
class TreeStorage:
    def __init__(self, RootStart, RootEnd, topLevelStorage:dict[str, LuaNode], nodeSubgroup:dict[str, LuaNode], otherSubnodeStorage:dict[str, LuaNode]):
        self.RootStart = RootStart
        self.RootEnd = RootEnd
        self.topLevelStorage = topLevelStorage
        self.nodeSubgroup = nodeSubgroup
        self.otherSubnodeStorage = otherSubnodeStorage
    
    def get_name(self):
        return self.name

    def recursiveNodeOutput(self, f:TextIOWrapper, currentTopLevelNode:LuaNode, parentNode:LuaSubNode, recursiveLevel=1):
        if(parentNode.hasListInfo):
            if(parentNode.nodeContent==''):
                f.write('\"]= {}\n')
            else:
                f.write('\"]= {\n')
                f.write(parentNode.nodeContent)
                f.write('\n}n')
        elif(parentNode.hasSubNodes):#{
            f.write('[')
            f.write(parentNode.name)#[240]= { #skillTree ID is outputted at this level for first instance of this function if skillTree nodes
            f.write('\"]= ')
            actualSubNode:LuaSubNode;
            #separate variable to prevent needing to reduce level after exit for loop
            nodeLevel:int = recursiveLevel+1
            for i, node in enumerate(parentNode.subnodes):
            #{#Need to retrieve actual subNode info from topLevelNode
                if i:#Every element but the first element in list
                    f.write(',\n')
                f.write('[')
                actualSubNode = currentTopLevelNode.recursiveSubNodes[node]
                f.write(actualSubNode.name)# ["name"]= at this level for first instance of this function if skillTree nodes
                f.write('\"]= ')
                self.recursiveNodeOutput(f, currentTopLevelNode, parentNode, ++nodeLevel)
            #}
        else:#Has context (not used )
            f.write('[')
            f.write(node.name)
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
                if(topLevelNode.hasSubNodes==False):
                    f.write(topLevelNode.nodeContent)
                    f.write(',\n')
                elif(topLevelNode.name=='nodes'):
                    nodeWhitespace = 8
                    for i, skillTreeNode in enumerate(self.nodeSubgroup):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')

                        f.write('        [')
                        f.write(skillTreeNode.name)#[240]= { #skillTree ID is outputted at this level
                        f.write('\"]= ')
                        # for i, node in enumerate(skillTreeNode.subnodes):
                        # #{
                        #     if i:#Every element but the first element in list
                        #         f.write(',\n')
                        #     f.write('        [')
                        #     f.write(node.name)# ["name"]= at this level
                        #     f.write('\"]= ')
                            
                        # #}
                        f.write('        },n')
                    #}
                else:
                    nodeWhitespace = 8
                    for i, skillTreeNode in enumerate(self.otherSubnodeStorage):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')
                        f.write('        [')
                        f.write(skillTreeNode.name)
                        if(skillTreeNode.hasListInfo):#{
                            if(skillTreeNode.nodeContent==''):
                                f.write('\"]= {},\n')
                            else:
                                f.write('\"]= {\n')
                                f.write(skillTreeNode.nodeContent)
                                f.write('\n        },n')
                        #}
                        elif(skillTreeNode.hasSubNodes):#{
                            f.write('\"]= {\n')
                            for i, node in enumerate(self.otherSubnodeStorage):
                            #{
                                if i:#Every element but the first element in list
                                    f.write(',\n')
                                #for i, skillTreeNode in enumerate(self.otherSubnodeStorage):
                            
                            #}
                            f.write('        },n')
                        #}
                        else:#{
                            f.write('\"]= ')
                            f.write(skillTreeNode.nodeContent)
                            f.write(',\n')
                        #}
                    #}
            #}
            f.write(skillTreeNode.RootEnd)
            f.close();

#Depreciated once finish parser code
def save_tree(tree, outputDirectory, fname='tree.lua'):
    fullPath = outputDirectory+fname
 #   print('Saving edited tree to '+fullPath+'. \n')
    with open(fullPath,'w') as f:
        for line in tree:
            f.write(line)

def replace_all_nodes_wrapper(inputDirectory, outputDirectory):
    original_tree = load_tree(inputDirectory)
    modified_tree = original_tree
    replace_all_nodes(modified_tree, original_tree, outputDirectory)

def replace_all_nodes(modified_tree, original_tree, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
    #Parsing lines into nodes instead
    topLevel_luaNodeLineNumber = -1
    topLevel_luaNodeName = ''
    lineNumber = -1
    scanLevel = ''
    scanBuffer = ''
    #Lines starting from top of file until first top level node group start stored here
    RootStart = ''
    #Lines after last node group set here (should  result in value of '}')
    RootEnd = ''
    #top level nodes such as "nodes" and "max_x" initialized here
    topLevelStorage:dict[str, LuaNode] = {}
    #store nodes here for easy editing of nodes
    nodeSubgroup:dict[str, LuaNode] = {}
    otherSubnodeStorage:dict[str, LuaNode] = {}


    for line in original_tree:#{
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
        #Start scanning actual info
        if(topLevel_luaNodeLineNumber!=-1):#{
            if(topLevel_luaNodeName==''):#{
                for lineChar in line:#{
                    if(scanLevel=='' and lineChar=='['):
                        scanLevel = 'insideTopLevelNodeName'
                        scanBuffer = '';
                    elif lineChar==']':
                        topLevel_luaNodeName = scanBuffer;
                        scanBuffer = '';
                        if(line.contains(',')):
                            topLevelStorage[topLevel_luaNodeName] = topLevel_luaNodeName, False;
                        else:
                            topLevelStorage[topLevel_luaNodeName] = topLevel_luaNodeName, True;
                    else:
                        scanBuffer += lineChar;
                #}
            #}
            elif(topLevel_luaNodeName=='nodes')#{
                if(topLevelStorage[topLevel_luaNodeName].hasSubNodes):#{
            
                #}
                else:#{
                    for lineChar in line:
                    #{
                    #}
                #}
            #}
            elif(topLevelStorage[topLevel_luaNodeName].hasSubNodes):#{
            
            #}
            else:#{
                for lineChar in line:
                #{
                #}
            #}
        #}
    #}
    if len(all_jsons) < 1:
    #{
        print('No JSON files found in data directory...Converting all nodes into nothing instead \n')
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
            replace_node(modified_tree, original_tree,
            int(node_df.iloc[line]['original']), int(node_df.iloc[line]['new']))
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
    POB_DIR = get_pob_dir()
    OrigTree_DIR = POB_DIR
    #detect if using Path of Building Source instead of using compiled code
    if os.path.isdir("POB_DIR/src/"):
        OrigTree_DIR = POB_DIR+'/src/TreeData/3_22/'
    else:
        OrigTree_DIR = POB_DIR+'/TreeData/3_22/'
    if os.path.isdir("POB_DIR/src/"):
        POB_DIR = POB_DIR+'/src/TreeData/Krangled3_22/'
    else:
        POB_DIR = POB_DIR+'/TreeData/Krangled3_22/'
    replace_all_nodes_wrapper(OrigTree_DIR, POB_DIR)
    #Editing copied file instead of replacing file in directory

if __name__ == "__main__":
    main()
