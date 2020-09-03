#!/usr/bin/python3

import sys
import subprocess
import os.path

debug = True

def usage(string):
  print('Usage: gh', string)

def run(command, error=True, print_output=True):
  if not (isinstance(command, list)):
    command = command.split(' ')

  if (debug):
    print('[DEBUG] Running: \'' + ' '.join(command) + '\'')
  
  stdout = None if print_output else subprocess.PIPE
  stderr = None if print_output else subprocess.STDOUT

  try:
    return subprocess.run(command, errors=None, stdout=stdout, stderr=stderr)
  except Exception as e:
    if (error):
      print('[' + str(e.returncode) + '] ' + e.output.decode())
    return None

def current_branch():
  # git rev-parse --abbrev-ref HEAD
  output = run('git symbolic-ref --quiet HEAD', error=False, print_output=False)
  if (output is None):
    print('You are not inside a git repository.')
    return None

  branch = None

  if (output.returncode == 128):
    print('You are not inside a git repository.')
    return None
  elif (output.returncode != 0):
    output = run('git rev-parse --short HEAD', error=False, print_output=False)
    branch = output.stdout.decode().replace('\n', '')
  else:
    branch = output.stdout.decode().replace('\n', '')

  if (branch.startswith('refs/heads')):
    branch = branch.replace('refs/heads/', '')

  return branch

# gh <commit(c)|push|pull|pullrequest(pr)|open|unstage...>
def print_usage():
  args = sys.argv
  # gh <commit(c)|push|pull|pullrequest(pr)|open|unstage...>
  if (len(args) == 2):
    arg = args[1].lower()

    if (arg == 'commit' or arg == 'c'):
      usage(arg, '<message>')
    elif (arg == 'push'):
      usage(arg, '[remote] [branch]')
    elif (arg == 'pull'):
      usage(arg, '[remote] [branch]')
    elif (arg == 'pullrequest' or arg == 'pull-request' or arg == 'pr'):
      usage(arg, 'new/open <title/id>')
    elif (arg == 'open'):
      usage(arg, '[remote]')
    elif (arg == 'unstage'):
      usage(arg)
  elif (len(args) == 3):
    first = args[1].lower()
    second = args[2].lower()

    if (first == 'commit'):
      print('abc')
  else:
    print('Usage: gh <command> [<args>]'
      + '\n\nCommands:'
      + '\n  commit  <message>            - Add files and commit'
      + '\n  push    [remote] [branch]    - Push to current or specific branch'
      + '\n  pull    [remote] [branch]    - Pull from current or specific branch'
      + '\n  pr      new/open <title/id>  - Open new or existing PR'
      + '\n  open    [remote]             - Open the current repo on GitHub'
      + '\n  unstage [file]               - Unstage current changes'
    )

# For commit arg
def commit(args):
  message = ' '.join(args)
  if (args[0].lower() == '--skip'):
    message = '[CI Skip] ' + ' '.join(args[1:])

  run(['git', 'add', '.', '&&', 'git', 'commit', '-m', '"' + message + '"'])

def push(args):
  remote = 'origin'
  branch = current_branch()

  if (len(args) == 1):
    branch = args[0]
  elif (len(args) == 2):
    remote = args[0]
    branch = args[1]

  # Push to origin and current branch
  output = run('git push ' + remote + ' ' + branch)
  if (output.returncode != 0):
    print('Could not push, did you commit anything?')

def main():
  if not (os.path.exists('.git')):
    print('You are not in a git directory!')
    return

  args = sys.argv
  if (len(args) == 1):
    print_usage()
  else:
    arg = args[1].lower()

    if (arg == 'commit'):
      commit(args[2:])
    elif (arg == 'push'):
      push(args[2:])

if __name__ == '__main__':
  main()
