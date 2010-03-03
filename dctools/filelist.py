import xml.parsers.expat

class Entity:
    def __init__(self, tag, attrs):
        self.tag = tag;
        self.children = list();
        self.parent = None;
    
    def append(self, c):
        self.children.append(c);

class File(Entity):
    def __init__(self, tag, attrs):
        self.tth = attrs.pop("TTH", None)
        self.name = attrs.pop("Name", None)
        self.size = attrs.pop("Size", None)
        Entity.__init__(self, tag, attrs);
    
    def repr(self):
        return self.name;

class Directory(Entity):
    def __init__(self, tag, attrs):
        self.subdirs = dict();
        self.name = attrs.pop("Name", "")
        Entity.__init__(self, tag, attrs);
    
    def repr(self):
        return self.name + "/";
    
    def append(self, c):
        self.children.append(c);
        if isinstance(c, Directory):
            self.subdirs[c.name] = c;

class FileListing(Directory):
    """
    Root element in a filelist.
    """
    def __init__(self, tag, attrs):
        attrs["Name"] = "";
        Directory.__init__(self, tag, attrs);

class FileList:
    def __init__(self, fobj):
        self.tth = dict();
        self.names = dict();
        self.root = None;
        self.tree = list();
        
        self.p = xml.parsers.expat.ParserCreate();
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        self.p.ParseFile(fobj);

    def start_element(self, name, attrs):
        e = None;

        if name == 'File':
            e = File(name, attrs);
            self.tth[e.tth] = e;
            self.names[e.name] = e;
        elif name == 'Directory':
            e = Directory(name, attrs);
        elif name == 'FileListing':
            e = FileListing(name, attrs);
            self.root = e;
            self.tree.append(self.root);
            return;

        e.parent = self.tree[-1];
        self.tree.append(e);

    def end_element(self, name):
        e = self.tree.pop();
        assert e.tag == name;

        if e == self.root:
            return;

        self.tree[-1].append(e);

    def char_data(self, data):
        pass;
        #print 'Character data:', repr(data)

def find(root, current, path):
    if path == "":
        return current;
    
    if path[0] == '/':
        current = root;
        path = path[1:]
    
    dirs = path.split("/");
    
    while len(dirs) > 0:
        if current is None:
            return None;

        if dirs[0] == "" or dirs[0] == ".":
            dirs = dirs[1:];
            continue;

        if dirs[0] == "..":
            current = current.parent;
            dirs = dirs[1:];
            continue;
        
        current = current.subdirs.get(dirs[0], None)
        
        if not isinstance(current, Directory):
            return None;
        
        dirs = dirs[1:];
    
    return current;

def findcomplete(root, current, path):
    return path.split("/");