# !/usr/bin/env python3
import argparse
import sys
import threading
import os
import urllib3

print("""
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   █████████████████████████████████████▌▀▀████████████████████████████████████████
   █████████████████████████████████████╓█▓ ███████████████████████████████████████
   █████████████████████████████████▀└    ╙ ║█.└▀ ▄▄▀▀█████████████████████████████
   ████████████████████████████████       ▐▌╒∩ ▓████┌██████████████████████████████
   ████████████████████████████████         ╙ ∩ ▄#▓.╙██████████████████████████████
   █████████████████████████████████▄       `▀█████▓▄▀█████████████████████████████
   ████████████████████████████▀▌▄▄▄▄▄▄▄▄    ▄████████M████████████████████████████
   ██████████████████████████▓█████████╩▄▓▓`███▌▓▄▀███████▌████████████████████████
   ███████████████████████████████████.█████⌐██████▄╙██████████████████████████████
   ███████████████████████████████████▐██████▄███████▓▀████████████████████████████
   ███████████████████████████████████████████▓▀███████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   █████████████████████████ ▄ ▀█ ▄ ▀██  ██ █═(█ █ ║██▌ ▄ █████████████████████████
   ████████████████████████▌ ████ ▀─▐█∩▐ ██ ║  ▌(█ ║██▌ ▀ █████████████████████████
   ████████████████████████▌ █▀▀█ ▓⌐▐█ ▀─╘█b▐( ∩▐█ ║██▌(▓ █████████████████████████
   █████████████████████████▄╙¡██ █▄▐█ █▌ █▌ ▐▄ ██ └╙▐▌(█⌐▐████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   ████████████████████████████████████████████████████████████████████████████████
   """)


class Request(threading.Thread):
    def __init__(self, pid, locks, url, word):
        threading.Thread.__init__(self)
        self.pid = pid
        self.locks = locks
        self.word = word
        self.url = url + word
        self.request = self.makeRequest(url)


    def makeRequest(self, url):
        try:
            #Check for which thread is currently locked and waiting for another thread to release
            for locked in range(len(self.locks)):
                if (self.locks[locked].acquire is True):
                    print("thread: %s waiting for request thread: %s to finish" % (self.pid, locked))

            #Lock the current thread attempting to make the request
            self.locks[self.pid].acquire()
            #Create the connection Session
            self.connection = urllib3.PoolManager()
            #Perform the request - Could use head to be faster
            self.request = self.connection.request("GET", self.url)

            #Assign response data
            self.length = len(self.request.data)
            self.status = self.request.status
            self.headers = self.request.headers
            self.reason = self.request.reason

            #Print values of reponse
            self.compiled = "\t|\t%s\t\t\t|\t\t%s\t\t|\t\t%s\t\t|\t\t%s" % (self.word.strip(), self.status, self.length, self.reason)
            print(self.compiled)

            # Add Directories based on response code
            if self.status == 200:
                foundDirs.append(self.word)
            elif self.status == 301:
                redirectedDirs.append(self.word)
            elif self.status == 404:
                notFoundDirs.append(self.word)
            elif self.status == 401:
                notAllowedDirs.append(self.word)

            #release current thread on completion of response
            self.locks[self.pid].release()

        # Check for keyboardInterrupt, exits the program
        except KeyboardInterrupt:
            print("Finished: \n\n Found: %d \t Redirects: %d \t Disallowed: %d \t Not Found %d" % (len(foundDirs), len(redirectedDirs), len(notFoundDirs), len(notFoundDirs)))

            #Print out discoverd directories
            for dir in foundDirs,redirectedDirs,notAllowedDirs:
                print(dir)

            #Exit Application
            sys.exit(1)


#Create the argument handler using argparse
class ArgHandler():
    #initialise the constructor
    def __init__(self):
        #create the argument parser, add arguments
        self.parser = argparse.ArgumentParser(description='A basic concurrent web crawler',formatter_class=argparse.RawDescriptionHelpFormatter)
        self.parser.add_argument('--url', metavar='u', type=str, nargs='+', help='url to test - http://www.example.com')
        self.parser.add_argument('--wordlist', metavar='w', type=str, nargs='+', help='wordlist used to perform fuzz - C:/User/Documents/sqlinjections.txt')
        self.parser.add_argument('--threads', metavar='t', type=int, nargs='+', default=20, help='number of concurrent threads to use - default: 20')

        self.args = self.parser.parse_args()
        self.checkArgs(self.args)

    #Check the arguments passed, execute if length >=3
    def checkArgs(self, args):
        if (len(sys.argv) >= 3):
            #Check if wordlist is valid
            if (os.path.exists(self.args.wordlist[0])):
                return True
            else:
                print("Cannot Open File: %s" % (self.args.wordlist[0]))
        else:
            #print the usage of the program crawler.py -h
            self.parser.print_usage()
            print("Example: \n\n python3 crawlr.py --url 'http://example.com/' --wordlist 'D:/Downloads/wordlist.txt/' --threads 20")
            sys.exit(1)


def run():
    #Initalise global arrays, for easy access
    global foundDirs, notFoundDirs, redirectedDirs, notAllowedDirs

    #Initialise the argument handler
    handler = ArgHandler()

    #Get the passed arguments
    threadCount = handler.args.threads[0]
    url = handler.args.url[0]
    wordlistPath = handler.args.wordlist[0]

    #Inititialise the wordlist file#
    wordlist = open(wordlistPath, 'r').readlines()

    #Index of current word
    pos = 0

    #Initialise arrays
    threads = []
    locks = []
    foundDirs = []
    notFoundDirs = []
    redirectedDirs = []
    notAllowedDirs = []

    #Create the threads
    for i in range(threadCount):
        locks.append(threading.Lock())

    #Start all the threads
    for requests in threads:
        requests.start()


    #Join the threads
    for requests in threads:
        requests.join()

    #Print the top row
    print("=" * 75 + "\n\t|\tWord\t\tRequest Code\t|\tLength\t|\tReason\n")

    #Check if the whole wordlist has been processed
    while (pos is not len(wordlist)):
        for pid in range(threadCount):
            #Change the word index
            pos += 1
            #Create the Request thread
            thread = Request(pid, locks, url, wordlist[pos])
            #enable daemon
            thread.deamon = True
            #append threads to thread array
            threads.append(thread)

#Run the main function
if __name__ == '__main__':
    run()

"""
References
    ----------

    docs.python.org. 2021. argparse — Parser for command-line options, arguments and sub-commands — Python 3.9.4 documentation. [online] Available at: <https://docs.python.org/3/library/argparse.html> [Accessed 5 April 2021].
    docs.python.org. (n.d.). threading — Thread-based parallelism — Python 3.9.0 documentation. [online] Available at: https://docs.python.org/3/library/threading.html.

"""
