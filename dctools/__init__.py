#
import sys;

import dctools.cli;

def main(argv):
    if len(argv) < 1:
        print "usage: dci <filelist>";
        return 1;
    
    term = dctools.cli.TerminalInterpreter(argv[0]);
    term.cmdloop();

def entrypoint():
  sys.exit(main(sys.argv[1:]));
