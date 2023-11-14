                        if indentationLevel==1:#Scanning top level tag content
                            if lineChar==',':
                                self.topLevel[ScanningInfo.topLevelKey].set_nodeContent(ScanningInfo.scanBuffer)
                                if __debug__:
                                    print(ScanningInfo.scanBuffer+',')
                                ScanningInfo.topLevelKey = ''
                            elif lineChar!='=':
                                ScanningInfo.scanBuffer += lineChar
                        elif indentationLevel==2:#Scanning for NodeId now (node added to subnodes once scanned)
                            if ScanningInfo.scanLevel=='':
                                if lineChar=='{':
                                    ScanningInfo.set_scanLevel('{')
                                    if __debug__:
                                        print('{')#should print right before topLevel nodes end of line containing name of top level node
                                elif lineChar=='}':#Exiting topLevelKey (ignoring the comma that might be after)
                                    ScanningInfo.reset_topLevelKey()
                                    if __debug__:
                                        print(' '*8+'}')
                                    # if(keyPosition[-1]=='{'):#Only remove keyposition if current node is grouping node.
                                    #     keyPosition.pop();#removing last position data
                                    indentationLevel = 1
                            #classes subgroup has {} as subgroups for class information such as for ascendancies
                            elif ScanningInfo.scanLevel=='{' and lineChar=='{':
                                ScanningInfo.set_scanLevel('classinfo')
                                ScanInfo.currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_GroupNodeFromTopLevel()
                                if __debug__:#Printing input information to console
                                    print(' '*8+'{', end='')
                                keyPosition.append(ScanInfo.currentNodeKey)
                            elif ScanningInfo.scanLevel=='classinfo' and lineChar=='[':
                                indentationLevel = 3
                                ScanningInfo.set_scanLevel('[')
                            elif ScanningInfo.scanLevel=='{' and lineChar=='[':
                                ScanningInfo.set_scanLevel('[')
                            elif ScanningInfo.scanLevel=='[':
                                if lineChar==']':
                                    currentNodeName = ScanningInfo.scanBuffer
                                    ScanningInfo.reset_scanBuffer()
                                    ScanInfo.currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_SubNodeFromTopLevel(currentNodeName)#Add node to Tree (SkillNodeID created here)
                                    if __debug__:#Printing input information to console
                                        print(' '*8+'['+ScanInfo.currentNodeKey+']= ', end='')
                                    ScanningInfo.set_scanLevel('nextOrContent')#Search for either node content or subnodes(should only need to find subnodes for skilltree nodes).
                                    keyPosition.append(ScanInfo.currentNodeKey)
                                else:
                                    ScanningInfo.append_Buffer(lineChar)
                            elif ScanningInfo.scanLevel=='nextOrContent':#Searching for subnodes like ["name"] or in rare cases search for node content value
                                if lineChar=='{':
                                    indentationLevel = 3
                                    if __debug__:#Printing input information to console
                                        print('{')
                                    ScanningInfo.reset_scanLevel()
                                elif lineChar!=' ' and lineChar!='=':#["points"]'s groups ["totalPoints"]= uses this
                                    keyPosition.pop();#Removing if not entering subnode
                                    ScanningInfo.set_scanLevel('nodeContent')
                                    ScanningInfo.set_scanBuffer(lineChar)
                            elif ScanningInfo.scanLevel=='nodeContent':
                                if lineChar==',' or lineChar=='\n':
                                    self.topLevel[ScanningInfo.topLevelKey].subnodes[ScanningInfo['ScanInfo.currentNodeKey']].nodeContent = ScanningInfo.scanBuffer
                                    if __debug__:#Printing input information to console
                                        print(ScanningInfo.scanBuffer+',')
                                else:
                                    ScanningInfo.append_Buffer(lineChar);
                            elif ScanningInfo.scanLevel=='listInfo':
                                if lineChar==',' or lineChar=='\n':
                                    ScanInfo.currentNodeKey = self.topLevel[ScanningInfo.topLevelKey].add_ListNodeFromTopLevel(ScanningInfo.scanBuffer)
                                    if __debug__:#Printing input information to console
                                        print(ScanningInfo.scanBuffer+',')
                                    #keyPosition.append(ScanInfo.currentNodeKey)
                                    ScanningInfo.reset_scans()
                                else:
                                    ScanningInfo.scanBuffer += lineChar
                            elif lineChar!=' ' and lineChar=='\n':
                                ScanningInfo.set_scanLevel('listInfo')
                                ScanningInfo.set_scanBuffer(lineChar)
                        else:
                            #At indentationLevel==3, scanning for things like ["name"] now (node added to subnodes once scanned)
                            indentationLevel  = self.recursivelyLoadNodeInput(lineChar, ScanningInfo, keyPosition, indentationLevel)