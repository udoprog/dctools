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
    prompt = "> ";
    config = "~/.dcirc";
    config_set = "=";
    comment_char = "#";
    
    def __init__(self):
        import readline;
        cmd.Cmd.__init__(self);
        
        self.pwd = [];
        self.triggers = {
            "my-list": self.my_list,
            "my-filelists": self.my_filelists,
            "my-dc++": self.my_dcpp,
        };
        
        self.printer = CliPrinter(self.stdout);
        
        self.own_list = None;
        self.open_list = None;
        self.handles = dict();
        self.variables = dict();
        
        readline.set_completer_delims(' \t\n/');
		
        self.setup();
        self.load();

    def setup(self):
        self.config = os.path.expanduser(self.config);
        self.do_refresh();

    def load(self):
        self.printer.notice("Opening own file list...");
        #self.own_list = dctools.filelist.FileList(bz2.BZ2File(filelist, "r"));
        
    def _read_config_line(self, line):
        line = line.strip();

        if len(line) <= 0:
            return;
        
        if line[0] == self.comment_char:
            return;

        i = line.find(self.config_set);
        
        if i <= 0:
            return;

        if len(line) < i + 1:
            return;
        
        key = line[:i].strip();
        val = line[i+1:].strip();
        
        self._set_variable(key, val);

    def _set_variable(self, key, val):
        if self.triggers.has_key(key):
            self.variables[key] = self.triggers[key](val);
        else:
            self.variables[key] = val;
    
    def my_list(self, val):
        val = os.path.expanduser(val);
        self.printer.notice("Loading my-list:", val);
        
        try:
            self.own_list = dctools.filelist.FileList(bz2.BZ2File(val, "r"));
        except OSError, e:
            self.printer.error("cannot open file list:", val);
        
        return val;

    def my_dcpp(self, val):
        dcpp = os.path.expanduser(val);
        dcpp_mylist = os.path.join(dcpp, "files.xml.bz2")
        
        if os.path.isfile(dcpp_mylist):
            self._set_variable("my-list", dcpp_mylist);
        
        return dcpp;
    
    def my_filelists(self, val):
        filelists = os.path.expanduser(val);
        return filelists;
    
    def do_refresh(self):
        if not os.path.isfile(self.config):
            self.printer.notice("creating:", self.config);
            try:
                open(self.config, "w").close();
            except OSError, e:
                self.printer.error("could not create configuration:", str(e));
                return;
        
        self.printer.notice("Refreshing configuration");
        
        try:
            cf = open(self.config, "r");
        except OSError, e:
            self.printer.error("could not open configuration:", str(e));
            return;
		
        for line in cf:
            self._read_config_line(line);
        
        cf.close();

    def do_save(self, text):
        try:
            cf = open(self.config, "w");
        except OSError, e:
            self.printer.error("could not open configuration:", str(e));
            return;
		
        for v in self.variables:
            cf.write(v + "=" + self.variables[v] + "\n");
        
        cf.close();

    def do_set(self, text):
        if text == "":
            for v in self.variables:
                self.printer.notice(v, "=", self.variables[v]);
        else:
            self._read_config_line(text);

    def do_ls(self, text):
        if not self.open_list:
            self.printer.error("no open lists");
            return;
        
        r = dctools.filelist.resolve(self.pwd, text)
        
        if r is None:
            self.printer.error("no such directory:", text);
            return;
        
        n = dctools.filelist.findone(self.open_list.root, r);
        
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
                        if self.own_list and self.own_list.tth.has_key(c.tth):
                            self.printer.notice(dctools.filelist.repr_entity(c));
                        else:
                            self.printer.boldnotice(dctools.filelist.repr_entity(c));
                    elif isinstance(c, dctools.filelist.Directory):
                        def find_tth_statistics(own_list, current, depth):
                            total_files = 0;
                            matching_tths = 0;
                            
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
                        
                        if not self.own_list:
                            total = 0;
                            matching = 0;
                        else:
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
        
        r = dctools.filelist.resolve(self.pwd, text)
        
        if r is None:
            self.printer.error("no such directory:", text);
            return;
        
        n = dctools.filelist.findone(self.open_list.root, r);
        
        if not n:
            self.printer.error("not a directory:", text);
            return;
        
        if len(n) > 1:
            self.printer.error("not a single match:", text);
            return;

        file = n[0];

        if not isinstance(file, dctools.filelist.Directory):
            self.printer.error("not a directory:", text);
            return;
        
        self.pwd = r;

    def do_pwd(self, text):
        self.printer.notice("/" + "/".join(self.pwd));
    
    def do_info(self, text):
        if not self.open_list:
            self.printer.error("no open lists");
            return;
        
        for n in dctools.filelist.findone(self.open_list.root, dctools.filelist.resolve(self.pwd, text)):
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

        self.pwd = [];
    
    def complete_ls(self, text, line, begidx, endidx):
        return self._complete_dir(text, line, begidx, endidx);

    def _complete_dir(self, text, line, begidx, endidx):
        import fnmatch;

        if not self.open_list:
            return [];

        rest = line.split(" ")[-1];
        
        if text == "":
            lookup = rest;
        else:
            lookup = rest[:-len(text)];
        
        r = dctools.filelist.resolve(self.pwd, lookup);
        
        if r is None:
            return [];
        
        n = dctools.filelist.find(self.open_list.root, r);
        
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
