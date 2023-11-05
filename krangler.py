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
    if len(all_jsons) < 1:
        print('No JSON files found in data directory...Converting all nodes into nothing instead \n')
        #Replace with code that doesn't use json file later
        all_node_data = pd.read_json('all_nodes_nothingness.json', typ='series')
        node_df = pd.DataFrame(all_node_data).reset_index().rename(columns = {'index':'original', 0:'new'})
        node_df = node_df.drop_duplicates()
        nothingness_dupes = node_df[node_df['original'].duplicated(keep=False)]
        node_df = node_df.drop(nothingness_dupes[nothingness_dupes['new']==-1].index)
        for line in range(len(node_df)):
            replace_node_with_nothing(modified_tree, original_tree, int(node_df.iloc[line]['original']))
    else:
        #Files need to follow stringify 4 space format with 2 spaces on bracket or similar format or will fail to read json files (minify format will most likely fail)
        all_node_data = pd.concat([pd.read_json(json_file, typ='series', dtype='dict', encoding_errors='ignore') for json_file in all_jsons], verify_integrity=True)
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
            replace_node(modified_tree, original_tree,
                    int(node_df.iloc[line]['original']), int(node_df.iloc[line]['new']))

    save_tree(modified_tree, outputDirectory)

#Use breakpoints at error message prints in Visual Studio to find bugs in json file

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
    is_MismatchedType = False
    if type(node_id) == str:#checking if string formated node id is found?
        node_found, node_id = get_node_id_by_name(original_tree, node_id)
        if not(node_found):
            print('Original string node with id:'+ str(node_id) +' not found. \n')
            return modified_tree
    else:
        node_found, node_id = get_node_id_by_name(original_tree, node_id)
        if not(node_found):
            print('Original non-string node with id:'+ str(node_id) +' not found. \n')
            return modified_tree
    replace_found = False
    replacement_found_by_name = False
    node_start = 0
    node_end = 0
    if replace_id==-1:
        replace_found = True
    else:
        if type(replace_id) == str:
            #checking if replacement node exists by name on original tree
            replace_found, replace_id = get_node_id_by_name(original_tree, replace_id)
            if replace_found == False:
                #if replacement node doesn't exist by name, check if exists by id on original tree
                node_found, node_start, node_end = get_node_by_id(original_tree, node_id)
                if replace_id > 0 and replace_found:
                    replace_found, replace_start, replace_end = get_node_by_id(original_tree, replace_id)
                    if replace_found == False:
                        print('Replacement '+str(replace_id)+' for node '+str(node_id)+' not found \n')
            
    is_ascendancy = False
    is_mastery = False
    for line_idx in range(node_end-node_start):
        if 'ascendancyName' in original_tree[node_start]:
            if replace_found:
                if 'ascendancyName' in modified_tree[node_start]:
                    ascendancy_line = modified_tree[node_start]
                else:
                    print('Replacement node does not match node type')
                    is_MismatchedType = True
            else:
                replace_lines = [
'            [\"name\"] = \"Ascendancy Replacement Error for node '+str(node_id)+' with invalid id '+str(replace_id)+'\",\n',
'            [\"icon\"] = \"Art/2DArt/SkillIcons/passives/MasteryBlank.png\",\n',
'            [\"ascendancyName\"] = \"None\",\n',
'            [\"stats\"] = {},\n']
                replace_start = 0
                replace_end = 4
            is_ascendancy = True
        modified_tree.pop(node_start)
    if replace_id > 0:
        replace_lines = original_tree[replace_start:replace_end]
    elif is_ascendancy:
        replace_lines = NOTHINGNESS_ASCENDANCY
        replace_start = 0
        replace_end = 4
    else:
        replace_lines = NOTHINGNESS
        replace_start = 0
        replace_end = 3
    for replace_idx, line_idx in enumerate(range(node_start, node_start+replace_end-replace_start)):
        if 'ascendancyName' in replace_lines[replace_idx]:
            try:
                modified_tree.insert(line_idx, ascendancy_line)
            except:
                print('error: node '+str(node_id)+'; replace: '+str(replace_id))
        else:
            modified_tree.insert(line_idx, replace_lines[replace_idx])
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
