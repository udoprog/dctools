#
import sys;

from dctools.cli import TerminalInterpreter

def main(argv):
  term = TerminalInterpreter();
  term.cmdloop();

def entrypoint():
  sys.exit(main(sys.argv[1:]));
