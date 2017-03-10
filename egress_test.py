#! /usr/bin/python

import telnetlib
import paramiko
import thread
import time
import os
import logging
import subprocess
import pandas

#additional paramiko logging (SSH debug info)
logger = paramiko.util.logging.getLogger()
logger.setLevel(logging.WARN)
paramiko.util.log_to_file('ssh_connect.log')

#time to wait between checking ports
portdelay = 0.01
#time to wait between checking SSH ports
sshdelay = 4
#alt SSH ports to test (must be configured on server side)
sshports = [53, 80, 123, 8080, 1443]

class EgressTester(object):

  thread_count = 0

  def __init__(self, input, log):

      for row in input:
          thread.start_new(self.testPort, (row[0], row[1], log))
          time.sleep(portdelay)
      while self.thread_count > 0:
          pass

      for sshport in sshports:
          thread.start_new(self.testSSH, (sshport, log))
          time.sleep(sshdelay)

  def testSSH(self, sshport, log):   
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      print 'Testing SSH on port %s' % (sshport)
      try:
          ssh.connect('pwnlogs.com', sshport, username='pwnie', password='pwnie')
          log.write('SSH Connection on port,%s,successful\n' % (sshport))
          log.flush()
          ssh.close()
      except paramiko.SSHException:
          pass
          log.write('SSH Connection on port,%s,failed\n' % (sshport))
          log.flush()
          ssh.close()
                
  def testPort(self, host, port, log):
      print 'Testing %s on port %s' % (host, port)
      try:
          connection = telnetlib.Telnet(host, port)
          log.write('Port Egress,%s,open\n' % (port))
          log.flush()
      except:
          log.write('Port Egress,%s,closed\n' % (port))
          log.flush()
      self.thread_count = self.thread_count - 1

def main():
  egress_list = parseCSV('egress_list.csv', ',')
  output = open('egress_results.csv', 'w')
  output.write("Test Type,Port Number / Nameserver,Result of Test\n")
  EgressTester(egress_list, output)
  
  #try to spin up a DNS tunnel (NOPASSWD: /usr/local/sbin/iodined in sudoers file)
  cmd = 'sudo iodine -PDNS1DNS2DNS3  ns.esc.la'
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)  
  p_wait = p.wait()
  print "DNS tunnel exit status/return code : ", p_wait
  killcmd = 'sudo killall -9 iodine'
  q = subprocess.Popen(killcmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)   
  if p_wait != 0:
      print "DNS tunnel failed!"
      with open("egress_results.csv", "a") as resultsfile:
          resultsfile.write("DNS Exfiltration,esc.la,Connection NOT Successful")
  else:
      print "DNS tunnel successful!"
      with open("egress_results.csv", "a") as resultsfile:
          resultsfile.write("DNS Exfiltration,esc.la,Connection Successful")
 
  data = pandas.read_csv('egress_results.csv')
  bytesttype = data.groupby('Test Type')
  results = bytesttype['Result of Test'].describe() 
  print " _____ _       _            _____               _            "
  print "|  ___| |_   _(_)_ __   __ |_   _|__   __ _ ___| |_ ___ _ __ "
  print "| |_  | | | | | | '_ \ / _` || |/ _ \ / _` / __| __/ _ \ '__|"
  print "|  _| | | |_| | | | | | (_| || | (_) | (_| \__ \ ||  __/ |   "
  print "|_|   |_|\__, |_|_| |_|\__, ||_|\___/ \__,_|___/\__\___|_|   "
  print "         |___/         |___/                                 "
  print(results)

def parseCSV(path, delimiter):
  text = open(path, 'r').read()
  text = text.replace('%s%s' % (delimiter, delimiter), '%s %s' % (delimiter, delimiter))
  lines = text.split('\n')
  rows = []
  for line in lines:
      if line != '':
          values = line.split(delimiter)
          rows.append(values)
  return rows

if __name__ == '__main__':
  main()


