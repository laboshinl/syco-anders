#!/usr/bin/env python
'''
Install FreeRadius.

Read more
www.freeradius.org

'''

__author__ = "anders@televerket.net"
__copyright__ = "Copyright 2012, The System Console project"
__maintainer__ = "Daniel Lindh"
__email__ = "syco@cybercow.se"
__credits__ = ["???"]
__license__ = "???"
__version__ = "1.0.0"
__status__ = "Production"

import fileinput, shutil, os
import app
import general
from general import x
import version
import iptables
import config
from scopen import scOpen


# The version of this module, used to prevent
# the same script version to be executed more then
# once on the same host.
SCRIPT_VERSION = 1

def build_commands(commands):
  commands.add("install-radius",             install_freeradius, help="Install FreeRadius server on the current server.")
  commands.add("uninstall-radius",           uninstall_freeradius,           help="Uninstall Freeradius server on the current server.")

def install_freeradius(args):
  '''
  Install and configure the mysql-server on the local host.

  '''
  app.print_verbose("Install FreeRadius version: %d" % SCRIPT_VERSION)
  version_obj = version.Version("InstallFreeRadius", SCRIPT_VERSION)
  version_obj.check_executed()

 


  # Install the mysql-server packages.
  if (not os.access("/usr/sbin/radiusd", os.W_OK|os.X_OK)):
    x("yum -y install freeradius-mysql freeradius-utils")

    x("/sbin/chkconfig radiusd on ")
    if (not os.access("/usr/sbin/radiusd", os.F_OK)):
      raise Exception("Couldn't install FreeRadius")

  # Configure iptables
  iptables.add_freeradius_chain()
  iptables.save()
  app.print_verbose("Creating database")
  mysql_exec("CREATE DATABASE radius",True)
  x("cat /etc/raddb/sql/mysql/schema.sql | mysql -uroot -p%s radius" %(app.get_mysql_root_password()) )
 
  mysql_exec("INSERT INTO radius.radcheck VALUES('','test','SHA-Password',':=','e727d1464ae12436e899a726da5b2f11d8381b26')",True)
  mysql_exec("GRANT SELECT ON radius.* TO 'production'@'localhost'",True)
  mysql_exec("GRANT ALL on radius.radacct TO 'production'@'localhost'",True)
  mysql_exec("GRANT ALL on radius.radpostauth TO 'production'@'localhost'",True)
  
  app.print_verbose("Copying config")
  
  sqlconf = scOpen("/etc/raddb/sql.conf")
  sqlconf.replace("\"localhost\"",config.general.get_mysql_primary_master_ip())
  sqlconf.replace("\.*login =.*","    login=\"production\"" )
  sqlconf.replace("\"radpass\"","\"%s\"" % app.get_mysql_production_password())
  
  radbconf = scOpen("/etc/raddb/radiusd.conf")

  radbconf.replace(".*[#].*$INCLUDE sql.conf.*",     "         $INCLUDE sql.conf")
  
  sitesConf = scOpen("/etc/raddb/sites-enabled/default")
  sitesConf.replace("^[#].*sql$","      sql")
  version_obj.mark_executed()

def uninstall_freeradius(args):
  '''
  Uninstall freeradius

  '''
  if (os.access("/etc/init.d/radiusd", os.F_OK)):
    x("/etc/init.d/radiusd stop")
  x("yum -y remove freeradius")
  
  x("rm -rf /etc/raddb")

  mysql_exec('DROP database radius',True)

  version_obj = version.Version("InstallFreeRadius", SCRIPT_VERSION)
  version_obj.mark_uninstalled()



def mysql_exec(command, with_user=False, host="127.0.0.1"):
  '''
  Execute a MySQL query, through the command line mysql console.

  todo: Don't send password on command line.

  '''
  command = command.replace('\\', '\\\\')
  command = command.replace('"', r'\"')

  cmd="mysql "

  if (host):
    cmd+= "-h" + host + " "

  if (with_user):
    cmd+='-uroot -p"' + app.get_mysql_root_password() + '" '

  return x(cmd + '-e "' + command + '"')

