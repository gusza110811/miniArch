import tty, termios
import os, sys

tattr = termios.tcgetattr(sys.stdin.fileno()).copy()
tattro = termios.tcgetattr(sys.stdout.fileno()).copy()
if os.name != "posix":
    raise NotImplementedError("terminal magic does not work with non-posix system (yet)")

def disable_buffering():
    stdinfd = sys.stdin.fileno()

    tty.setcbreak(stdinfd, termios.TCSANOW)

def disable_lfcrlf():
    newattr = termios.tcgetattr(sys.stdout.fileno())
    newattr[1] &= ~termios.ONLCR
    termios.tcsetattr(sys.stdout, termios.TCSANOW, newattr)

def reset():
    global tattr
    global tattro
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, tattr)
    termios.tcsetattr(sys.stdout.fileno(), termios.TCSANOW, tattro)
