    #rework nodeOutput later after getting scanning code done
    def recursiveNodeOutput(self, f:TextIOWrapper, currentTopLevelNode:LuaNode, parentNode:LuaSubNode):
            # if(parentNode.nodeContent==''):
                
            # else:
            #     f.write('\"]= {\n')
            #     f.write(parentNode.nodeContent)
            #     f.write('\n}')
        if(parentNode.hasSubNodes()):#{
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
                    actualSubNode = currentTopLevelNode.recursiveSubNodes[node]
                    if(actualSubNode.isListInfo()):
                        f.write(actualSubNode.nodeLevel*' '+node.name)
                    else:
                        f.write(actualSubNode.nodeLevel*' '+'[')
                        f.write(node.name)# ["name"]= at this level for first instance of this function if skillTree nodes
                        f.write('\"]= ')
                        self.recursiveNodeOutput(f, currentTopLevelNode, parentNode, nodeLevel+1)
            #}
            f.write(parentNode.get_nodeLevel*' '+'}')
        elif(parentNode.nodeContent==''):
            f.write('\"]= {}\n')
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
                f.write(' '*4+'[\"')
                f.write(topLevelNode.name)#outputs ["nodes"]= { at this level
                f.write('\"]= ')
                if topLevelNode.hasListInfo:#["imageZoomLevels"] has information at this level
                    f.write('{')
                    for i, subNode in enumerate(self[topLevelNode].subnodes):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')
                        #f.write(' '*4+subNode.)
                    #}
                elif topLevelNode.hasSubNodes()==False:
                    f.write(topLevelNode.nodeContent)
                    f.write(',\n')
                else:#if(topLevelNode.hasSubNodes()):
                    for i, subNode in enumerate(self[topLevelNode].subnodes):
                    #{
                        if i:#Every element but the first element in list
                            f.write(',\n')
                        f.write('        [')
                        f.write(subNode.name)#[240]= { #skillTree ID is outputted at this level
                        f.write('\"]= ')
                        if(subNode.hasListInfo):#{
                            if(subNode.nodeContent==''):
                                f.write('\"]= {},\n')
                            else:
                                f.write('\"]= {\n')
                                f.write(subNode.nodeContent)
                                f.write('\n        },n')
                        #}
                        elif topLevelNode.hasSubNodes()==False:
                            print('Placeholder')
                        else:
                            self.recursiveNodeOutput(f, self[topLevelNode].subnodes, skillTreeNode)
                    #}
            #}
            f.write('}')
            f.close();