import os;
import cmd;
import bz2;
import sys;

import dctools.filelist;
import musync.printer;

class CliPrinter(musync.printer.TermCaps):
    def warning(self, *text):
        self._writeall(self.c.red, self._joinstrings(text), self.c.sgr0, "\n");

    def error(self, *text):
        self._writeall(self.c.red, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");
    
    def notice(self, *text):
        self._writeall(self.c.blue, self._joinstrings(text), self.c.sgr0, "\n");
    
    def boldnotice(self, *text):
        self._writeall(self.c.magenta, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");

    def partialnotice(self, *text):
        self._writeall(self.c.magenta, self._joinstrings(text), self.c.sgr0, "\n");

class TerminalInterpreter(cmd.Cmd):
    identchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_/"
    prompt = "> "
    
    def __init__(self, filelist):
        import readline;
        cmd.Cmd.__init__(self);

        self.printer = CliPrinter(self.stdout);
        
        self.printer.notice("Opening own file list...");
        
        self.own_list = dctools.filelist.FileList(bz2.BZ2File(filelist, "r"));
        
        self.open_list = None;
        self.current = None;
        self.handles = dict();
        readline.set_completer_delims(' \t\n/');
    
    def do_ls(self, text):
        if not self.open_list:
            self.printer.error("no open lists");
            return;
        
        n = dctools.filelist.findentity(self.open_list.root, self.current, text);
        
        if not n:
            self.printer.error("not a directory:", text);
            return;

        if len(n) == 0:
            self.printer.warning("(empty directory)");
            return;
        
        for r in n:
            if isinstance(r, dctools.filelist.Directory):
                self.printer.notice(dctools.filelist.build_path(r) + ":");
                
                for c in r.children:
                    if isinstance(c, dctools.filelist.File):
                        if self.own_list.tth.has_key(c.tth):
                            self.printer.notice(dctools.filelist.repr_entity(c));
                        else:
                            self.printer.boldnotice(dctools.filelist.repr_entity(c));
                    elif isinstance(c, dctools.filelist.Directory):
                        def find_tth_statistics(own_list, current, depth):
                            total_files = 0;
                            matching_tths = 0;
                            
                            #if depth > 2:
                            #    return 0, 0;
                            
                            if isinstance(current, dctools.filelist.File):
                                total_files += 1;
                                if self.own_list.tth.has_key(current.tth):
                                    matching_tths += 1;
                            elif isinstance(current, dctools.filelist.Directory):
                                for cc in current.children:
                                    total, matching = find_tth_statistics(own_list, cc, depth + 1);
                                    total_files += total;
                                    matching_tths += matching;
                            
                            return total_files, matching_tths;
                        
                        total, matching = find_tth_statistics(self.own_list, c, 0);
                        
                        if total == matching:
                            self.printer.notice(dctools.filelist.repr_entity(c));
                        elif matching == 0:
                            self.printer.boldnotice(dctools.filelist.repr_entity(c));
                        else:
                            self.printer.partialnotice(dctools.filelist.repr_entity(c));
                    else:
                        self.printer.notice(dctools.filelist.repr_entity(c));
            else:
                self.printer.error("not a directory:", dctools.filelist.build_path(r));
    
    def do_cd(self, text):
        if not self.open_list:
            self.printer.error("no open lists");
            return;
        
        n = dctools.filelist.findentity(self.open_list.root, self.current, text);
        
        if not n:
            self.printer.error("not a directory:", text);
            return;
        
        if len(n) > 1:
            self.printer.error("not a single match:", text);
            return;
        
        self.current = n[0];
    
    def do_info(self, text):
        if not self.open_list:
            self.printer.error("no open lists");
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
          self.printer.notice(str(e) + "");
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
        return map(lambda c: dctools.filelist.repr_entity(c), filter(lambda c: c.name.startswith(text), n))
        
        #if not self.open_list:
        #    return [];
        #print line, text;
        
    def help_ls(self):
        self.printer.notice("ls: list a directory");
    
    def help_cd(self):
        self.printer.notice("cd: change the current directory");
    
    def help_open(self):
        self.printer.notice("open: open a specific filelist");
