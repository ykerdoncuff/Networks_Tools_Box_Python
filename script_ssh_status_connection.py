#!/usr/bin/python3
# Jimmy Taylor
# https://www.consentfactory.com/python-threading-queuing-netmiko/

# This method will spin up threads and process IP addresses in a queue

# Importing Netmiko modules
import time
from unittest import result
from netmiko import ConnectHandler


# Additional modules imported for getting password, pretty print
from getpass import getpass
from pprint import pprint
import signal,os

# Queuing and threading libraries
from queue import Queue
import threading

import pandas as pd


# These capture errors relating to hitting ctrl+C (I forget the source)
#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError: Broken pipe
#signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C


# Switch IP addresses from text file that has one IP per line
ip_adrrs_file = pd.read_csv('a4_list.csv')

ip_addrs = ip_adrrs_file['IP'].to_list()


# This sets up the queue
enclosure_queue = Queue()
# Set up thread lock so that only one thread prints at a time
print_lock = threading.Lock()

# CLI command being sent. This could be anywhere (and even be a passed paramenter) 
# but I put at the top for code readability
command = "show time"



# Function used in threads to connect to devices, passing in the thread # and queue
def deviceconnector(i,q):

    # This while loop runs indefinitely and grabs IP addresses from the queue and processes them
    # Loop will stop and restart if "ip = q.get()" is empty
    while True:
        output=""
        # These print statements are largely for the user indicating where the process is at
        # and aren't required
        print("{}: Waiting for IP address...".format(i))
        grab = q.get()
        ip=ip_adrrs_file['IP'][i]
        print("{}: Acquired IP: {}".format(i,ip))
        
        #device
        device_dict =  {
            'host': str(ip),
            'username': 'USER',
            'password': 'PASSWORD',
            'device_type': 'enterasys'
        }

        # Connect to the device, and print out auth or timeout errors
        try:
            net_connect = ConnectHandler(**device_dict,auth_timeout=420)
        
        except ConnectionRefusedError:
            with print_lock:
                print("\n{}: ERROR: Connection to {} Refused.\n".format(i,ip))
                output = "ERROR: Connection Refused"
                ip_adrrs_file.loc[i, 'SSH Status'] = output
            q.task_done()
            continue
        except TimeoutError:
            with print_lock:
                print("\n{}: ERROR: Connection to {} timed-out.\n".format(i,ip))
                output = "ERROR: Connection timed-out"
                ip_adrrs_file.loc[i, 'SSH Status'] = output
            q.task_done()
            continue
        except Exception:
            with print_lock:
                print("\n{}: ERROR: Authenticaftion failed for {}.\n".format(i,ip))
                output = "ERROR: Authenticaftion failed"
                ip_adrrs_file.loc[i, 'SSH Status'] = output
            q.task_done()
            continue
            
        # Capture the output, and use TextFSM (in this case) to parse data
        output = net_connect.send_command(command,use_textfsm=True)
        
        with print_lock:
            print("{}: Printing output from {}".format(i,ip))
            pprint(output)

        # Disconnect from device
        net_connect.disconnect
        ip_adrrs_file.loc[i, 'SSH Status'] = "OK"

        # Set the queue task as complete, thereby removing it from the queue indefinitely
        q.task_done()

# Mail function that compiles the thread launcher and manages the queue
def main():

    start = time.perf_counter()
    # Setting up threads based on number set above
    for i in range(len(ip_adrrs_file)):
        # Create the thread using 'deviceconnector' as the function, passing in
        # the thread number and queue object as parameters 
        thread = threading.Thread(target=deviceconnector, args=(i,enclosure_queue,))
        # Set the thread as a background daemon/job
        thread.setDaemon(True)
        # Start the thread
        thread.start()

    # For each ip address in "ip_addrs", add that IP address to the queue
    for ip_addr in ip_addrs:
        enclosure_queue.put(ip_addr)
    

    # Wait for all tasks in the queue to be marked as completed (task_done)
    enclosure_queue.join()
    while not enclosure_queue.empty():
        result = enclosure_queue.get()
        print(result) 
    finish = time.perf_counter()
    
    print("*** Script complete")
    #Sortie
    print(ip_adrrs_file)
    print("*** Export CSV ***")
    ip_adrrs_file.to_csv("export_ssh_status.csv")
    print("*** Export Done ***")
    print(f'Runtime: {round(finish-start,4)} seconds')

if __name__ == '__main__':
    
    # Calling the main function
    main()
