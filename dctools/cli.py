import os;
import cmd;
import bz2;
import sys;

import dctools.filelist;
import musync.printer;

class CliPrinter(musync.printer.TermCaps):
    columns = 120;

    def warning(self, *text):
        self._writeall(self.c.red, self._joinstrings(text), self.c.sgr0, "\n");

    def error(self, *text):
        self._writeall(self.c.red, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");
    
    def notice(self, *text):
        self._writeall(self.c.blue, self._joinstrings(text), self.c.sgr0, "\n");
    
    def boldnotice(self, *text):
        self._writeall(self.c.magenta, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");

    def missingnotice(self, *text):
        self._writeall(self.c.red, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");
    
    def partialnotice(self, *text):
        self._writeall(self.c.yellow, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");
    
    def existingnotice(self, *text):
        self._writeall(self.c.green, self.c.bold, self._joinstrings(text), self.c.sgr0, "\n");
    
    def listall(self, color, text):
        w = 0;
        
        for t in text:
            if len(t) > w:
                w = len(t);
        
        w += 3;
        cols = int(self.columns / w);
        
        if cols == 0:
            for res in text:
                self._writeall(color, res, self.c.sgr0);
        else:
            colw = int(self.columns / cols);
            
            while len(text) > 0:
                for i in range(cols):
                    if len(text) <= 0:
                        break;

                    res = text.pop();
                    res += " "*(colw - len(res));
                    self._writeall(color, res, self.c.sgr0);
                
                self._writeall("\n");

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
            "columns": self.set_columns,
        };
        
        self.printer = CliPrinter(self.stdout);
        
        self.own_list = None;
        self.open_list = None;
        self.available_filelists = list();
        self.handles = dict();
        self.variables = dict();
        
        readline.set_completer_delims(' \t\n/');
		
        self.setup();
        self.load();

    def set_columns(self, val):
        try:
            self.printer.columns = int(val);
            if self.printer.columns < 10:
                self.printer.columns = 10;
            return str(self.printer.columns);
        except:
            self.printer.error("Bad columns value");
        
        return val;

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
        filelist = os.path.expanduser(val);
        
        if os.path.isfile(filelist):
            self.printer.notice("Loading my-list:", filelist);
            
            try:
                self.own_list = dctools.filelist.FileList(bz2.BZ2File(filelist, "r"));
            except OSError, e:
                self.printer.error("cannot open file list:", filelist);
        else:
            self.printer.warning("Not a file:", filelist);
        
        return filelist;

    def my_dcpp(self, val):
        dcpp = os.path.expanduser(val);
        dcpp_mylist = os.path.join(dcpp, "files.xml.bz2")
        dcpp_filelists = os.path.join(dcpp, "FileLists")
        
        if os.path.isfile(dcpp_mylist):
            self._set_variable("my-list", dcpp_mylist);

        if os.path.isdir(dcpp_filelists):
            self._set_variable("my-filelists", dcpp_filelists);
        
        return dcpp;
    
    def my_filelists(self, val):
        filelists = os.path.expanduser(val);
        
        if os.path.isdir(filelists):
            self.printer.notice("Loading FileLists from:", filelists);
            self.available_filelists = os.listdir(filelists);
        else:
            self.printer.warning("Not a directory:", filelists);
        
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
                self.printer.boldnotice(dctools.filelist.build_path(r) + ":");
                
                partial = list();
                missing = list();
                existing = list();
                
                for c in r.children:
                    if isinstance(c, dctools.filelist.File):
                        if self.own_list and self.own_list.tth.has_key(c.tth):
                            existing.append(dctools.filelist.repr_entity(c));
                        else:
                            missing.append(dctools.filelist.repr_entity(c));
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
                            existing.append(dctools.filelist.repr_entity(c));
                        elif matching == 0:
                            missing.append(dctools.filelist.repr_entity(c));
                        else:
                            partial.append(dctools.filelist.repr_entity(c));

                if len(missing) > 0:
                    self.printer.missingnotice("== Missing Files ==");
                    self.printer.listall(self.printer.c.red, missing);

                if len(partial) > 0:
                    self.printer.partialnotice("== Partial Files ==");
                    self.printer.listall(self.printer.c.yellow, partial);
                
                if len(existing) > 0:
                    self.printer.existingnotice("== Existing Files ==");
                    self.printer.listall(self.printer.c.green, existing);
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
        path = os.path.join(self.variables.get("my-filelists", ""), text);
        
        try:
          open_list = dctools.filelist.FileList(bz2.BZ2File(path, "r"));
        except Exception, e:
          self.printer.error("could not open filelist", str(e));
          return;
        
        if self.open_list:
            del self.open_list;

        self.open_list = open_list;
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
    
    def complete_open(self, text, line, begidx, endidx):
        return filter(lambda fl: fl.startswith(text), self.available_filelists);
    
    def help_ls(self):
        self.printer.notice("ls: list a directory");
    
    def help_cd(self):
        self.printer.notice("cd: change the current directory");
    
    def help_open(self):
        self.printer.notice("open: open a specific filelist");
