import tty, termios
import os, sys

tattr = termios.tcgetattr(sys.stdin)
if os.name != "posix":
    raise NotImplementedError("terminal magic does not work with non-posix system (yet)")

def disable_buffering():
    tty.setcbreak(sys.stdin.fileno(), termios.TCSANOW)

def reset():
    global tattr
    termios.tcsetattr(sys.stdin, termios.TCSANOW, tattr)
