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
        readline.set_completer_delims(' \t\n/');
    
    def do_ls(self, text):
        if not self.open_list:
            self.stdout.write("No open lists\n");
            return;
        
        n = dctools.filelist.findentity(self.open_list.root, self.current, text);
        
        if not n:
            self.stdout.write("not a directory: " + text + "\n");
            return;

        if len(n) == 0:
            self.stdout.write("(empty directory)\n");
            return;
        
        for r in n:
            if isinstance(r, dctools.filelist.Directory):
                self.stdout.write(r.path() + ":\n");
                
                for c in r.children:
                    self.stdout.write(c.repr() + "\n");
                    self.stdout.write("");
            else:
                self.stdout.write("Not a directory: " + r.path());
    
    def do_cd(self, text):
        if not self.open_list:
            self.stdout.write("No open lists\n");
            return;
        
        n = dctools.filelist.findentity(self.open_list.root, self.current, text);
        
        if not n:
            self.stdout.write("not a directory: " + text + "\n");
            return;
        
        if len(n) > 1:
            self.stdout.write("not a single match: " + text + "\n");
            return;
        
        self.current = n[0];
    
    def do_info(self, text):
        if not self.open_list:
            self.stdout.write("No open lists\n");
            return;
        
        for n in dctools.filelist.findentity(self.open_list.root, self.current, text):
            if isinstance(n, dctools.filelist.File):
                print "Name:", n.name;
                print "Size:", n.size;
                print "TTH:", n.tth;
                print "";
            else:
                print "Directory:", n.name;
                print "";
    
    def complete_info(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);

    def do_exit(self, text):
        import sys;
        sys.exit(0);
    
    def complete_cd(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);
    
    def do_open(self, text):
        if self.open_list:
            del self.open_list;
        
        try:
          self.open_list = dctools.filelist.FileList(bz2.BZ2File(text, "r"));
        except Exception, e:
          self.stdout.write(str(e) + "\n");
          return;
        
        self.current = self.open_list.root;
    
    def complete_ls(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);

    def _complete_dir(self, text, line, begidx, endidx):
        import fnmatch;

        if not self.open_list:
            return [];
        
        rest = " ".join(line.split(" ")[1:]);
        
        if text == "":
            lookup = rest;
        else:
            lookup = rest[:-len(text)];
        
        n = dctools.filelist.find(self.open_list.root, self.current, lookup);
        return map(lambda c: c.repr(), filter(lambda c: c.name.startswith(text), n))
        
        #if not self.open_list:
        #    return [];
        #print line, text;
        
    def help_ls(self):
        self.stdout.write("ls: list a directory\n");
    
    def help_cd(self):
        self.stdout.write("cd: change the current directory\n");

    def help_open(self):
        self.stdout.write("open: open a specific filelist\n");
