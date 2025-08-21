#!/usr/bin/env python3
"""
DEMI Engine - Core multithreaded brute force engine
"""

import threading
import time
from queue import Queue, Empty

class DemiEngine:
    def __init__(self, module_class, target, users=None, passwords=None, pairs=None,
                 threads=4, stop_on_success=False, module_options=None):
        """
        Core engine for DEMI brute force attacks
        
        :param module_class: protocol module class (e.g. SSHModule, FTPModule)
        :param target: target IP or hostname
        :param users: list of usernames
        :param passwords: list of passwords
        :param pairs: list of (username, password) pairs
        :param threads: number of worker threads
        :param stop_on_success: stop after first valid credential
        :param module_options: dictionary of options to pass to module instances
        """
        self.module_class = module_class
        self.target = target
        self.users = users or []
        self.passwords = passwords or []
        self.pairs = pairs or []
        self.threads = threads
        self.stop_on_success = stop_on_success
        self.module_options = module_options or {}
        
        # Threading components
        self.queue = Queue()
        self.results = []
        self.lock = threading.Lock()
        self.stop_flag = threading.Event()
        
        # Statistics
        self.attempts = 0
        self.errors = 0

    def worker(self):
        """Worker thread function"""
        while not self.stop_flag.is_set():
            try:
                # Get credentials from queue with timeout
                user, passwd = self.queue.get(timeout=1)
            except Empty:
                # Queue is empty, exit worker
                break
            except Exception:
                continue

            try:
                # Create module instance with options
                module = self.module_class(**self.module_options)
                
                # Attempt login
                success = module.login(self.target, user, passwd)
                
                with self.lock:
                    self.attempts += 1
                    
                    if success:
                        print(f"[+] SUCCESS: {user}:{passwd}")
                        self.results.append((user, passwd))
                        
                        if self.stop_on_success:
                            print("[*] Stop-on-success enabled, stopping attack...")
                            self.stop_flag.set()
                            # Clear remaining queue items
                            try:
                                while not self.queue.empty():
                                    self.queue.get_nowait()
                                    self.queue.task_done()
                            except Empty:
                                pass
                    else:
                        print(f"[-] Failed: {user}:{passwd}")
                        
            except Exception as e:
                with self.lock:
                    self.errors += 1
                    print(f"[!] Error testing {user}:{passwd} -> {str(e)}")

            finally:
                # Mark task as done
                try:
                    self.queue.task_done()
                except:
                    pass

    def run(self):
        """Run the brute force attack"""
        start_time = time.time()
        
        # Populate the queue
        if self.pairs:
            # Use provided user:pass pairs
            for user, passwd in self.pairs:
                if not self.stop_flag.is_set():
                    self.queue.put((user, passwd))
        else:
            # Generate all combinations from separate lists
            for user in self.users:
                for passwd in self.passwords:
                    if not self.stop_flag.is_set():
                        self.queue.put((user, passwd))

        total_attempts = self.queue.qsize()
        print(f"[*] Queued {total_attempts} credential attempts")

        # Start worker threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)

        try:
            # Wait for all threads to complete
            for t in threads:
                t.join()
                
        except KeyboardInterrupt:
            print("\n[!] Received interrupt signal, stopping threads...")
            self.stop_flag.set()
            
            # Wait a bit for threads to stop gracefully
            for t in threads:
                t.join(timeout=2)

        # Calculate and display statistics
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n[*] Attack Statistics:")
        print(f"    Total attempts: {self.attempts}")
        print(f"    Successful: {len(self.results)}")
        print(f"    Errors: {self.errors}")
        print(f"    Duration: {duration:.2f} seconds")
        if self.attempts > 0:
            print(f"    Rate: {self.attempts/duration:.2f} attempts/second")

        return self.results
