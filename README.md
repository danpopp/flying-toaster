# flying-toaster
![After Dark Flying Toasters](/logo.png)

## A firewall network egress surveying tool. ##
```
 _____ _       _            _____               _            
|  ___| |_   _(_)_ __   __ |_   _|__   __ _ ___| |_ ___ _ __ 
| |_  | | | | | | '_ \ / _` || |/ _ \ / _` / __| __/ _ \ '__|
|  _| | | |_| | | | | | (_| || | (_) | (_| \__ \ ||  __/ |   
|_|   |_|\__, |_|_| |_|\__, ||_|\___/ \__,_|___/\__\___|_|   
         |___/         |___/                                 
Test Type                     
DNS Exfiltration        count                         1
                        unique                        1
                        top       Connection Successful
                        freq                          1
Port Egress             count                     65535
                        unique                        2
                        top                        open
                        freq                      65528
SSH Connection on port  count                         5
                        unique                        1
                        top                  successful
                        freq                          5
Name: Result of Test, dtype: object
```

### Overview ###
Flying-Toaster will perform automated analysis of firewall egress restrictions at a target location. Run from a physical or virtual system it sequentially tests each port for connectivity, relying on an always-on AWS instance running simulated services, and a TCP-over-DNS tunnel server for testing advanced data exfiltration. A CSV file containing the test hostnames and ports is read by Flying-Toaster who attempts to initiate a TCP connection on that port, delivering the results to another CSV file. As a secondary test SSH connections are attempted over several non-standard ports. Finally a DNS tunnel is attempted. The results are appended to the port test results CSV, which can be rendered into any number of reports, tables, and charts. 

#### 1. Preliminary Assessment ####
Test outbound egress on all ports - can outbound connections be made without restriction?

#### 2. Secondary Assessment ####
Test outbound protocol inspection - can a standard SSH connection be made over non-standard ports?

#### 3. Tertiary Assessment ####
Test for advanced data-exfiltration - can an iodine tunnel be established over standard DNS traffic?

#### Setup Dependencies for SSH Testing ####
`sudo apt-get install libgssglue-dev`

`pip install paramiko` (may need to run as sudo)

`pip install pandas` (may need to run as sudo)

#### Run Script ####
`git clone git@gihub.com:danpopp/flying-toaster`

`cd flying-toaster`

`sudo python ./egress_test.py`

#### Example Input File / Common Ports ####
```
user@host:~/flying-toaster$ cat egress_list.csv
pwnlogs.com,22
pwnlogs.com,23
pwnlogs.com,53
pwnlogs.com,80
pwnlogs.com,123
pwnlogs.com,443
pwnlogs.com,1334
pwnlogs.com,8080
pwnlogs.com,8443
pwnlogs.com,5000
```
#### Example Output File / All Tests / Ports ####
```
pwnlogs.com,1,open
pwnlogs.com,2,open
...
pwnlogs.com,65534,open
pwnlogs.com,65535,open
SSH Connection on port,53,successful
SSH Connection on port,80,successful
SSH Connection on port,123,successful
SSH Connection on port,1,failed
SSH Connection on port,8080,successful
SSH Connection on port,1443,successful
DNS Exfiltration,esc.la,Connection Successful
```
### Workflow ###
#### Input ####
The script accepts a text file of comma-separated values with: `address,port`.
#### Execution ####
The script outputs a text file of comma-separated values returning: `address,port,[open || closed]`
In this case, we are testing all ports.
The script tests alternate-port SSH egress on TCP 53, 80, 123, 8080, 1443 and appends results.
The script tests TCP traffic over a covert DNS tunnel and appends the results. 
#### Output ####
The script summarizes the results and produces a detailed CSV with info on each port tested. An included HTML page can render it or the CSV can be made into a PDF on most linux machines by running `unoconv -f pdf egress_results.csv` A complete PDF report of all 65535 ports will be approx 1341 pages, but only consume about 2 MB.

### Infrastructure Requirements ###
This project utilizes a python honeypot script configured to emulate SSH, HTTP/HTTPS, Telnet, SMTP, SIP, an HTTP proxy, and default TCP/UDP connections on every port. Though this requires a dedicated machine and dedicated public IP address, the initial egress testing can be conducted using freely available public resources such as portquiz.net, for more advanced testing, you will need to configure and host infrastructure. 

#### 1. Egress Ports Assessment ####
If you don't have infrastructure and a dedicated IP address available, you can still run this test for default TCP/UDP connections using **portquiz.net** - it will similarlly respond on every port 1-65535. Currently we are hosting the infrastructrue for complete testing as described below at **pwnlogs.com**.

#### SSH Over Non-Standard Ports Assessment ####
A medium interaction honeypot https://github.com/fabio-d/honeypot hosted in it's own AWS VPC. It is configured to respond to the following SSH non-standard ports: 53, 80, 123, 8080, 1443. The DNS records for **pwnlogs.com** are directed to this server.

#### DNS Exfiltration Assessment ####
An iodined server https://github.com/yarrick/iodine and openSSH server is running on hosted private infrastructure. It is configured to allow DNS tunnels to be established and to allow an SSH tunnel to be established to the default gateway (10.13.37.1) over the DNS tunnel. The nameserver records for **ns.esc.la** point an iodined server. The iodine password is **DNS1DNS2DNS3**.

