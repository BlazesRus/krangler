from krangler import load_tree
import pandas as pd

def load_node_tree():
    full_tree = load_tree()
    # node_tree = full_tree[10553:77185] #full_tree[:69505]
    node_tree = full_tree[10553:72688] #full_tree[:69505]
    return node_tree

def find_all_nodes(start_idx=0):
    tree = load_node_tree()
    df = pd.DataFrame(columns=['type','id','name','stats'])
    node_found = True
    while node_found:
        node_found, start_idx, node_type, node, node_name, stats_lines = find_next_node(tree, start_idx)
        if node_found:
            temp_df = pd.DataFrame([{'type':node_type,
                                    'id':node,
                                    'name':node_name,
                                    'stats':stats_lines}])
            df = pd.concat([df,temp_df])
        start_idx+=2
    return df

def find_next_node(tree, start_idx=0):
    node_found = False
    node = -1
    node_start_idx = -1
    stats_lines = []
    node_type = 'invalid'
    node_name = 'invalid'
    for line_idx, line in enumerate(tree[start_idx:]):
        if "[\"skill\"]" in line:
            node_start_idx = line_idx+start_idx-1
            node = tree[node_start_idx].rsplit('[')[1].rsplit(']')[0]
            node_found = True
            if node_found:
                node_name = tree[node_start_idx+2].rsplit(']')[1][3:-3]
                for line_idx, line in enumerate(tree[node_start_idx:]):
                    if '[\"group\"]' in line:
                        node_end_idx = node_start_idx+line_idx
                        node_end_found = True
                        node_data = tree[node_start_idx:node_end_idx]
                        break
                # try:
                for line_idx, line in enumerate(node_data):
                    is_keystone = check_for_keystone(node_data)
                    is_ascendancy, ascendancy_name = check_for_ascendancy(node_data)
                    is_notable = check_for_notable(node_data)
                    is_jewel = check_for_jewel(node_data)
                    is_mastery = check_for_mastery(node_data)
                # except:
                #     print('node name: '+str(node_name))
                #     print('line idx: '+str(line_idx))
                #     print('line: '+str(line))

                if is_keystone:
                    node_type = 'keystone'
                elif is_ascendancy and is_notable:
                    node_type = 'ascendancy_'+ascendancy_name+'_notable'
                elif is_ascendancy:
                    node_type = 'ascendancy_'+ascendancy_name
                elif is_notable:
                    node_type = 'notable'
                elif is_jewel:
                    node_type = 'jewel'
                elif is_mastery:
                    node_type = 'mastery'
                else:
                    node_type = 'small'
                if node_type not in ['invalid', 'jewel', 'mastery']:
                    for line_idx, line in enumerate(node_data):
                        if '[\"stats\"]' in line:
                            stats_lines = []
                            for line in node_data[line_idx+1:]:
                                if '},' in line:
                                    break
                                stats_lines.append(line.rsplit('\"')[1]+', ')
                    stats_lines = ''.join(stats_lines)[:-2]
                break
    return node_found, node_start_idx, node_type, node, node_name, stats_lines

def check_for_keystone(subtree):
    for line_idx, line in enumerate(subtree):
        if '[\"isKeystone\"]' in line:
            return True
    return False

def check_for_ascendancy(subtree):
    for line_idx, line in enumerate(subtree):
        if '[\"ascendancyName\"]' in line:
            return True, line.rsplit(']')[1][3:-3]
    return False, 'none'

def check_for_notable(subtree):
    for line_idx, line in enumerate(subtree):
        if '[\"isNotable\"]' in line:
            return True
    return False

def check_for_jewel(subtree):
    for line_idx, line in enumerate(subtree):
        if '[\"isJewelSocket\"]' in line:
            return True
    return False

def check_for_mastery(subtree):
    for line_idx, line in enumerate(subtree):
        if '[\"isMastery\"]' in line:
            return True
    return False

def get_regular_nodes():
    df = find_all_nodes().reset_index(drop=True)
    # regular_df = df[df.type.isin(['small','notable','mastery','keystone'])]
    regular_df = df[~df.type.isin(['jewel'])]
    regular_df['new'] = -1
    regular_df[['id','new']].to_csv('all_nodes.csv',index=False)
