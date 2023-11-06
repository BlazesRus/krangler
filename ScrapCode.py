	#Replace with code that doesn't use json file later
	# all_node_data = pd.read_json('all_nodes_nothingness.json', typ='series')
	# node_df = pd.DataFrame(all_node_data).reset_index().rename(columns = {'index':'original', 0:'new'})
	# node_df = node_df.drop_duplicates()
	# nothingness_dupes = node_df[node_df['original'].duplicated(keep=False)]
	# node_df = node_df.drop(nothingness_dupes[nothingness_dupes['new']==-1].index)
	# for line in range(len(node_df)):
	#     replace_node_with_nothing(modified_tree, original_tree, int(node_df.iloc[line]['original']))

	#Parsing lines into nodes instead
	inside_nodeLevel = False
	topLevel_luaNodeLineNumber = -1
	topLevel_luaNodeName = ''
	LineChar = '';
	#InsideLuaComment = false;
	lineNumber = -1;
	
	topLevelStorage = { "RootStart" : "" }

	for line in original_tree:#{
		++lineNumber;
		if(topLevel_luaNodeLineNumber==-1):#Add to root level before actual node info starts
		#{
			if(line.contains('[')):
			#{
				topLevel_luaNodeLineNumber = lineNumber;
				# if(StartedTagRead):#Only start saving scans once enter certain depth of xml file
				# #{
				#     if(InsideClosingTag):
				#     #{
				#         if(LineChar=='>'):
				#         #{
				#             if (CurrentTag == EntryTagName):#Exiting entry tag
				#             #{
				#                 EntryTagName.clear();
				#             #}
				#             else://Exiting inner tag 
				#             #{

				#             #}
				#             CurrentTag = "";//Reset it to clear buffer so next tag has fresh storage
				#             TagContentStage = 0;
				#             InsideClosingTag = false; InsideTag = false;
				#         #}
				#     }
				#     else if (InsideTag):
				#     #{
				#         if (LineChar == '>'):
				#         #{
				#             if (EntryTagName.empty()):
				#             #{
				#                 EntryTagName = CurrentTag;
				#             #}
				#             else
				#             #{ 
				#             #}
				#         #}
				#         else if (CurrentTag.empty())
				#         #{
				#             if (ScanBuffer.empty())
				#             #{
				#                 if (LineChar == '!')//Detecting potential Commented Out Parts
				#                     PotentialComment = true;
				#                 else if(LineChar=='/')
				#                 #{

				#                 #}
				#                 else if (LineChar != ' ' && LineChar != '	' && LineChar != '\n')
				#                     ScanBuffer += LineChar;
				#             #}
				#             else if (LineChar == '/')//Closed Tag without any arguments
				#             #{
				#                 CurrentTag = ScanBuffer;
				#                 ScanBuffer = "/";
				#             #}
				#             else if (LineChar == ' ' || LineChar == '	' || LineChar == '\n')
				#             #{
				#                 CurrentTag = ScanBuffer;
				#                 ScanBuffer.clear();
				#                 //if (LineChar != '\\')
				#                 //{
				#                 //    ScanningArgData = true; Stage = 0;
				#                 //}
				#             #}
				#             else if (LineChar != ' ' && LineChar != '	' && LineChar != '\n')
				#             #{
				#                 ScanBuffer += LineChar;
				#             #}
				#         #}
				#         ##------------------Scanning Argument Field/Values-------------------------------
				#         else:
				#         #{
				#             if (ScanBuffer.empty()):
				#             {
				#                 if (LineChar != ' ' && LineChar != '	' && LineChar != '\n')
				#                 {
				#                     ScanBuffer += LineChar;
				#                 }
				#             }
				#             else if (LineChar == ' ' || LineChar == '	' || LineChar == '\n')
				#             {
				#                 //CurrentTag = ScanBuffer;
				#                 ScanBuffer.clear();
				#                 //if (LineChar != '\\')
				#                 //{
				#                 //    ScanningArgData = true; Stage = 0;
				#                 //}
				#             }
				#             else if (LineChar != ' ' && LineChar != '	' && LineChar != '\n')
				#             {
				#                 ScanBuffer += LineChar;
				#             }
				#         }
				#     }
				#     else
				#     {
				#         if (LineChar == '<')
				#         {
				#             //Send Description field into tag target

				#             InsideTag = true; ScanBuffer.clear();
				#         }
				#         else//If description value is empty, add data to description field buffer
				#         {
				#             ScanBuffer += LineChar;
				#         }
				#     }
				# }
				# else
				# {
				#     #topLevelStorage[topLevel_luaNodeName] = line;
				#     if(line.contains('{')):
				#         inside_nodeLevel = True
				# }
			#}
			else:
			#{
				topLevelStorage["RootStart"] += line;
			#}
		#}
		elif inside_nodeLevel == False:
		#{
			if(line.contains('[')):
			#{
				topLevel_luaNodeLineNumber = lineNumber;
			#}
			else:
			#{
				if "RootEnd" in topLevelStorage:
					topLevelStorage["RootEnd"] += line;
				else:
					topLevelStorage["RootEnd"] = line;
			#}
		#}
		#else:
		#{
		#}
	#}

# Maybe returning value of current node group if non-integer node
def replace_node_with_nothing(modified_tree, original_tree, node_id):
    if type(node_id) == str:
        node_found, node_id = get_node_id_by_name(original_tree, node_id)
        if not(node_found):
            print('Original node string with id:'+ str(node_id) +' not found. \n')
            return modified_tree
    node_found, node_start, node_end = get_node_by_id(modified_tree, node_id)
    is_ascendancy = False
    is_mastery = False
    for line_idx in range(node_end-node_start):
        if 'ascendancyName' in original_tree[node_start]:
            ascendancy_line = original_tree[node_start]
            is_ascendancy = True
        modified_tree.pop(node_start)
    if is_ascendancy:
        replace_lines = NOTHINGNESS_ASCENDANCY
        replace_start = 0
        replace_end = 4
        #print('Replacing node id '+str(node_id)+' with blank ascendancy node.\n')
    else:
        replace_lines = NOTHINGNESS
        replace_start = 0
        replace_end = 3
        #print('Replacing node id '+str(node_id)+' with blank node.\n')
    for replace_idx, line_idx in enumerate(range(node_start, node_start+replace_end-replace_start)):
        if 'ascendancyName' in replace_lines[replace_idx]:
            try:
                modified_tree.insert(line_idx, ascendancy_line)
            except:
                print('ascendancy replace_idx replacement error: node '+str(node_id)+".\n")
        else:
            modified_tree.insert(line_idx, replace_lines[replace_idx])
    return modified_tree

def replace_node(modified_tree, original_tree, node_id, replace_id):
    Does_TargetNodeHaveID = False
    node_index = -1#avoid replacing parameter info
    node_start = -1
    node_end = -1
    if type(node_id) != str:#{
        #Check to make sure both replacement and node_id have same keytype
        if type(node_id) != str:
            Does_TargetNodeHaveID = True
        else:
            return
        node_found, node_start, node_end = get_node_by_id(original_tree, node_id)
        if not(node_found):
            print('Original node with id:'+ str(node_id) +' not found. \n')
            return
        #else:#maybe check if is mastery node and either skip or change the node
    #}
    else:
    #{
        #Check to make sure both replacement and node_id have same keytype
        if type(node_id) != str:
            return
            
        node_found, node_index = get_node_id_by_name(original_tree, node_id)
        if not(node_found):
            print('Original string node with name:'+ str(node_id) +' not found. \n')
            return
        else:
            print('Original string node with name:'+ str(node_id) +' found. \n')
    #}
    #is_MismatchedType = False
    is_ascendancy = False
    #is_mastery = False

    #Only replace non-parent group nodes
    if Does_TargetNodeHaveID:
    #{
        #if(p)

        #checking subnode information
        for line_idx in range(node_end-node_start):#{
            if 'ascendancyName' in original_tree[node_start]:
                if 'ascendancyName' in original_tree[replace_start]:
                    ascendancy_line = original_tree[node_start]
                else:
                    print('Mismatched ascendancy node named '+node_id+' attempted to replace with node'+str(replace_id)+'. \n')
                    return
            elif 'isMastery' in original_tree[node_start]:
                if 'isMastery' not in original_tree[node_start]:
                    print('Mismatched Mastery node named '+node_id+' attempted to replace with node'+str(replace_id)+'. \n')
                    return
            #checking to make sure not jewel socket
            elif 'isJewelSocket' in original_tree[node_start]:
                return modified_tree
            #Notibles can only be replaced with notibles
            elif 'isNotable' in original_tree[node_start]:
                if 'isNotable' not in original_tree[replace_start]:
                    print('Mismatched Notable node named '+node_id+' attempted to replace with node'+str(replace_id)+'. \n')
                    return
            #Remving last element from list
            modified_tree.pop(node_start)
        #}

        if replace_id > 0:
        #{
            replace_lines = original_tree[replace_start:replace_end]
        #}
        #Replacing every numbered Node with nothingness
        elif is_ascendancy:
            replace_lines = NOTHINGNESS_ASCENDANCY
            replace_start = 0
            replace_end = 4
        else:
            replace_lines = NOTHINGNESS
            replace_start = 0
            replace_end = 3

        for replace_idx, line_idx in enumerate(range(node_start, node_start+replace_end-replace_start)):#{
            if 'ascendancyName' in replace_lines[replace_idx]:
                try:
                    modified_tree.insert(line_idx, ascendancy_line)
                except:
                    print('error: node '+str(node_id)+'; replace: '+str(replace_id))
            else:
                modified_tree.insert(line_idx, replace_lines[replace_idx])
        #}
    #}
    else:
        replace_found, replacement_index  = get_node_id_by_name(original_tree, replace_id)
        if replace_found == False:
            print('Replacement '+str(replace_id)+' for node named '+node_id+' not found. \n')
            return modified_tree
        if(replacement_index!=-1):
        #{
            print('Matching replaceid('+str(replacement_index)+') found for replacement node named '+replace_id)
        #}
        #if node_id=="classes":#inside class info node
        #if node_id=="nodes":#inside node group storage


    return modified_tree

def get_node_by_id(tree, node_id):
    start_offset = 10553 #10261
    end_offset = 72688 #66842
    subtree = tree[start_offset:end_offset]
    node_str = '['+str(node_id)+']'
    node_start_found = False
    for line_idx, line in enumerate(subtree):
        if node_str in line:
            node_start_idx = line_idx+2
            node_start_found = True
            break
    if node_start_found:
        node_end_found = False
        for line_idx, line in enumerate(subtree[node_start_idx:]):
            if '[\"group\"]' in line:
                node_end_idx = node_start_idx+line_idx
                node_end_found = True
                break
    if node_start_found and node_end_found:
        return True, node_start_idx+start_offset, node_end_idx+start_offset
    else:
        return False, -1, -1

def get_node_id_by_name(tree, node_name):
    node_id_found = False
    node_id = -1
    for line_idx, line in enumerate(tree):
        if node_name in line:
            node_start_idx = line_idx-2
            node_id = tree[node_start_idx].rsplit('[')[1].rsplit(']')[0]
            node_id_found = True
            break
    return node_id_found, node_id
	

class LuaNode:
  def __init__(self, name, hasSubNodes, originalLineNumber=-1, nodeContent=''):
    self.name = name
    self.hasSubNodes = hasSubNodes
    self.originalLineNumber = originalLineNumber
    self.nodeContent = nodeContent
  
  def get_name(self):
    return self.name

class TreeStorage:
    def __init__(self, loadedData:list[str], topLevelStorage:Dict[str, LuaNode], RootStart = '', RootEnd = ''):
        self.loadedData = loadedData
        self.topLevelStorage = topLevelStorage
        self.RootStart = RootStart
        self.RootEnd = RootEnd
    topLevelStorage = { }
    def addTopLevelNode(value: Dict[str, LuaNode], name:str):
        topLevelStorage[name] = name;


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

def replace_all_nodes(modified_tree:TreeStorage, original_tree:TreeStorage, outputDirectory, basedir='./data/'):
    all_jsons = glob.glob(basedir+'*.json')
	

def reconstructAndSave_Tree(TreeStorage, outputDirectory, fname='tree.lua'):
    fullPath = outputDirectory+fname
 #   print('Saving edited tree to '+fullPath+'. \n')
    
    nodeWhitespace = 4;
    with open(fullPath,'w') as f:
        f.write(TreeStorage.RootStart)
        for topLevelNode in TreeStorage.topLevelStorage:#{
            f.write('    [\"')
            f.write(topLevelNode.name)
            f.write('\"]= ')
            if(topLevelNode.hasSubNodes==False):
                f.write(topLevelNode.nodeContent)
                f.write(',\n')
            elif(topLevelNode.name=='nodes'):
                nodeWhitespace = 8
                for i, skillTreeNode in enumerate(TreeStorage.nodeSubgroup):
                #{
                    if i:#Every element but the first element in list
                        f.write(',\n')
                    #skillTree node outputted at this [240]= {
                    if(skillTreeNode.hasListInfo):#{
                        f.write('\"]= {\n')
                        f.write(skillTreeNode.nodeContent)
                        f.write('        }')
                    #}
                    else:
                        f.write('        [')
                        f.write(skillTreeNode.name)
                        f.write('\"]= {')
                        #for "masteryEffects" skill
                        for i, node in enumerate(skillTreeNode.subnodes):
                        #{
                            if i:#Every element but the first element in list
                                f.write(',\n')
                            #for i, skillTreeNode in enumerate(TreeStorage.otherSubnodeStorage):
                                
                        #}
                        f.write('        },n')
                #}
            else:
                nodeWhitespace = 8
                for i, skillTreeNode in enumerate(TreeStorage.otherSubnodeStorage):
                #{
                    if i:#Every element but the first element in list
                        f.write(',\n')
                    f.write('        [')
                    f.write(skillTreeNode.name)
                    if(skillTreeNode.hasListInfo):#{
                        if(nodeContent==''):
                            f.write('\"]= {},\n')
                        else:
                            f.write('\"]= {\n')
                            f.write(skillTreeNode.nodeContent)
                            f.write('\n        },n')
                    #}
                    elif(skillTreeNode.hasSubNodes):#{
                        f.write('\"]= {\n')
                        for i, node in enumerate(TreeStorage.otherSubnodeStorage):
                        #{
                            if i:#Every element but the first element in list
                                f.write(',\n')
                            #for i, skillTreeNode in enumerate(TreeStorage.otherSubnodeStorage):
                                
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
            