from io import TextIOWrapper
import time
from tkinter import INSIDE
import pandas as pd
import numpy as np
import glob
import subprocess
import os
import platform
import pathlib

class LuaSubNode(object):
    __slots__ = ["parentKey", "name", "nodeLevel", "topLevelKey", "subnodes", "hasListInfo", "nodeContent"]
    def __init__(self, parentKey:str, name, nodeLevel, topLevelKey):
        #Can detect if parent is from topLevel by lack of _ character in name
        self.parentKey:str = parentKey
        #if name is '{', then node is a grouping node that stores other nodes inside {}
        self.name = name
        #Keynames based on (parent's topLevelKey or subnode's name if parent is in LuaNode)+_+name (can't use lists as key so using string instead)
        #  If name is starts with '{' and ends with number of index in parentnode, then is using {} grouping (such as for mastery node)  
        #  use name[1,-1] to extract information about index
        self.topLevelKey = topLevelKey
        self.hasListInfo = False
        self.nodeContent:str = ''
        #Actual subnodes stored inside the parent LuaNode (key refers to topLevelKey, value refers to name)
        self.subnodes:dict[str,str]={}
        #if nodeLevel == 2, then parent is one of LuaNodes (iteration level is equal to this)
        self.nodeLevel:int = nodeLevel
  
    def get_name(self):
        return self.name

    def get_nodeLevel(self):
        return self.nodeLevel

    def get_topLevelKey(self):
        return self.topLevelKey

    def get_hasListInfo(self):
        return self.hasListInfo

    def hasSubNodes(self):
        return len(self.subnodes)!=0
        
    def get_subNodeKey(self, name):
        return self.topLevelKey+'_'+name

    def isParentTopLevel(self):
        return '_' not in self.parentKet
    
    def nodePosition(self):
        #using _ separators for find node position inside tree
        position:list[str] = []
        stringBuffer:str = ''
        for lineChar in self.topLevelKey:
            if(lineChar=='_'and stringBuffer!=''):
                position.append(stringBuffer)
                stringBuffer = ''
            else:
                stringBuffer += lineChar
        return position
        
    def printDebugInfo(self, subnodekeyName:str=''):
        if subnodekeyName =='':
            print('Subnode node named '+self.name+' content:\n')
        else:
            print('Subnode node named '+self.name+' (keyname:'+subnodekeyName+')content:\n')
        print(" has "+str(len(self.subnodes))+' subnodes.\n')
        for nodeKey, nodeData in self.subnodes.items():
            print('Detected subnode '+nodeKey+" with name of "+nodeData.name+'.\n')
            print(" has "+str(len(nodeData.subnodes))+' subnodes.\n')
            if nodeKey=='\"nodes\"':
                hasIcon:bool = False
                isPossibleNormalNode:bool = True
                for subData in nodeData.subnodes.values:
                    if subData=='"isNotable"':
                        print('Notable node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='"isMastery"':
                        print('Nullifying mastery node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='"ascendancyName"':
                        print('Ascendancy node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='\"isJewelSocket\"':
                        print('Jewel node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='\"icon\"':
                        hasIcon = True
                        break
                if(isPossibleNormalNode and hasIcon):
                    print('Normal skill node with id '+nodeKey+' is stored.\n')
                elif(isPossibleNormalNode):
                    print('Node with id '+nodeKey+' is stored.\n')

class LuaNode(object):
    __slots__ = ["name", "nodeContent", "subnodes", "recursiveSubNodes"]
    def __init__(self, name:str):
        self.name = name
        self.nodeContent = ''
        #Node ID data stored at this level (the first subnodes are added here, rest get added to recursiveSubNodes)
        #  keys for these refer to the name of the subnode, with the actual values refering to the subnode
        self.subnodes:dict[str, LuaSubNode] = {}
        #["name"] and other fields stored here (access via self.subnodes[NodeId]
        self.recursiveSubNodes:dict[str, LuaSubNode] = {}
    
    def get_name(self):
        return self.name
    
    def hasSubNodes(self):
        return len(self.subnodes)!=0

    def get_childNode(self, subNodeName, childNodeName):
        childKey:str = self.subnodes[subNodeName].get_subNodeKey(childNodeName)
        self.recursiveSubNodes[childKey]
    
    def add_SubNodeFromTopLevel(self, name:str=''):
        topLevelKey:str = self.name+'_'+name
        self.subnodes[topLevelKey] = LuaSubNode(self.name, name, 2, topLevelKey)
        return topLevelKey;

    def add_GroupNodeFromTopLevel(self):
        nodeKey:str = '{'+str(len(self.subnodes))
        self.subnodes[nodeKey] = LuaSubNode(self.name, '{', 2, nodeKey)
        return nodeKey;
    
    def add_SubNodeToSubnode(self, name:str, parentSubnode:LuaSubNode):
        #parentsubNode is self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.topLevelKey+'_'+name
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, name, parentSubnode.nodeLevel+1, topLevelKey)
        #Making sure subnode gets child added
        parentSubnode.subnodes[topLevelKey] = name
        return topLevelKey

    def add_GroupNodeToSubnode(self, parentSubnode:LuaSubNode):
        #parentsubNode is self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        nodePostfix:str = '{'+str(len(parentSubnode.subnodes))
        topLevelKey:str = parentSubnode.topLevelKey+'_'+nodePostfix
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '{', parentSubnode.nodeLevel+1, topLevelKey)
        #Making sure subnode gets child added
        parentSubnode.subnodes[topLevelKey] = '{'
        return topLevelKey

    def add_SubNodeToSubnodeFromKey(self, name:str, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        nodeKey:str = parentSubnode.topLevelKey+'_'+name
        self.recursiveSubNodes[nodeKey] = LuaSubNode(parentSubnodeKey, name, parentSubnode.nodeLevel+1, nodeKey)
        #Making sure subnode gets child added
        self.recursiveSubNodes[parentSubnodeKey].subnodes[nodeKey] = name
        return nodeKey
    
    #Adding to subnode using key info
    def add_GroupNodeToSubnodeFromKey(self, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        nodePostfix:str = '{'+str(len(parentSubnode.subnodes))
        topLevelKey:str = parentSubnode.topLevelKey+'_'+nodePostfix
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnodeKey, '{', parentSubnode.nodeLevel+1, topLevelKey)
        #Making sure subnode gets child added(directly using value reference to make sure doesn't edit a copy of node)
        self.recursiveSubNodes[parentSubnodeKey].subnodes[topLevelKey] = '{'
        return topLevelKey
        
    # '"isMastery"' in nodeData.subnodes:
    def isMasteryNode(self, skillNode:LuaSubNode):
        return '"isMastery"' in skillNode.subnodes.values()
    
    #'"ascendancyName"' in nodeData.subnodes:
    def isAscendancyNode(self, skillNode:LuaSubNode):
        return '"ascendancyName"' in skillNode.subnodes.values()
    
    def isNotableNode(self, skillNode:LuaSubNode):
        # '"isNotable"' in nodeData.subnodes:
        return '"isNotable"' in skillNode.subnodes.values()

    def isJewelSocket(self, skillNode:LuaSubNode):
        # '"isJewelSocket"' in nodeData.subnodes:
        return '"isJewelSocket"' in skillNode.subnodes.values()
    
    def isNotJewelSocket(self, skillNode:LuaSubNode):
        # '"isJewelSocket"' not in nodeData.subnodes.:
        return '"isJewelSocket"' not in skillNode.subnodes.values()

    def printDebugInfo(self, topLevelkeyName:str=''):
        if topLevelkeyName =='':
            print('TopLevel node named '+self.name+'content:\n')
        else:
            print('TopLevel node named '+self.name+' (keyname:'+topLevelkeyName+')content:\n')
        print(" has "+str(len(self.subnodes))+' subnodes with those subnodes having a total of '+str(len(self.recursiveSubNodes))+'.\n')
        for nodeKey, nodeData in self.subnodes.items():
            nodeData.printDebugInfo(nodeKey)

class ScanInfo:
    __slots__ = ["scanLevel", "scanBuffer", "topLevelKey"]
    def __init__(self, scanLevel, scanBuffer, topLevelKey):
        self.scanLevel = scanLevel
        self.scanBuffer = scanBuffer
        self.topLevelKey = topLevelKey
        
    def get_scanLevel(self):
        return self.scanLevel
    
    def get_scanBuffer(self):
        return self.scanBuffer

    def get_topLevelKey(self):
        return self.topLevelKey
    
    def set_scanLevel(self, value:str):
        self.scanLevel = value
    
    def set_scanBuffer(self, value:str):
        self.scanBuffer = value
        
    def append_Buffer(self, value:str):
        self.scanBuffer += value

    def set_topLevelKey(self, value:str):
        self.set_topLevelKey = value

    def reset_scanLevel(self):
        self.scanLevel = ''
    
    def reset_scanBuffer(self):
        self.scanBuffer = ''
        
    def reset_scans(self):
        self.scanBuffer = ''
        self.scanLevel = ''

    def reset_topLevelKey(self):
        self.set_topLevelKey = ''
 
class TreeStorage:
    __slots__ = ["RootStart", "topLevel"]
    def __init__(self, fileData:list[str]):
        #Lines starting from top of file until first top level node group start stored here
        self.RootStart:str = ''
        #top level nodes such as "nodes" and "max_x" initialized here (topLevel['\"nodes\"'] to access skill node data)
        self.topLevel:dict[str, LuaNode] = {}
        if(fileData!={}):
            self.generateNodeTree(fileData)

    def recursiveNodeOutput(self, f:TextIOWrapper, currentTopLevelNode:LuaNode, parentNode:LuaSubNode):
        if(parentNode.hasListInfo):
            if(parentNode.nodeContent==''):
                f.write('\"]= {}\n')
            else:
                f.write('\"]= {\n')
                f.write(parentNode.nodeContent)
                f.write('\n}')
        elif(parentNode.hasSubNodes()):#{
            f.write(parentNode.get_nodeLevel*' '+'['+parentNode.name+']= {')#[240]= { #skillTree ID is outputted at this level for first instance of this function if skillTree nodes
            actualSubNode:LuaSubNode;
            #separate variable to prevent needing to reduce level after exit for loop
            nodeLevel:int = parentNode.get_nodeLevel
            for i, node in enumerate(parentNode.subnodes):
            #{#Need to retrieve actual subNode info from topLevelNode
                if i:#Every element but the first element in list
                    f.write(',\n')
                if(node.name=='{'):#{
                    #for use for subobject of ["masteryEffects"] node for {} grouping for effects
                    f.write((parentNode.get_nodeLevel+1)*' '+'{')
                    self.recursiveNodeOutput(f, currentTopLevelNode, parentNode)
                    f.write((parentNode.get_nodeLevel+1)*' '+'}')
                #}
                else:
                    f.write((parentNode.get_nodeLevel+1)*' '+'[')
                    actualSubNode = currentTopLevelNode.recursiveSubNodes[node]
                    f.write(node.name)# ["name"]= at this level for first instance of this function if skillTree nodes
                    f.write('\"]= ')
                    self.recursiveNodeOutput(f, currentTopLevelNode, parentNode, nodeLevel+1)
            #}
            f.write(parentNode.get_nodeLevel*' '+'}')
        else:
            f.write(parentNode.get_nodeLevel*' '+'['+parentNode.name+']= '+parentNode.nodeContent)

    def reconstructAndSave_Tree(self, outputDirectory, fname='tree.lua'):
        fullPath:str
        if(outputDirectory=='./Debug/'):
            fullPath = './Debug/'+'treeOutput.lua'
        else:
            fullPath = outputDirectory+fname
    #   print('Saving edited tree to '+fullPath+'. \n')
        with open(fullPath,'w') as f:
            f.write(self.RootStart)
            for topLevelNode in self.topLevel:#{
                f.write('    [\"')
                f.write(topLevelNode.name)#outputs ["nodes"]= { at this level
                f.write('\"]= ')
                if skillTreeNode.hasListInfo:#["imageZoomLevels"] has information at this level
                    print('Placeholder')
                elif topLevelNode.hasSubNodes()==False:
                    f.write(topLevelNode.nodeContent)
                    f.write(',\n')
                else:#if(topLevelNode.hasSubNodes()):
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
                        elif topLevelNode.hasSubNodes()==False:
                            print('Placeholder')
                        else:
                            self.recursiveNodeOutput(f, self[topLevelNode].subnodes, skillTreeNode)
                    #}
            #}
            f.write(skillTreeNode.RootEnd)
            f.close();

    def recursivelyLoadNodeInput(self, lineChar:str, ScanningInfo:ScanInfo, keyPosition:list[str], indentationLevel=3):
        if ScanningInfo.scanLevel=='':
            if lineChar=='{':
                ScanningInfo.set_scanLevel('{')
            elif(lineChar=='}'):#Exiting Node level
                --indentationLevel;
                keyPosition.pop();#removing last position data
        elif ScanningInfo.scanLevel=='{' and lineChar=='[':
            ScanningInfo.set_scanLevel('[')
        #Grouping node
        elif ScanningInfo.scanLevel=='{' and lineChar=='{':
            ScanningInfo.get_scanLevel('classinfo')
            #ParentNode == self.topLevel[topLevelKey].recursiveSubNodes[keyPosition[-1]]
            currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_GroupNodeToSubnode(self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]])
            if(currentNodeKey not in self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes):
                print("Failed to add grouping subnode:'+currentNodeKey+' to Tree at indentation level "+str(indentationLevel))
            keyPosition.append(currentNodeKey)
        elif ScanningInfo.scanLevel=='classinfo' and lineChar=='[':
            indentationLevel += 1
            ScanningInfo.set_scanLevel('[')
        elif ScanningInfo.scanLevel=='[':
            if lineChar==']':
                if(keyPosition[-1] not in self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes):
                    print(keyPosition[-1]+' not detected within '+ScanningInfo.topLevelKey+'\'s recursive subnode storage.\n')
                    return -1#force early exit on error(-1 breaks the loop)
                subNodeKey:str = self.topLevel[ScanningInfo.topLevelKey].add_SubNodeToSubnode(ScanningInfo.scanBuffer, self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]])#Add node to Tree
                if(currentNodeKey not in self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes):
                    print("Failed to add subnode:'+subNodeKey+' to Tree at indentation level "+str(indentationLevel))
                keyPosition.append(subNodeKey)
                ScanningInfo.reset_scanBuffer()
                ScanningInfo.set_scanLevel('nextOrContent')#Search for either node content or subnodes
            else:
                ScanningInfo.append_Buffer(lineChar)
        elif ScanningInfo.scanLevel=='nextOrContent':#Searching for subnodes like ["name"] or in rare cases search for node content value
            if lineChar=='{':
                indentationLevel += 1
                ScanningInfo.reset_scanLevel()
                indentationLevel = self.recursivelyLoadNodeInput(lineChar, ScanningInfo, keyPosition, indentationLevel)
            elif lineChar!=' ' and lineChar!='=':#["points"]'s groups ["totalPoints"]= uses this
                ScanningInfo.set_scanLevel('nodeContent')
                ScanningInfo.set_scanBuffer(lineChar)
        elif ScanningInfo.scanLevel=='nodeContent':
            if lineChar==',' or lineChar=='\n':
                self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]].nodeContent = ScanningInfo.scanBuffer
                keyPosition.pop();#removing last position data
            else:
                ScanningInfo.append_Buffer(lineChar);
        return indentationLevel#making sure to pass values back to main function

    def generateNodeTree(self, fileData:list[str]):
        # self.topLevel:dict[str, LuaNode] = dict()
        topLevel_luaNodeLineNumber = -1
        lineNumber = -1
        #
        currentNodeKey:str
        currentNodeName:str
        #Can be passed as reference unlike string information and keeps better track of node position
        keyPosition:list[str] = []

        #Indentation level for topLevel nodes are at 1 indentation, actual data for nodes starts at 2 indentation
        #Might remove and just check size of keyPosition
        indentationLevel = 2;
        
        #scanLevel:str = ''
        #scanBuffer = ''
        #topLevelKey = ''
        #Making use of python's object references to treat variable information as pass-by-reference equivalent
        ScanningInfo:ScanInfo = ScanInfo('','','')

        for line in fileData:#{
            lineNumber += 1;
            if(topLevel_luaNodeLineNumber==-1):#Add to root level before actual node info starts
            #{
                if '[' in line:#{
                    topLevel_luaNodeLineNumber = lineNumber;
                #}
                else:#{
                    self.RootStart += line;
                #}
            #}
            #Start scanning actual info(indentation level for topLevel nodes are at 1 indentation,)
            if topLevel_luaNodeLineNumber!=-1:#{
                for lineChar in line:#{
                    if ScanningInfo.topLevelKey=='':#{ (indentationLevel==1) at this point
                        if ScanningInfo.scanLevel=='' and lineChar=='[':
                            ScanningInfo.set_scanLevel('insideTopLevelNodeName')
                            ScanningInfo.reset_scanBuffer()
                        elif lineChar==']':#["nodes"]= created at this point
                            if ',' in line:
                                self.topLevel[ScanningInfo.topLevelKey] = LuaNode(ScanningInfo.scanBuffer)
                            else:
                                ScanningInfo.topLevelKey = ScanningInfo.scanBuffer
                                self.topLevel[ScanningInfo.topLevelKey] = LuaNode(ScanningInfo.topLevelKey)
                            if(ScanningInfo.topLevelKey not in self.topLevel):
                                print("Failed to add topLevelNode:'+ScanningInfo.topLevelKey+' to Tree")
                            ScanningInfo.reset_scans()
                        elif ScanningInfo.scanLevel=='insideTopLevelNodeName':
                            ScanningInfo.append_Buffer(lineChar);
                    #}
                    else:#{
                        if indentationLevel==2:#Scanning for NodeId now (node added to subnodes once scanned)
                            if ScanningInfo.scanLevel=='':
                                if lineChar=='{':
                                    ScanningInfo.set_scanLevel('{')
                                elif lineChar=='}':#Exiting topLevelKey (ignoring the comma that might be after)
                                    ScanningInfo.reset_topLevelKey()
                                    keyPosition.pop();#removing last position data
                            #classes subgroup has {} as subgroups for class information such as for ascendancies
                            elif ScanningInfo.scanLevel=='{' and lineChar=='{':
                                ScanningInfo.set_scanLevel('classinfo')
                                currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_GroupNodeFromTopLevel()
                                if(currentNodeKey not in self.topLevel[ScanningInfo.topLevelKey].subnodes):
                                    print("Failed to add grouping subnode:'+currentNodeKey+' to Tree")
                                keyPosition.append(currentNodeKey)
                            elif ScanningInfo.scanLevel=='classinfo' and lineChar=='[':
                                indentationLevel = 3
                                ScanningInfo.set_scanLevel('[')
                            elif ScanningInfo.scanLevel=='{' and lineChar=='[':
                                ScanningInfo.set_scanLevel('[')
                            elif ScanningInfo.scanLevel=='[':
                                if lineChar==']':
                                    currentNodeName = ScanningInfo.scanBuffer
                                    ScanningInfo.reset_scanBuffer()
                                    currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_SubNodeFromTopLevel(currentNodeName, ScanningInfo.topLevelKey)#Add node to Tree (SkillNodeID created here)
                                    if(currentNodeKey not in self.topLevel[ScanningInfo.topLevelKey].subnodes):
                                        print("Failed to add subnode:'+currentNodeKey+' to Tree")
                                    ScanningInfo.set_scanLevel('nextOrContent')#Search for either node content or subnodes(should only need to find subnodes for skilltree nodes).
                                else:
                                    ScanningInfo.append_Buffer(lineChar)
                            elif ScanningInfo.scanLevel=='nextOrContent':#Searching for subnodes like ["name"] or in rare cases search for node content value
                                if lineChar=='{':
                                    indentationLevel = 3
                                    keyPosition.append(currentNodeKey)
                                    ScanningInfo.reset_scanLevel()
                                elif lineChar!=' ' and lineChar!='=':#["points"]'s groups ["totalPoints"]= uses this
                                    ScanningInfo.set_scanLevel('nodeContent')
                                    ScanningInfo.set_scanBuffer(lineChar)
                            elif ScanningInfo.scanLevel=='nodeContent':
                                if lineChar==',' or lineChar=='\n':
                                    self.topLevel[ScanningInfo.topLevelKey].subnodes[ScanningInfo['currentNodeKey']].nodeContent = ScanningInfo.scanBuffer
                                else:
                                    ScanningInfo.append_Buffer(lineChar);
                        else:
                            #At indentationLevel==3, scanning for things like ["name"] now (node added to subnodes once scanned)
                            indentationLevel  = self.recursivelyLoadNodeInput(lineChar, ScanningInfo, keyPosition, indentationLevel)
                    #}
            #}
            if indentationLevel==-1:#forcing early end to loop because of error
                break;
        #}
        
        print('Finished loading lua file into node tree.  '+str(lineNumber)+" lines total scanned.\n")

    def nullify_mastery_node(self, nodeKeyID:str):
        #Label nodes as Unknown Mastery and give every possible mastery effect or turn into normal nullified node(mastery nodes crash client if have no effects)
        print('Placeholder')

    def nullify_ascendancy_node(self, nodeKeyID:str):
        print('Placeholder')
        
    def nullify_notable_node(self, nodeKeyID:str):
        #same as nullify_normal_node except give a different image
        print('Placeholder')

    def nullify_normal_node(self, nodeKeyID:str):
        print('Placeholder')

    def nullifyAllSkillTreeNodes(self):
        if '\"nodes\"' in self.topLevel:
            for nodeKey, nodeData in self.topLevel['\"nodes\"'].items():
                if '"isNotable"' in nodeData.subnodes:
                    print('Nullifying notable node with id '+nodeKey+'.\n')
                    self.nullify_notable_node(nodeKey)
                elif '"isMastery"' in nodeData.subnodes:
                    print('Nullifying mastery node with id '+nodeKey+'.\n')
                    self.nullify_mastery_node(nodeKey)
                elif '"ascendancyName"' in nodeData.subnodes:
                    print('Nullifying ascendancy node with id '+nodeKey+'.\n')
                    self.nullify_ascendancy_node(nodeKey)
                #Make sure to skip jewel nodes
                elif self.topLevel.isNotJewelSocket(nodeData):
                    print('Nullifying node with id '+nodeKey+'.\n')
                    self.nullify_normal_node(nodeKey)
        else:
            print('Error:Nodes group doesn\'t exist inside file')

    def printDebugInfo(self):
        print("Listing top level nodes and information about each skill node detected")
        for topLevelNodeKey, topLevelNodeData in self.topLevel.items():
            topLevelNodeData.printDebugInfo(topLevelNodeKey)
        
    def replace_node(self, original_topLevel:dict[str, LuaNode], node_id:str, replace_id:str):
        print('Placeholder')

    def replace_nodes(self, original_topLevel:dict[str, LuaNode], nodeReplacementInfo:dict[str, str]):
        print('Placeholder')

    def nullifyUnusedNodes(self, original_topLevel:dict[str, LuaNode], nodeReplacementInfo:dict[str, str]):
        #Returning those keys not replaced on list based on https://stackoverflow.com/questions/35713093/how-can-i-compare-two-lists-in-python-and-return-not-matches
        #For those inside original_tree.topLevel['\"nodes\"'].subnodes.keys() but not inside nodeReplacementInfo
        if '\"nodes\"' in original_topLevel:
            skillTreeNodes = original_topLevel['\"nodes\"']
            nonReplacedNodeIds:list[str] = [x for x in skillTreeNodes.subnodes.keys() if x not in nodeReplacementInfo]
            for nodeKey in nonReplacedNodeIds:
                if '\"isNotable\"' in original_topLevel['\"nodes\"'].subnodes[nodeKey].subnodes:
                    print('Nullifying notable node with id '+nodeKey+'.\n')
                    self.nullify_notable_node(nodeKey)
                elif '\"isMastery\"' in original_topLevel['\"nodes\"'].subnodes[nodeKey].subnodes:
                    print('Nullifying mastery node with id '+nodeKey+'.\n')
                    self.nullify_mastery_node(nodeKey)
                elif '\"ascendancyName\"' in original_topLevel['\"nodes\"'].subnodes[nodeKey].subnodes:
                    print('Nullifying ascendancy node with id '+nodeKey+'.\n')
                    self.nullify_ascendancy_node(nodeKey)
                #Make sure to skip jewel nodes
                elif self.topLevel.isJewelSocket(original_topLevel['\"nodes\"'].subnodes[nodeKey]):# elif '\"isJewelSocket\"' not in original_topLevel['\"nodes\"'].subnodes[nodeKey].subnodes:
                    print('Nullifying node with id '+nodeKey+'.\n')
                    self.nullify_normal_node(nodeKey)
        else:
            print('Error:Nodes group doesn\'t exist inside file')
        
def load_tree(outputDirectory, fname='tree.lua'):
    fullPath = outputDirectory+fname
 #   print('Loading tree from '+fullPath+'. \n')
    return open(outputDirectory+'/tree.lua','r').readlines()

def replace_all_nodes(inputDirectory, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
    originalFileData = load_tree(inputDirectory)
    #Parsing lines into nodes instead
    original_tree:TreeStorage = TreeStorage(originalFileData)
    original_tree.printDebugInfo()
    modified_tree:TreeStorage = original_tree
    nodeReplacementInfo:dict[str, str]={}

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
        nothingness_dupes = node_df[node_df['original'].duplicated(keep=False)]
        node_df = node_df.drop(nothingness_dupes[nothingness_dupes['new']==-1].index)

        if any(node_df['original'].duplicated()):
            print('WARNING: mismatched duplicate nodes found:')
            for node_id in np.where(node_df['original'].duplicated())[0]:
                print('mismatch original node: '+str(node_df.iloc[node_id]['original'])) #+', new: '+str(node_df.iloc[node_id]['new']))

        for line in range(len(node_df)):
            nodeReplacementInfo[node_df.iloc[line]['original']] = node_df.iloc[line]['new']

        #Test NodeTree generation and reconstruction before creating new code for replacing nodes
        modified_tree.replace_nodes(original_tree.topLevel, nodeReplacementInfo)

        modified_tree.nullifyUnusedNodes(original_tree.topLevel, nodeReplacementInfo)
    #}
    modified_tree.reconstructAndSave_Tree(outputDirectory)

#Use breakpoints at error message prints in Visual Studio to find bugs in json file

def get_pob_dir():
    # open the text file for reading and read the first line of the file, which contains the directory path
    POBInstallLocation = ""
    pob_location = open("pob_location.txt", "r")
    POBInstallLocation = pob_location.readline().rstrip()
    pob_location.close()

    # check if the file is empty, and get directory from user input if it is empty
    if POBInstallLocation == "":
        POBInstallLocation = input("Please enter the directory where your Path of Building(root folder;not the data folder) is located: ")
        file = open("pob_location.txt", "w")
        file.write(POBInstallLocation)
        file.close()

    return POBInstallLocation

def main():
    POBInstallLocation = get_pob_dir()
    #Edit dataFolderInputOverride.txt file to override OrigTree_DIR default pathing
    OrigTreeOverrideData = open("dataFolderInputOverride.txt", "r")
    OrigTreeOverride:str = OrigTreeOverrideData.readline().rstrip()
    OrigTreeOverrideData.close()
    OrigTree_DIR:str
    KrangledData_DIR:str
    if OrigTreeOverride == "./Debug/":
        OrigTree_DIR = './Debug/'
    elif OrigTreeOverride == "":
        #detect if using Path of Building Source instead of using compiled code
        if os.path.isdir("POB_DIR/src/"):
            OrigTree_DIR = POBInstallLocation+'/src/TreeData/3_22/'
        else:
            OrigTree_DIR = POBInstallLocation+'/TreeData/3_22/'
    else:
        OrigTree_DIR = OrigTreeOverride
    if OrigTreeOverride == './Debug/':
        KrangledData_DIR = './Debug/'
    else:
        #Edit dataFolderOutputOverride.txt file to override OrigTree_DIR default pathing
        OrigTreeOverrideData = open("dataFolderOutputOverride.txt", "r")
        OutputOverride:str = OrigTreeOverrideData.readline().rstrip()
        OrigTreeOverrideData.close()
        if OutputOverride == "":
            if os.path.isdir("POB_DIR/src/"):
                KrangledData_DIR = POBInstallLocation+str('/src/TreeData/Krangled3_22/')
            else:
                KrangledData_DIR = POBInstallLocation+str('/TreeData/Krangled3_22/')
        else:
            KrangledData_DIR = OutputOverride
    replace_all_nodes(OrigTree_DIR, KrangledData_DIR)
    #Editing copied file instead of replacing file in directory

if __name__ == "__main__":
    main()
