import xml.parsers.expat
import collections;

Directory = collections.namedtuple('Directory', 'name children parent')
File = collections.namedtuple('File', 'name tth size parent')

def repr_entity(e):
    if isinstance(e, Directory):
        return e.name + "/";
    elif isinstance(e, File):
        return e.name;
    else:
        return "";

def build_path(e):
    if not e:
        return "/";
    
    parts = list();
    if e.name == "":
        return "/";

    return e.name;
    
#    parts.append(e.name);
#    
#    parent = e.parent;
#
#    while parent is not None:
#        parts.append(e.name);
#        parent = parent.parent;
#    
#    parts.reverse();
#    return "/".join(parts);

def directory_append(d, c):
    d.children.append(c);

def build_file(name, attrs, parent):
    return File(attrs.pop("Name", None), attrs.pop("TTH", None), int(attrs.pop("Size", None)), parent);

def build_directory(name, attrs, parent):
    return Directory(attrs.pop("Name"), list(), parent);

def build_filelisting(name, attrs):
    return Directory("", list(), None);

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
        del self.p;

    def start_element(self, name, attrs):
        e = None;

        if name == 'File':
            e = build_file(name, attrs, self.tree[-1]);
            self.tth[e.tth] = e;
            self.names[e.name] = e;
        elif name == 'Directory':
            e = build_directory(name, attrs, self.tree[-1]);
        elif name == 'FileListing':
            e = build_filelisting(name, attrs);
            self.root = e;
            self.tree.append(self.root);
            return;
        
        self.tree.append(e);

    def end_element(self, name):
        e = self.tree.pop();
        if e == self.root:
            return;
        directory_append(self.tree[-1], e);

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
        
        for child in current.children:
            if fnmatch.fnmatch(child.name, parts[0]):
                for cr in rlist(child, parts[1:]):
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
        
        for child in current.children:
            if fnmatch.fnmatch(child.name, parts[0]):
                for cr in rlist(child, parts[1:]):
                    result.append(cr);
        
        return result;
    
    return rlist(current, parts);
