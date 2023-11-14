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

#forward references(based on https://stackoverflow.com/questions/19376923/how-to-use-a-type-defined-later-for-function-annotations)
class LuaSubNode: pass
class LuaNode: pass

class LuaSubNode(object):
    __slots__ = ["parentKey", "name", "nodeLevel", "topLevelKey", "subnodes", "nodeContent"]
    def __init__(self, parentKey:str, name, nodeLevel, topLevelKey):
        #Can detect if parent is from topLevel by lack of _ character in name
        self.parentKey:str = parentKey
        #if name is '{', then node is a grouping node that stores other nodes inside {}
        #if name is empty, then treat nodeContent element in lsit
        self.name = name
        #Keynames based on (parent's topLevelKey or subnode's name if parent is in LuaNode)+_+name (can't use lists as key so using string instead)
        #  If name is starts with '{' and ends with number of index in parentnode, then is using {} grouping (such as for mastery node)  
        #  use name[1,-1] to extract information about index
        self.topLevelKey = topLevelKey
        self.nodeContent:str = ''
        #Actual subnodes stored inside the parent LuaNode (key refers to topLevelKey, value refers to name or element value in case of list element)
        self.subnodes:dict[str,str]={}
        #if nodeLevel == 2, then parent is one of LuaNodes (iteration level is equal to this)
        self.nodeLevel:int = nodeLevel
  
    def get_name(self):
        return self.name

    def get_nodeLevel(self):
        return self.nodeLevel

    def get_topLevelKey(self):
        return self.topLevelKey

    def set_nodeContent(self, value:str):
        self.nodeContent = value

    def isListInfo(self):
        return self.name==''

    def hasSubNodes(self):
        return len(self.subnodes)!=0
        
    def get_subNodeKey(self, name):
        return self.topLevelKey+'_'+name

    def isParentTopLevel(self):
        return '_' not in self.parentKet
    
    # '"isMastery"' in nodeData.subnodes:
    def isMasteryNode(self):
        return '"isMastery"' in self.subnodes.values()
    
    #'"ascendancyName"' in nodeData.subnodes:
    def isAscendancyNode(self):
        return '"ascendancyName"' in self.subnodes.values()
    
    def isNotableNode(self):
        # '"isNotable"' in nodeData.subnodes:
        return '"isNotable"' in self.subnodes.values()

    def isJewelSocket(self):
        # '"isJewelSocket"' in nodeData.subnodes:
        return '"isJewelSocket"' in self.subnodes.values()
    
    def isNotJewelSocket(self):
        # '"isJewelSocket"' not in nodeData.subnodes.:
        return '"isJewelSocket"' not in self.subnodes.values()

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
            print(' '*8+'Subnode node named '+self.name+' content:\n')
        else:
            print(' '*8+'Subnode node named '+self.name+' (keyname:'+subnodekeyName+')content:\n')
        print(' '*8+"Subnode has "+str(len(self.subnodes))+' subnodes.\n')
        for nodeKey, nodeData in self.subnodes.items():
            print(' '*12+'Detected child subnode '+nodeKey+" with name of "+nodeData.name+'.\n')
            print(' '*12+"Child subnode has "+str(len(nodeData.subnodes))+' subnodes.\n')
            if nodeKey=='\"nodes\"':
                hasIcon:bool = False
                isPossibleNormalNode:bool = True
                for subData in nodeData.subnodes.values:
                    if subData=='"isNotable"':
                        print(' '*12+'Notable node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='"isMastery"':
                        print(' '*12+'Nullifying mastery node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='"ascendancyName"':
                        print(' '*12+'Ascendancy node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='\"isJewelSocket\"':
                        print(' '*12+'Jewel node with id '+nodeKey+' is stored.\n')
                        isPossibleNormalNode = False
                        break
                    elif subData=='\"icon\"':
                        hasIcon = True
                        break
                if(isPossibleNormalNode and hasIcon):
                    print(' '*12+'Normal skill node with id '+nodeKey+' is stored.\n')
                elif(isPossibleNormalNode):
                    print(' '*12+'Node with id '+nodeKey+' is stored.\n')

    def add_SubNodeToSubnode(self, name:str):
        #parentsubNode is self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = self.topLevelKey+'_'+name
        self.subnodes[topLevelKey] = name
        #Handling the topLevelNode changes inside topLevelFunction (topLevel[topLevelKey])
        return topLevelKey

    def add_GroupNodeToSubnode(self):
        #parentKey+_+name
        nodePostfix:str = '{'+str(len(self.subnodes))
        topLevelKey:str = self.topLevelKey+'_'+nodePostfix
        #Making sure subnode gets child added
        self.subnodes[topLevelKey] = '{'
        #Handling the topLevelNode changes inside topLevelFunction (topLevel[topLevelKey])
        return topLevelKey

    def add_ListNodeToSubnode(self, value:str):
        #parentKey+_+indexFromParent
        topLevelKey:str = self.topLevelKey+'_'+str(len(self.subnodes))
        #Making sure subnode gets child added
        self.subnodes[topLevelKey] = value
        #Handling the topLevelNode changes inside topLevelFunction (topLevel[topLevelKey])
        return topLevelKey
    
    def NodeOutputFromTopLevel(self, f:TextIOWrapper, currentTopLevelNode:LuaNode):
        indentation:str = ' '*8
        if(self.name=='{'):#Grouping node
            f.write(indentation+'{')
            self.recursiveNodeOutput(f, currentTopLevelNode, self)
            f.write(indentation+'}')
        elif(len(self.subnodes)==0):
            if(self.name==''):#isListInfo
                f.write(indentation+self.name)
            elif(self.nodeContent!=''):
                f.write(indentation+'[')
                f.write(self.name)#[240]= { #skillTree ID is outputted at this level
                f.write('\"]= '+self.nodeContent)
            else:
                f.write(indentation+'[')
                f.write(self.name)#[240]= { #skillTree ID is outputted at this level
                f.write('\"]= {}')
        else:
            f.write(indentation+'[')
            f.write(self.name)#[240]= { #skillTree ID is outputted at this level
            f.write('\"]= {')
            for i, subNodeKey in enumerate(self.subnodes.keys()):
            #{
                subNode = currentTopLevelNode.recursiveSubNodes[subNodeKey]
                if i:#Every element but the first element in list
                    f.write(',\n')
                subNode.recursiveNodeOutput(f, currentTopLevelNode, self)
            #}
            f.write(' '*8+'}')

    def recursiveNodeOutput(self, f:TextIOWrapper, currentTopLevelNode:LuaNode, parentSubnode:LuaSubNode):
        indentation:str = ' '*4*self.nodeLevel
        if(self.name=='{'):#Grouping node
            f.write(indentation+'{')
            self.recursiveNodeOutput(f, currentTopLevelNode, self)
            f.write(indentation+'}')
        elif(len(self.subnodes)==0):
            if(self.name==''):#isListInfo
                f.write(indentation+self.name)
            elif(self.nodeContent!=''):
                f.write(indentation+'[')
                f.write(self.name)#[240]= { #skillTree ID is outputted at this level
                f.write('\"]= '+self.nodeContent)
            else:
                f.write(indentation+'[')
                f.write(self.name)#[240]= { #skillTree ID is outputted at this level
                f.write('\"]= {}')
        else:
            f.write(indentation+'[')
            f.write(self.name)#[240]= { #skillTree ID is outputted at this level
            f.write('\"]= {')
            for i, subNodeKey in enumerate(self.subnodes.keys()):
            #{
                subNode = currentTopLevelNode.recursiveSubNodes[subNodeKey]
                if i:#Every element but the first element in list
                    f.write(',\n')
                subNode.recursiveNodeOutput(f, currentTopLevelNode, self)
            #}
            f.write(' '*8+'}')

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
    
    def set_nodeContent(self, value:str):
        self.nodeContent = value

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
        nodeKey:str = self.name+'_'+'{'+str(len(self.subnodes))
        self.subnodes[nodeKey] = LuaSubNode(self.name, '{', 2, nodeKey)
        return nodeKey;

    def add_ListNodeFromTopLevel(self, value:str):
        nodeKey:str = self.name+'_'+str(len(self.subnodes))
        self.subnodes[nodeKey] = LuaSubNode(self.name, '', 2, nodeKey)
        self.subnodes[nodeKey].nodeContent = value
        return nodeKey;
    
    def add_SubNodeToSubnode(self, name:str, parentSubnode:LuaSubNode):
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_SubNodeToSubnode(name)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, name, parentSubnode.nodeLevel+1, topLevelKey)
        return topLevelKey

    def add_GroupNodeToSubnode(self, parentSubnode:LuaSubNode):
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_GroupNodeToSubnode()
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '{', parentSubnode.nodeLevel+1, topLevelKey)
        return topLevelKey
    
    def add_ListNodeToSubnode(self, value:str, parentSubnode:LuaSubNode):
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_ListNodeToSubnode(value)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '', parentSubnode.nodeLevel+1, topLevelKey)
        self.recursiveSubNodes[topLevelKey].set_nodeContent(value)
        return topLevelKey

    def printDebugInfo(self, topLevelkeyName:str=''):
        if topLevelkeyName =='':
            print(' '*4+'TopLevel node named '+self.name+'content:\n')
        else:
            print(' '*4+'TopLevel node named '+self.name+' (keyname:'+topLevelkeyName+')content:\n')
        print(' '*4+'has '+str(len(self.subnodes))+' subnodes with those subnodes having a total of '+str(len(self.recursiveSubNodes))+'.\n')
        for nodeKey, nodeData in self.subnodes.items():
            nodeData.printDebugInfo(nodeKey)

class ScanInfo:
    __slots__ = ["scanLevel", "scanBuffer", "topLevelKey", "currentNodeKey"]
    def __init__(self):
        self.scanLevel = ''
        self.scanBuffer = ''
        self.topLevelKey = ''
        self.currentNodeKey = ''
        
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
        self.topLevelKey = value

    def reset_scanLevel(self):
        self.scanLevel = ''
    
    def reset_scanBuffer(self):
        self.scanBuffer = ''
        
    def reset_scans(self):
        self.scanBuffer = ''
        self.scanLevel = ''

    def reset_topLevelKey(self):
        self.topLevelKey = ''
 
class TreeStorage:
    __slots__ = ["RootStart", "topLevel"]
    def __init__(self, fileData:list[str]):
        #Lines starting from top of file until first top level node group start stored here
        self.RootStart:str = ''
        #top level nodes such as "nodes" and "max_x" initialized here (topLevel['\"nodes\"'] to access skill node data)
        self.topLevel:dict[str, LuaNode] = {}
        if(fileData!={}):
            self.generateNodeTree(fileData)

    def reconstructAndSave_Tree(self, outputDirectory, fname='tree.lua'):
        fullPath:str
        if(outputDirectory=='./Debug/'):
            fullPath = './Debug/'+'tree.lua'
        else:
            fullPath = outputDirectory+fname
    #   print('Saving edited tree to '+fullPath+'. \n')
        with open(fullPath,'w') as f:
            f.write(self.RootStart)
            for topLevelKey,topLevelNode in self.topLevel.items():#{
                f.write(' '*4+'[\"')
                f.write(topLevelNode.name)#outputs ["nodes"]= { at this level
                f.write('\"]= ')
                if topLevelNode.hasSubNodes()==False:
                    f.write(topLevelNode.nodeContent)
                    f.write(',\n')
                else:#if(topLevelNode.hasSubNodes()):
                    f.write('{\n')
                    for i, (subKey, subNode) in enumerate(topLevelNode.subnodes.items()):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')
                        subNode.NodeOutputFromTopLevel(f, topLevelNode)
                    #}
            #}
            f.write('}')
            f.close();

    def recursivelyLoadNodeInput(self, lineChar:str, ScanningInfo:ScanInfo, keyPosition:list[str], indentationLevel=3):
        if ScanningInfo.scanLevel=='':
            if lineChar=='{':
                ScanningInfo.set_scanLevel('{')
                if __debug__:
                    print(' '*4*indentationLevel+'{')
            elif(lineChar=='}'):#Exiting Node level
                --indentationLevel;
                if(keyPosition[-1]=='{'):#Only remove keyposition if current node is grouping node.
                    keyPosition.pop();#removing last position data
                if __debug__:
                    print(' '*4*indentationLevel+'}')
        elif ScanningInfo.scanLevel=='{' and lineChar=='[':
            ScanningInfo.set_scanLevel('[')
            if __debug__:
                print(' '*4*indentationLevel+'[', end='')
        #Grouping node
        elif ScanningInfo.scanLevel=='{' and lineChar=='{':
            ScanningInfo.get_scanLevel('classinfo')
            #ParentNode == self.topLevel[topLevelKey].recursiveSubNodes[keyPosition[-1]]
            ScanInfo.currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_GroupNodeToSubnode(self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]])
            if __debug__:
                print(' '*4*indentationLevel+'\{', end='')
            keyPosition.append(ScanInfo.currentNodeKey)
        elif ScanningInfo.scanLevel=='classinfo' and lineChar=='[':
            indentationLevel += 1
            ScanningInfo.set_scanLevel('[')
            if __debug__:
                print(' '*4*indentationLevel+'[', end='')
        elif ScanningInfo.scanLevel=='[':
            if lineChar==']':
                if(keyPosition[-1] not in self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes):
                    print(keyPosition[-1]+' not detected within '+ScanningInfo.topLevelKey+'\'s recursive subnode storage.\n')
                    return -1#force early exit on error(-1 breaks the loop)
                subNodeKey:str = self.topLevel[ScanningInfo.topLevelKey].add_SubNodeToSubnode(ScanningInfo.scanBuffer, self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]])#Add node to Tree
                if __debug__:
                    print(' '*4*indentationLevel+ScanningInfo.scanBuffer+']=', end='')
                keyPosition.append(subNodeKey)
                ScanningInfo.reset_scanBuffer()
                ScanningInfo.set_scanLevel('nextOrContent')#Search for either node content or subnodes
            else:
                ScanningInfo.append_Buffer(lineChar)
        elif ScanningInfo.scanLevel=='nextOrContent':#Searching for subnodes like ["name"] or in rare cases search for node content value
            if lineChar=='{':
                indentationLevel += 1
                ScanningInfo.reset_scanLevel()
                if __debug__:
                    print(' '*4*indentationLevel+'{')
                indentationLevel = self.recursivelyLoadNodeInput(lineChar, ScanningInfo, keyPosition, indentationLevel)
            elif lineChar!=' ' and lineChar!='=':#["points"]'s groups ["totalPoints"]= uses this
                ScanningInfo.set_scanLevel('nodeContent')
                ScanningInfo.set_scanBuffer(lineChar)
        elif ScanningInfo.scanLevel=='nodeContent':
            if lineChar==',' or lineChar=='\n':
                self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]].nodeContent = ScanningInfo.scanBuffer
                if __debug__:
                    print(' '*4*indentationLevel+ScanningInfo.scanBuffer+',')
                keyPosition.pop();#removing last position data
            else:
                ScanningInfo.append_Buffer(lineChar);
        elif ScanningInfo.scanLevel=='listInfo':
            if lineChar==',' or lineChar=='\n':
                subNodeKey:str = self.topLevel[ScanningInfo.topLevelKey].add_ListNodeToSubnode(ScanningInfo.scanBuffer, self.topLevel[ScanningInfo.topLevelKey].recursiveSubNodes[keyPosition[-1]])
                if __debug__:
                    print(' '*4*indentationLevel+ScanningInfo.scanBuffer+',')
                #keyPosition.append(subNodeKey)
                ScanningInfo.reset_scans()
            else:
                ScanningInfo.scanBuffer += lineChar
        elif lineChar!=' ' and lineChar=='\n':
            ScanningInfo.set_scanLevel('listInfo')
            ScanningInfo.set_scanBuffer(lineChar)
        return indentationLevel#making sure to pass values back to main function

    def generateNodeTree(self, fileData:list[str]):
        # # Forcing initialization
        # self.RootStart = ''
        # self.topLevel:dict[str, LuaNode] = {}

        topLevel_luaNodeLineNumber = -1
        lineNumber = -1

        currentNodeName:str
        #Can be passed as reference unlike string information and keeps better track of node position
        keyPosition:list[str] = []

        #Indentation level for topLevel nodes are at 1 indentation, actual data for nodes starts at 2 indentation
        #Might remove and just check size of keyPosition
        indentationLevel = 1;
        
        #scanLevel:str = ''
        #scanBuffer = ''
        #topLevelKey = ''
        #Making use of python's object references to treat variable information as pass-by-reference equivalent
        ScanningInfo:ScanInfo = ScanInfo()

        for line in fileData:#{
            lineNumber += 1;
            if(topLevel_luaNodeLineNumber==-1):#Add to root level before actual node info starts
            #{
                if '[' in line:#{
                    #print(self.RootStart, end='')
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
                            ScanningInfo.topLevelKey = ScanningInfo.scanBuffer
                            self.topLevel[ScanningInfo.topLevelKey] = LuaNode(ScanningInfo.topLevelKey)
                            if __debug__:
                                print(' '*4+'['+ScanningInfo.topLevelKey+']= ', end='')
                            if ',' not in line:
                                indentationLevel = 2
                            ScanningInfo.reset_scans()
                        elif ScanningInfo.scanLevel=='insideTopLevelNodeName':
                            ScanningInfo.append_Buffer(lineChar);
                    #}
                    elif(ScanningInfo.scanLevel=='ScanningTopLevelContent'):
                        print('Placeholder')
                    elif(ScanningInfo.scanLevel=='EnteringTopLevelSubOrListContent'):
                        print('Placeholder')
                    else:#{
                        if indentationLevel==1:#Scanning top level tag content
                            print('Placeholder')
                        elif indentationLevel==2:#Scanning for NodeId now (node added to subnodes once scanned)
                            print('Placeholder')
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
            for nodeKey, nodeData in self.topLevel['\"nodes\"'].subnodes.items():
                if nodeData.isNotableNode():
                    print('Nullifying notable node with id '+nodeKey+'.\n')
                    self.nullify_notable_node(nodeKey)
                elif nodeData.isMasteryNode():
                    print('Nullifying mastery node with id '+nodeKey+'.\n')
                    self.nullify_mastery_node(nodeKey)
                elif nodeData.isAscendancyNode():
                    print('Nullifying ascendancy node with id '+nodeKey+'.\n')
                    self.nullify_ascendancy_node(nodeKey)
                #Make sure to skip jewel nodes
                elif nodeData.isNotJewelSocket():
                    print('Nullifying node with id '+nodeKey+'.\n')
                    self.nullify_normal_node(nodeKey)
        else:
            print('Error:Nodes group doesn\'t exist inside file')

    def printDebugInfo(self):
        print("Total of "+str(len(self.topLevel))+' top level nodes detected.\n')
        print("Listing top level nodes and information about each skill node detected:\n")
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
                if original_topLevel['\"nodes\"'].subnodes[nodeKey].isNotableNode():
                    print('Nullifying notable node with id '+nodeKey+'.\n')
                    self.nullify_notable_node(nodeKey)
                elif original_topLevel['\"nodes\"'].subnodes[nodeKey].isMasteryNode():
                    print('Nullifying mastery node with id '+nodeKey+'.\n')
                    self.nullify_mastery_node(nodeKey)
                elif original_topLevel['\"nodes\"'].subnodes[nodeKey].isAscendancyNode():
                    print('Nullifying ascendancy node with id '+nodeKey+'.\n')
                    self.nullify_ascendancy_node(nodeKey)
                #Make sure to skip jewel nodes
                elif  original_topLevel['\"nodes\"'].subnodes[nodeKey].isNotJewelSocket():
                    print('Nullifying node with id '+nodeKey+'.\n')
                    self.nullify_normal_node(nodeKey)
        else:
            print('Error:Nodes group doesn\'t exist inside file')
        
def load_tree(inputDirectory, fname='tree.lua'):
    if(inputDirectory=='./Debug/'):
        fullPath = './Debug/'+'DebugInput.lua'
    else:
        fullPath = inputDirectory+fname
 #   print('Loading tree from '+fullPath+'. \n')
    return open(fullPath,'r').readlines()

def replace_all_nodes(inputDirectory, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
    originalFileData = load_tree(inputDirectory)
    #Parsing lines into nodes instead
    original_tree:TreeStorage = TreeStorage(originalFileData)
    #original_tree.printDebugInfo()
    modified_tree:TreeStorage = original_tree
    nodeReplacementInfo:dict[str, str]={}

    #if len(all_jsons) < 1:
    #{
        # print('No JSON files found in data directory...Converting all nodes into nothing instead \n')
        # modified_tree.nullifyAllSkillTreeNodes()
    #}
    # else:
    # #{
    #     #Files need to follow stringify 4 space format with 2 spaces on bracket or similar format or will fail to read json files (minify format will most likely fail)
    #     all_node_data = pd.concat([pd.read_json(json_file, typ='series', dtype='dict', encoding_errors='ignore') for json_file in all_jsons])
    #     #print('node_df stage starting \n')
    #     node_df = pd.DataFrame(all_node_data).reset_index().rename(columns = {'index':'original', 0:'new'})
    #     #print('dropping duplicates \n')
    #     node_df = node_df.drop_duplicates()
    #     nothingness_dupes = node_df[node_df['original'].duplicated(keep=False)]
    #     node_df = node_df.drop(nothingness_dupes[nothingness_dupes['new']==-1].index)

    #     if any(node_df['original'].duplicated()):
    #         print('WARNING: mismatched duplicate nodes found:')
    #         for node_id in np.where(node_df['original'].duplicated())[0]:
    #             print('mismatch original node: '+str(node_df.iloc[node_id]['original'])) #+', new: '+str(node_df.iloc[node_id]['new']))

    #     for line in range(len(node_df)):
    #         nodeReplacementInfo[node_df.iloc[line]['original']] = node_df.iloc[line]['new']

    #     #Test NodeTree generation and reconstruction before creating new code for replacing nodes
    #     #modified_tree.replace_nodes(original_tree.topLevel, nodeReplacementInfo)

    #     #modified_tree.nullifyUnusedNodes(original_tree.topLevel, nodeReplacementInfo)
    # #}
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
    if OrigTreeOverride == "./Debug/" or ".\\Debug\\":
        OrigTree_DIR = './Debug/'
    elif OrigTreeOverride == "":
        #detect if using Path of Building Source instead of using compiled code
        if os.path.isdir("POB_DIR/src/"):
            OrigTree_DIR = POBInstallLocation+'/src/TreeData/3_22/'
        else:
            OrigTree_DIR = POBInstallLocation+'/TreeData/3_22/'
    else:
        OrigTree_DIR = OrigTreeOverride
    if OrigTreeOverride == "./Debug/" or ".\\Debug\\":
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
