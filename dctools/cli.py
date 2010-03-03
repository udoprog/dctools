import os
import cmd
import bz2

import dctools.filelist;

class TerminalInterpreter(cmd.Cmd):
    identchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_/"
    prompt = "> "
    
    def __init__(self):
        import readline;
        cmd.Cmd.__init__(self);
        self.open_list = None;
        self.current = None;
        readline.set_completer_delims(' \t\n');
    
    def do_ls(self, text):
        if not self.open_list:
            self.stdout.write("No open lists\n");
            return;
        
        n = dctools.filelist.find(self.open_list.root, self.current, text);
        
        if not n:
            self.stdout.write("not a directory: " + text + "\n");
            return;

        if len(n.children) == 0:
            self.stdout.write("(empty directory)\n");
            return;
        
        for c in n.children:
            self.stdout.write(c.repr() + "\n");
    
    def do_cd(self, text):
        if not self.open_list:
            self.stdout.write("No open lists\n");
            return;

        n = dctools.filelist.find(self.open_list.root, self.current, text);
        
        if not n:
            self.stdout.write("not a directory: " + text + "\n");
            return;
        
        self.current = n;
    
    def complete_cd(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);
    
    def do_open(self, text):
        if self.open_list:
            del self.open_list;
        
        try:
          self.open_list = dctools.filelist.FileList(bz2.BZ2File(text, "r"));
        except Exception, e:
          self.stdout.write(str(e) + "\n");
        
        self.current = self.open_list.root;
    
    def complete_ls(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);

    def _complete_dir(self, text, line, begidx, endidx):
        if not self.open_list:
            return [];
        
        if len(text) > 0 and text[-1] == "/":
            n = dctools.filelist.find(self.open_list.root, self.current, text);
            return map(lambda p: text + p.repr(), n.children);
        else:
            dirs = text.split("/");
            dirname = "/".join(dirs[:-1]);
            basename = dirs[-1];
            
            n = dctools.filelist.find(self.open_list.root, self.current, dirname);
            
            if not n:
                return [];
            
            if basename == "..":
                dirname += "/..";
                basename = "";
            
            return map(lambda p: os.path.join(dirname, p.repr()), filter(lambda c: c.name.startswith(basename), n.children));
    
    def help_ls(self):
        self.stdout.write("test\n");
        return "TEST";
