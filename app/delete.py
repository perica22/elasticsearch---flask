import ipdb


# global list of id’s to keep track of already added files to tree,
# so we could skip searching for those which are not added
TREE_FILES = ["null"] # TO-DO: make this redis list at some point


class Tree:
    def __init__(self, root, leafs):
        self.root = root
        self.master = None # maybe when i am doing this init i could do init of Node and add it to branch 
        self.branch = None
        self.node = None
        self.leafs = leafs
        self.folders_list = []

    def create_node(self, data):
        self.node = data["_source"]
        self.node["_id"] = data["_id"]
        if self.node["DS_Type"] == "dir":
            self.node["children"] = []

    def add_node(self, obj, mode=None):
        if not self.branch:
            self.branch = obj
        elif mode:
            #ipdb.set_trace()
            for file in self.branch['children']:
                if file['_id'] != obj['_id']:
                    self.branch['children'].append(obj)
                    break
        elif "children" in obj:
            obj["children"].append(self.branch)
            self.branch = obj
        
        TREE_FILES.append(obj['_id'])
        self.root = self.branch["DS_Parent"]

    def merge(self, master_item, branch_item):
        if not self.master:
            self.master = self.branch
            self.branch=None
        else:
            #ipdb.set_trace() #infinite loop in case of folders
            try:
                while branch_item != []:
                    for branch_file in branch_item['children']:
                        for master_file in master_item['children']:
                            if master_file['_id'] in branch_file['_id']:
                                pass
                            else:
                                master_item['children'].append(branch_file)

                    if self.folders_list:
                        self._add_folders(master_item)
                    master_item = master_file
                    branch_item = branch_file

            except KeyError:
                self.branch = None
                return

    def _add_folders(self, path):
        #ipdb.set_trace()
        for folder in self.folders_list:
            if folder['DS_Parent'] == path['_id'] and folder['_id'] not in TREE_FILES:
                path['children'].append(folder)
                TREE_FILES.append(folder['_id'])
                self.folders_list.remove(folder)
