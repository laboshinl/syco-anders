#! /usr/bin/env python

import general, app

# The version of this module, used to prevent
# the same script version to be executed more then
# once on the same host.
script_version = 1

def get_help():
  '''
  Return short help about this module.
  
  Used by main scritpt.
  '''
  command="git-commit"
  help="[comment] Commit changes to fosh to github"
  return command, help
  
def run(args):
  '''
  Commit the fosh folder to the github repository.
  
  '''
  comment=args[1]
  general.shell_exec("find " + app.fosh_path + " -iname '*.pyc' -delete")
  general.shell_exec("cd " + app.fosh_path + ";git add *")
  general.shell_exec("cd " + app.fosh_path + ";git commit -a -m'%s'" % comment)
  general.shell_exec("cd " + app.fosh_path + ";git push origin")