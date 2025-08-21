# demi/interface.py

import logging
from demi.engine import DemiEngine
from demi.modules import ssh, ftp, http_basic, http_form

MODULES = {
    "ssh": ssh.SSHModule,
    "ftp": ftp.FTPModule,
    "http-basic": http_basic.HTTPBasicModule,
    "http-form": http_form.HTTPFormModule,
}

class DEMIInterface:
    def __init__(self, config):
        self.config = config
        # Setup robust logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger("DEMI")
        self.engine = None

    def prepare_job(self):
        module_class = MODULES.get(self.config["module"])
        if not module_class:
            self.logger.error(f"Module {self.config['module']} not supported.")
            raise ValueError("Invalid module")
        # Initialize engine
        self.engine = DemiEngine(
            module_class=module_class,
            target=self.config["target"],
            users=self.config.get("users"),
            passwords=self.config.get("passwords"),
            pairs=self.config.get("pairs"),
            threads=self.config.get("threads", 4),
            stop_on_success=self.config.get("stop_on_success", False),
            module_options=self.config.get("module_options", {})
        )

    def run(self):
        self.logger.info(f"Starting attack: target={self.config['target']}, module={self.config['module']}")
        self.prepare_job()
        results = self.engine.run()
        self.logger.info(f"Attack Completed! Found {len(results)} valid credential(s).")
        for user, passwd in results:
            print(f" {user}:{passwd}")
        return results

    def load_wordlists(self, userlist, passlist, pairsfile):
        # Utility for robust file loading
        # ...Can use methods from demi/utils.py or extend error handling...
        pass

    def set_config(self, **kwargs):
        self.config.update(kwargs)
