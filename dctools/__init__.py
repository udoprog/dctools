#
import sys;

import dctools.cli;

def main(argv):
    term = dctools.cli.TerminalInterpreter();
    term.cmdloop();

def entrypoint():
  sys.exit(main(sys.argv[1:]));
