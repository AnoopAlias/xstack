#!/usr/bin/env python

import commoninclude
import cgitb
import subprocess
import cgi
import psutil
import os
import platform
import signal
import yaml


__author__ = "Anoop P Alias"
__copyright__ = "Copyright Anoop P Alias"
__license__ = "GPL"
__email__ = "anoopalias01@gmail.com"


installation_path = "/opt/nDeploy"  # Absolute Installation Path
backend_config_file = installation_path+"/conf/backends.yaml"
whm_terminal_log = installation_path+"/nDeploy_whm/term.log"
cluster_config_file = installation_path+"/conf/ndeploy_cluster.yaml"

cgitb.enable()
form = cgi.FieldStorage()

print('Content-Type: text/html')
print('')
print('<html>')
print('    <head>')
print('    </head>')
print('    <body>')

if form.getvalue('action'):
    if form.getvalue('action') == 'nginxreload':
        if os.path.isfile(cluster_config_file):

            procExe = subprocess.Popen('echo -e "Reloading NGINX cluster-wide..." > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('/usr/sbin/nginx -s reload && ansible -i /opt/nDeploy/conf/nDeploy-cluster/hosts ndeployslaves -m shell -a \"nginx -s reload\" >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Nginx reload initialized cluster-wide!')

        else:

            procExe = subprocess.Popen('echo -e "Reloading NGINX cluster-wide..." > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('/usr/sbin/nginx -s reload >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Nginx reload initialized!')

    elif form.getvalue('action') == 'watcherrestart':

        procExe = subprocess.Popen('echo -e "Reloading Watcher..." > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        procExe.wait()
        procExe = subprocess.Popen('service ndeploy_watcher stop && /bin/rm -f /opt/nDeploy/watcher.pid && service ndeploy_watcher start >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        procExe.wait()

        commoninclude.print_success('Watcher reload initialized!')

    elif form.getvalue('action') == 'redisflush':
        if os.path.isfile(cluster_config_file):

            procExe = subprocess.Popen('echo -e "Flushing Redis cache cluster-wide... > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('redis-cli FLUSHALL && ansible -i /opt/nDeploy/conf/nDeploy-cluster/hosts ndeployslaves -m shell -a \"redis-cli FLUSHALL\" >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Redis Cache flushed cluster-wide!')

        else:

            procExe = subprocess.Popen('echo -e "Flushing Redis cache cluster-wide... > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('redis-cli FLUSHALL >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Redis Cache flushed!')

    elif form.getvalue('action') == 'restart_backends':

        backend_data_yaml = open(backend_config_file, 'r')
        backend_data_yaml_parsed = yaml.safe_load(backend_data_yaml)
        backend_data_yaml.close()
        
        php_status_dict = {}
        if "PHP" in backend_data_yaml_parsed:
            php_backends_dict = backend_data_yaml_parsed["PHP"]
            for php,path in list(php_backends_dict.items()):
                for myprocess in psutil.process_iter():
                    # Workaround for Python 2.6
                    if platform.python_version().startswith('2.6'):
                        myexe = myprocess.exe
                    else:
                        myexe = myprocess.exe()
                    if path+"/usr/sbin/php-fpm" in myexe:
                        php_status_dict[php] = "ACTIVE"
                        break
                    else:
                        php_status_dict[php] = "NOT ACTIVE"
            
            for service,status in list(php_status_dict.items()):
                if status == "NOT ACTIVE":
                    commoninclude.print_warning(service+' was flagged as '+status+'.<br>')

        if os.path.isfile(cluster_config_file):

            procExe = subprocess.Popen('echo -e "Restarting application backends cluster-wide... > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('service ndeploy_backends restart && ansible -i /opt/nDeploy/conf/nDeploy-cluster/hosts ndeployslaves -m shell -a \"service ndeploy_backends restart\" >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Application Backends restarted cluster-wide!')

        else:

            procExe = subprocess.Popen('echo -e "Restarting application backends... > '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
            procExe = subprocess.Popen('service ndeploy_backends restart >> '+whm_terminal_log, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procExe.wait()
    
            commoninclude.print_success('Application Backends restarted!')

    else:
        commoninclude.print_forbidden()

else:
    commoninclude.print_forbidden()

print('    </body>')
print('</html>')
