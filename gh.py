#!/usr/bin/python3

import sys
import subprocess
import os.path
import re
import urllib.parse
import webbrowser

gh_remote = r"(?:https:\/\/|git@)github\.com(?:\/|\:)([\w-]+)\/([\w-]+)(?:\.git)?"

debug = False

#################################
## Utils
#################################
def usage(string):
  # Print usage prefix
  print('Usage: gh', string)

# If you want the output in `stdout` then you will need to set print_output=False
def run(command, error=True, print_output=True):
  if not (isinstance(command, list)):
    command = command.split(' ')

  if (debug):
    print('[DEBUG] Running: \'' + ' '.join(command) + '\'')
  
  stdout = None if print_output else subprocess.PIPE
  stderr = None if print_output else subprocess.STDOUT

  try:
    return subprocess.run(command, errors=None, text=True, stdout=stdout, stderr=stderr)
  except Exception as e:
    if (error):
      print('[' + str(e.returncode) + '] ' + e.output)
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
    branch = output.stdout.replace('\n', '')
  else:
    branch = output.stdout.replace('\n', '')

  if (branch.startswith('refs/heads')):
    branch = branch.replace('refs/heads/', '')

  return branch

# Returns tuple: (user, repo)
def get_remote_info(remote):
  output = run('git remote get-url ' + remote, print_output=False)
  if (output.returncode != 0):
    return None

  matches = re.finditer(gh_remote, output.stdout)

  for matchNum, match in enumerate(matches, start=1):
    if (matchNum > 1):
      break
    elif (matchNum == 0):
      continue

    groups = match.groups()
    if (len(groups) != 2):
      print('Invalid remote URL? Could not find User/Repo')

    return groups

  return None

def new_pr(base_branch, branch, title):
  upstream = get_remote_info('upstream')
  origin = get_remote_info('origin')

  if (branch is None):
    return

  if (origin is None and upstream is None):
    print("No 'origin' or 'upstream' remote set!")
    return

  url = ''
  if (upstream is not None):
    # https://github.com/TheBusyBiscuit/Slimefun4/compare/master...WalshyDev:stable
    url = 'https://github.com/' + upstream[0] + '/' + upstream[1] + '/compare/' + base_branch + '...' + origin[0] + ':' + branch
  else:
    url = 'https://github.com/' + origin[0] + '/' + origin[1] + '/compare/'  + base_branch + '...' + branch

  url += '?' + urllib.parse.urlencode({'title': title})

  print(url)
  webbrowser.open(url)

def open_pr(remote, pr_id):
  pair = get_remote_info(remote)

  if (pair is None):
    print("No '" + remote + "' remote set!")
    return

  url = 'https://github.com/' + pair[0] + '/' + pair[1] + '/pull/' + pr_id

  print(url)
  webbrowser.open(url)

#################################
## Usage
#################################
# gh <branch(b)|commit(c)|diff|init(i)|open(o)|push|pull|pullrequest(pr)|unstage...>
def print_usage():
  args = sys.argv
  if (len(args) == 2):
    arg = args[1].lower()

    if (arg == 'branch' or arg == 'b'):
      usage(arg + ' <branch>')
    elif (arg == 'commit' or arg == 'c'):
      usage(arg + ' <message>')
    elif (arg == 'init' or arg == 'i'):
      usage(arg + ' [remote-url]')
    elif (arg == 'push'):
      usage(arg + ' [remote] [branch]')
    elif (arg == 'pull'):
      usage(arg + ' [remote] [branch]')
    elif (arg == 'pullrequest' or arg == 'pull-request' or arg == 'pr'):
      usage(arg + ' new/open <title/id>')
    elif (arg == 'open'):
      usage(arg + ' [remote]')
    elif (arg == 'unstage'):
      usage(arg)
  elif (len(args) == 3):
    first = args[1].lower()
    second = args[2].lower()

    if (first == 'pr' and second == 'new'):
      usage('pr new [base-branch] [branch] \'<title>\'')
    elif (first == 'pr' and second == 'open'):
      usage('pr open [remote] <id>')
  else:
    print('Usage: gh <command> [<args>]'
      + '\n\nCommands:'
      + '\n  branch  <branch>             - Switch to an existing or new branch'
      + "\n  commit  '<message>'          - Add files and commit"
      + '\n  diff                         - View current diff between HEAD and unstaged changes'
      + '\n  init    [remote-url]         - Initialise a git repo and add `origin` remote'
      + '\n  open    [remote]             - Open the current repo on GitHub'
      + '\n  push    [remote] [branch]    - Push to current or specific branch'
      + '\n  pull    [remote] [branch]    - Pull from current or specific branch'
      + '\n  pr      new/open <title/id>  - Open new or existing PR'
      + '\n  unstage [file]               - Unstage current changes'
    )

#################################
## Actions
#################################
def branch(args):
  if (len(args) == 0):
    print_usage()
    return

  branch = args[0]

  output = run('git checkout ' + branch, error=False, print_output=False)
  if (output.returncode != 0):
    run('git checkout -b ' + branch, error=False, print_output=False)
    print('Switched to new branch \'' + branch + '\'')
  else:
    print('Switched to branch \'' + branch + '\'')

def commit(args):
  message = ' '.join(args)
  if (args[0].lower() == '--skip'):
    message = '[CI Skip] ' + ' '.join(args[1:])

  run('git add .')
  run(['git', 'commit', '-m', message])

def diff(args):
  # OwO Diffity
  run('git diff')

def init(args):
  run('git init')

  if (len(args) > 0):
    run('git remote add origin ' + args[0])

def push(args):
  remote = 'origin'
  branch = current_branch()

  force_push = False
  for arg in args:
    if arg == '-f' or arg == '--force':
      force_push = True

  if (len(args) == 1 and args[0] != '-f' and args[0] != '--force'):
    branch = args[0]
  elif (len(args) == 2 and args[0] != '-f' and args[0] != '--force'):
    remote = args[0]
    branch = args[1]

  # Push to origin and current branch
  output = run('git push ' + remote + ' ' + branch + (' --force' if force_push == True else ''))
  if (output.returncode != 0):
    print('Could not push, did you commit anything?')

def pull(args):
  remote = 'origin'
  branch = current_branch()

  if (len(args) == 1):
    remote = args[0]
  elif (len(args) == 2):
    remote = args[0]
    branch = args[1]

  # Pull to origin and current branch
  output = run('git pull ' + remote + ' ' + branch)
  if (output.returncode != 0):
    print('Could not pull any new changes')

def pr(args):
  if (len(args) == 0 or len(args) == 1):
    print_usage()
    return

  if (args[0].lower() == 'new'):
    if (len(args) == 2):
      new_pr('master', current_branch(), args[1])
    elif (len(args) == 3):
      new_pr(args[1], current_branch(), args[2])
    elif (len(args) == 4):
      new_pr(args[1], args[2], args[3])
    else:
      print_usage()
  elif (args[0].lower() == 'open'):
    if (len(args) == 2):
      open_pr('origin', args[1])
    elif (len(args) == 3):
      open_pr(args[1], args[2])
    else:
      print_usage()

def open(args):
  remote = 'origin'
  if (len(args) == 1):
    remote = args[0]

  info = get_remote_info(remote)

  if (info is None):
    print('Invalid remote specified!')
    return

  url = 'https://github.com/' + info[0] + '/' + info[1]
  print(url)
  webbrowser.open(url)

def main():
  args = sys.argv

  global debug
  debug = args[0] == 'gh.py'

  if (len(args) == 1):
    print_usage()
  else:
    arg = args[1].lower()

    if (len(args) > 0 and arg != 'init' and arg != 'i' and arg != 'open' and arg != 'o' and not os.path.exists('.git')):
      print('You are not in a git directory!')
      return

    if (arg == 'branch' or arg == 'b'):
      branch(args[2:])
    elif (arg == 'commit' or arg == 'c'):
      commit(args[2:])
    elif (arg == 'diff'):
      diff(args[2:])
    elif (arg == 'init' or arg == 'i'):
      init(args[2:])
    elif (arg == 'push'):
      push(args[2:])
    elif (arg == 'pull'):
      pull(args[2:])
    elif (arg == 'pullrequest' or arg == 'pull-request' or arg == 'pr'):
      pr(args[2:])
    elif (arg == 'open' or arg == 'o'):
      open(args[2:])
    else:
      print_usage()

if __name__ == '__main__':
  main()