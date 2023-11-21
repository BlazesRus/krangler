import copy
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

class ScanInfo:
    __slots__ = ["scanLevel", "scanBuffer", "topLevelKey"]
    def __init__(self):
        self.scanLevel = ''
        self.scanBuffer = ''
        self.topLevelKey = ''
        
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
        #If both subnodes size is zero and content is zero, save as empty list with {}
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

    def printNodeContent(self, topLevelNode:LuaNode):
        actualSubnode:LuaSubNode
        if(self.name=='{'):
            print(' '*self.nodeLevel*4+'{')
            for i, nodeKey in enumerate(self.subnodes.keys()):
                if i:
                    print(',')
                actualSubnode = topLevelNode.recursiveSubNodes[nodeKey]
                actualSubnode.printNodeContent(topLevelNode)
            print(' '*self.nodeLevel*4+'}')
        elif(self.name==''):#List content
            print(' '*self.nodeLevel*4+self.nodeContent)
        else:
            print(' '*self.nodeLevel*4+'['+self.name+']', end='')
            if self.nodeContent != '':
                print('= '+self.nodeContent, end='')
            else:
                print('= {')
                for i, nodeKey in enumerate(self.subnodes.keys()):
                    if i:
                        print(',')
                    actualSubnode = topLevelNode.recursiveSubNodes[nodeKey]
                    actualSubnode.printNodeContent(topLevelNode)
                print(' '*4+'}')

    def saveNodeToFile(self, topLevelNode:LuaNode, f:TextIOWrapper):
        actualSubnode:LuaSubNode
        if(self.name=='{'):
            f.write(' '*self.nodeLevel*4+'{')
            for i, nodeKey in enumerate(self.subnodes.keys()):
                if i:
                    f.write(',\n')
                actualSubnode = topLevelNode.recursiveSubNodes[nodeKey]
                actualSubnode.saveNodeToFile(topLevelNode, f)
            f.write(' '*self.nodeLevel*4+'}')
        elif(self.name==''):#List content
            f.write(' '*self.nodeLevel*4+self.nodeContent)
        else:
            f.write(' '*self.nodeLevel*4+'['+self.name+']')
            if self.nodeContent != '':
                f.write('= '+self.nodeContent)
            else:
                f.write('= {\n')
                for i, nodeKey in enumerate(self.subnodes.keys()):
                    if i:
                        f.write(',\n')
                    actualSubnode = topLevelNode.recursiveSubNodes[nodeKey]
                    actualSubnode.saveNodeToFile(topLevelNode, f)
                f.write(' '*4+'}\n')

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
        currentSubNode = self.subnodes[topLevelKey]
        return topLevelKey, currentSubNode

    def add_GroupNodeFromTopLevel(self):
        nodeKey:str = self.name+'_'+'{'+str(len(self.subnodes))
        self.subnodes[nodeKey] = LuaSubNode(self.name, '{', 2, nodeKey)
        currentSubNode = self.subnodes[nodeKey]
        return nodeKey, currentSubNode

    def add_ListNodeFromTopLevel(self, value:str):
        nodeKey:str = self.name+'_'+str(len(self.subnodes))
        self.subnodes[nodeKey] = LuaSubNode(self.name, '', 2, nodeKey)
        self.subnodes[nodeKey].nodeContent = value
        currentSubNode = self.subnodes[nodeKey]
        return nodeKey, currentSubNode

    def add_SubNodeToPrimarySubnode(self, name:str, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.subnodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_SubNodeToSubnode(name)
        lowLevelNodes = self.recursiveSubNodes
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, name, parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode

    def add_EmptyListToPrimarySubnode(self, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.subnodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_SubNodeToSubnode('')
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '', parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode

    def add_GroupNodeToPrimarySubnode(self, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.subnodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_GroupNodeToSubnode()
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '{', parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode
    
    def add_ListNodeToPrimarySubnode(self, value:str, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.subnodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_ListNodeToSubnode(value)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '', parentSubnode.nodeLevel+1, topLevelKey)
        self.recursiveSubNodes[topLevelKey].set_nodeContent(value)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode
    
    def add_SubNodeToLowLevelNode(self, name:str, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_SubNodeToSubnode(name)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, name, parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode

    def add_EmptyListToLowLevelNode(self, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_SubNodeToSubnode('')
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '', parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode

    def add_GroupNodeToLowLevelNode(self, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_GroupNodeToSubnode()
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '{', parentSubnode.nodeLevel+1, topLevelKey)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode
    
    def add_ListNodeToLowLevelNode(self, value:str, parentSubnodeKey:str):
        parentSubnode:LuaSubNode = self.recursiveSubNodes[parentSubnodeKey]
        #parentKey+_+name
        topLevelKey:str = parentSubnode.add_ListNodeToSubnode(value)
        self.recursiveSubNodes[topLevelKey] = LuaSubNode(parentSubnode.topLevelKey, '', parentSubnode.nodeLevel+1, topLevelKey)
        self.recursiveSubNodes[topLevelKey].set_nodeContent(value)
        currentSubNode = self.recursiveSubNodes[topLevelKey]
        return topLevelKey, currentSubNode
    
    def set_primarySubNodeContent(self, topLevelKey:str, value:str):
        self.subnodes[topLevelKey].set_nodeContent(value)

    def set_lowLevelContent(self, topLevelKey:str, value:str):
        self.recursiveSubNodes[topLevelKey].set_nodeContent(value)

    def printNodeContent(self):
        print(' '*4+'['+self.name+']', end='')
        if self.nodeContent != '':
            print('= '+self.nodeContent, end='')
        else:
            print('= {')
            for i, nodeData in enumerate(self.subnodes.values()):
                if i:
                    print(',')
                nodeData.printNodeContent(self)
            print(' '*4+'}')

    def saveNodeToFile(self, f:TextIOWrapper):
        f.write(' '*4+'['+self.name+']')
        if self.nodeContent != '':
            f.write('= '+self.nodeContent)
        else:
            f.write('= {')
            for i, nodeData in enumerate(self.subnodes.values()):
                if i:
                    f.write(',\n')
                nodeData.saveNodeToFile(self, f)
            f.write(' '*4+'}')

class TreeStorage:
    __slots__ = ["RootStart", "topLevel"]
    def __init__(self):
        #Lines starting from top of file until first top level node group start stored here
        self.RootStart:str = ''
        #top level nodes such as "nodes" and "max_x" initialized here (topLevel['\"nodes\"'] to access skill node data)
        self.topLevel:dict[str, LuaNode] = {}

    def generateNodeTree(self, inputDirectory):
        if(inputDirectory=='./Debug/'):
            fullPath = './Debug/'+'DebugInput.lua'
        else:
            fullPath = inputDirectory+'tree.lua'
        topLevel_luaNodeLineNumber = -1
        lineNumber = -1
        #Can be passed as reference unlike string information and keeps better track of node position
        keyPosition:list[str] = []
        #Making use of python's object references to treat variable information as pass-by-reference equivalent
        ScanningInfo:ScanInfo = ScanInfo()
        currentTopLevel:LuaNode#Using as reference to current topLevel element
        currentNodeKey:str
        #lastNodeKey:str
        currentSubNode:LuaSubNode#Reference to last subnode added

        for line in open(fullPath,'r').readlines():#{
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
                        elif ScanningInfo.scanLevel=='insideTopLevelNodeName':
                            if lineChar==']':#["nodes"]= created at this point
                                ScanningInfo.topLevelKey = ScanningInfo.scanBuffer
                                #self.topLevel[ScanningInfo.topLevelKey] = LuaNode(ScanningInfo.topLevelKey)
                                self.topLevel.update({ScanningInfo.topLevelKey: LuaNode(ScanningInfo.topLevelKey)})
                                currentTopLevel = self.topLevel[ScanningInfo.topLevelKey]
                                ScanningInfo.reset_scanBuffer()
                            else:
                                ScanningInfo.append_Buffer(lineChar);
                    #}
                    elif lineChar=='=':
                        pass#Don't need to do anything here since just going to ignore the existance for now
                    elif lineChar=='}':
                        if ScanningInfo.scanLevel=='InsideListContent':
                            ScanningInfo.scanLevel = ''
                        else:
                            if len(keyPosition)==0:#Should be exiting TopLevelNode
                                ScanningInfo.reset_topLevelKey()
                            else:#keyPosition size is 1 when at 1st Subnode Level
                                keyPosition.pop();
                            if len(keyPosition)==1:#look for next subnode for topLevelNode
                                ScanningInfo.set_scanLevel('EnteringTopLevelSubOrListContent')
                                currentSubNode = currentTopLevel.subnodes[currentNodeKey]
                            elif len(keyPosition)>0:#Update current subnode
                                currentSubNode = currentTopLevel.recursiveSubNodes[currentNodeKey]
                    elif ScanningInfo.scanLevel=='InsideListContent':
                        if lineChar==',' or lineChar=='\n':
                            if len(keyPosition)==0:#parentNode is topLevelNode
                                currentTopLevel.add_ListNodeFromTopLevel(ScanningInfo.scanBuffer)
                            else:
                                if len(keyPosition)==1:#parentNode is 1st level subnode
                                    currentTopLevel.add_ListNodeToPrimarySubnode(ScanningInfo.scanBuffer, keyPosition[-1])
                                else:
                                    currentTopLevel.add_ListNodeToLowLevelNode(ScanningInfo.scanBuffer, keyPosition[-1])
                            ScanningInfo.reset_scanBuffer()
                        else:
                            ScanningInfo.append_Buffer(lineChar)

                    elif ScanningInfo.scanLevel == '':
                        if lineChar=='{':
                            if '{}' in line:#Empty list node
                                keyPosition.pop();
                            else:
                                ScanningInfo.scanLevel = '{'
                    
                    elif ScanningInfo.scanLevel == '{':
                        if lineChar=='[':
                            ScanningInfo.scanLevel = '['
                        elif lineChar=='{':#Add grouping node
                            if len(keyPosition)==0:#parentNode is topLevelNode
                                currentNodeKey, currentSubNode = currentTopLevel.add_GroupNodeFromTopLevel()
                            else:
                                if len(keyPosition)==1:#parentNode is 1st level subnode
                                    currentNodeKey, currentSubNode = currentTopLevel.add_GroupNodeToPrimarySubnode(keyPosition[-1])
                                else:
                                    currentNodeKey, currentSubNode = currentTopLevel.add_GroupNodeToLowLevelNode(keyPosition[-1])
                            keyPosition.append(currentNodeKey)
                        elif lineChar!=' ' and lineChar!='\n':
                            ScanningInfo.scanBuffer = lineChar
                            ScanningInfo.scanLevel = 'InsideListContent'
                    elif ScanningInfo.scanLevel == '[':
                        if lineChar==']':
                            #Add node to Tree
                            if len(keyPosition)==0:#parentNode is topLevelNode
                                currentNodeKey, currentSubNode = currentTopLevel.add_SubNodeFromTopLevel(ScanningInfo.scanBuffer)
                            else:
                                if len(keyPosition)==1:#parentNode is 1st level subnode
                                    currentNodeKey, currentSubNode = currentTopLevel.add_SubNodeToPrimarySubnode(ScanningInfo.scanBuffer, keyPosition[-1])
                                else:
                                    currentNodeKey, currentSubNode = currentTopLevel.add_SubNodeToLowLevelNode(ScanningInfo.scanBuffer, keyPosition[-1])
                            keyPosition.append(currentNodeKey)
                            ScanningInfo.reset_scanBuffer()
                            ScanningInfo.scanLevel = ']'#Search for either node content,subnodes, or for nodeContent value
                        elif lineChar==' ':
                            print("Bug:Encountered space inside of subnode name.")
                        elif lineChar==',':
                            print("Bug:Encountered , inside of subnode name.")
                        else:
                            ScanningInfo.append_Buffer(lineChar)
                    elif ScanningInfo.scanLevel == ']':
                        if lineChar=='{':
                            if '{}' in line:#Empty list node
                                keyPosition.pop()
                            else:
                                ScanningInfo.scanLevel = '{'
                    elif ScanningInfo.scanLevel == 'ScanningContent':
                        if lineChar==',' or lineChar=='\n':
                            if len(keyPosition)==0:#targetNode is topLevelNode
                                currentTopLevel.set_nodeContent(ScanningInfo.scanBuffer)
                                ScanningInfo.topLevelKey = ''
                            elif len(keyPosition)==1:#parentNode is 1st level subnode
                                currentSubNode.set_nodeContent(ScanningInfo.scanBuffer)
                            else:
                                currentSubNode.set_nodeContent(ScanningInfo.scanBuffer)
                            if len(keyPosition)>0:
                                keyPosition.pop();
                            ScanningInfo.reset_scans()
                        else:
                            ScanningInfo.append_Buffer(lineChar)
                    elif lineChar=='{':
                        ScanningInfo.scanLevel = '{'
                    elif lineChar=='[':
                        ScanningInfo.scanLevel = '['
                    elif lineChar!=' ' and lineChar!='\n':#Entering node content value
                        ScanningInfo.scanBuffer = lineChar
                        ScanningInfo.scanLevel = 'ScanningContent'
            #}
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

    def printNodeContent(self):
        for i, topLevelNodeData in enumerate(self.topLevel.values()):
            if i:
                print(',')
            topLevelNodeData.printNodeContent()
        
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
            
    def reconstructAndSave_Tree(self, outputDirectory, fname='tree.lua'):
        fullPath:str
        if(outputDirectory=='./Debug/'):
            fullPath = './Debug/'+'tree.lua'
        else:
            fullPath = outputDirectory+fname
    #   print('Saving edited tree to '+fullPath+'. \n')
        with open(fullPath,'w') as f:
            f.write(self.RootStart)
            for i, topLevelNode in enumerate(self.topLevel.values()):#{
                if i:
                    f.write(',\n')
                topLevelNode.saveNodeToFile(f)
            #}
            f.write('}')
            f.close();

def replace_all_nodes(inputDirectory, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
    #Parsing lines into nodes instead of editing the file data directly
    original_tree:TreeStorage = TreeStorage()
    original_tree.generateNodeTree(inputDirectory)
    original_tree.printNodeContent()
    modified_tree:TreeStorage = copy.deepcopy(original_tree)
    nodeReplacementInfo:dict[str, str]={}

    if len(all_jsons) < 1:
    #{
         print('No JSON files found in data directory...Converting all nodes into nothing instead \n')
        # modified_tree.nullifyAllSkillTreeNodes()
    #}
    else:
    #{
        #Files need to follow stringify 4 space format with 2 spaces on bracket or similar format or will fail to read json files (minify format will most likely fail)
        all_node_data = pd.concat([pd.read_json(json_file, typ='series', dtype='dict', encoding_errors='ignore') for json_file in all_jsons])
        node_df = pd.DataFrame(all_node_data).reset_index().rename(columns = {'index':'original', 0:'new'})
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
