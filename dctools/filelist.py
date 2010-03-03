import xml.parsers.expat

class Entity:
    def __init__(self, tag, attrs):
        self.name = attrs.pop("Name", "")
        self.tag = tag;
        self.children = list();
        self.parent = None;
    
    def append(self, c):
        self.children.append(c);
    
    def path(self):
        parts = list();
        if self.name == "":
            return "/";
        
        parts.append(self.name);
        
        parent = self.parent;

        while parent is not None:
            parts.append(parent.name);
            parent = parent.parent;

        parts.reverse();
        return "/".join(parts);

class File(Entity):
    def __init__(self, tag, attrs):
        self.tth = attrs.pop("TTH", None)
        self.size = attrs.pop("Size", None)
        Entity.__init__(self, tag, attrs);
    
    def repr(self):
        return self.name;

class Directory(Entity):
    def __init__(self, tag, attrs):
        self.subentity = dict();
        Entity.__init__(self, tag, attrs);
    
    def repr(self):
        return self.name + "/";
    
    def append(self, c):
        self.children.append(c);
        self.subentity[c.name] = c;

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
    import fnmatch;

    if path == "":
        return current.children;
    
    parts = path.split("/");
    
    if len(parts) <= 0:
        return current.children;
    
    # then we are at root
    if parts[0] == "":
        current = root;
        parts = parts[1:];
    
    def rlist(current, parts):
        result = list();
        
        if current is None:
            return [];
        
        while True and len(parts) > 0:
            if parts[0] == "" or parts[0] == ".":
                parts = parts[1:];
                continue;
            
            if parts[0] == "..":
                current = current.parent;
                parts = parts[1:];
                continue;
            
            break;

        if len(parts) <= 0:
            return current.children;
        
        if isinstance(current, File):
            return [];
        
        for ent in current.subentity:
            if fnmatch.fnmatch(ent, parts[0]):
                for cr in rlist(current.subentity[ent], parts[1:]):
                    result.append(cr);

        return result;
    
    return rlist(current, parts);

def findentity(root, current, path):
    import fnmatch;

    if path == "":
        return [current];
    
    parts = path.split("/");
    
    if len(parts) <= 0:
        return [current];
    
    # then we are at root
    if parts[0] == "":
        current = root;
        parts = parts[1:];
    
    def rlist(current, parts):
        result = list();
        
        if current is None:
            return [];
        
        while True and len(parts) > 0:
            if parts[0] == "" or parts[0] == ".":
                parts = parts[1:];
                continue;
            
            if parts[0] == "..":
                current = current.parent;
                parts = parts[1:];
                continue;
            
            break;
        
        if len(parts) <= 0:
            return [current];
        
        if isinstance(current, File):
            if len(parts) == 1:
                return [current];
            else:
                return [];
        
        for ent in current.subentity:
            if fnmatch.fnmatch(ent, parts[0]):
                for cr in rlist(current.subentity[ent], parts[1:]):
                    result.append(cr);
        
        return result;
    
    return rlist(current, parts);
