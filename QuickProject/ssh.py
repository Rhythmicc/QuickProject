from . import *
import paramiko
SShConfig = requirePackage("paramiko.config", "SSHConfig", real_name='paramiko')
from paramiko import SSHClient

class ParamikoSSH:
    def __init__(self):
        self.config = SShConfig()
        with open(os.path.expanduser("~/.ssh/config")) as f:
            self.config.parse(f)
        if os.path.exists(os.path.expanduser("~/.ssh/id_rsa")):
            self.identity = os.path.expanduser("~/.ssh/id_rsa")
        else:
            self.identity = None
        self.activate_connections = {}
    
    def _parse_host(self, host: str, user: str = None, port: int = 22, identity: str = None):
        host_config = self.config.lookup(host)
        if not host_config and not user:
            raise Exception("Host not found in config file.")
        if host_config:
            host = host_config.get("hostname", host)
            identity = host_config.get("identityfile")
            if not user:
                user = host_config.get("user", None)
                if not user:
                    from QuickProject import QproErrorString
                    QproDefaultConsole.print(QproErrorString, "User not found in config file.")
        if not identity:
            identity = self.identity
        port = host_config.get("port", port)
        return host, user, port, identity
    
    def connect(self, host: str, user: str = None, port: int = 22, identity: str = None) -> SSHClient:
        conn_id = self._parse_host(host, user, port, identity)
        
        if conn_id in self.activate_connections:
            return self.activate_connections[conn_id]

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(*conn_id)
        self.activate_connections[conn_id] = ssh
        return ssh

    def close(self, host: str, user: str = None, port: int = 22, identity: str = None):
        conn_id = self._parse_host(host, user, port, identity)
        
        if conn_id in self.activate_connections:
            self.activate_connections[conn_id].close()
            del self.activate_connections[conn_id]

    def __del__(self):
        for k in self.activate_connections:
            self.activate_connections[k].close()
        self.activate_connections.clear()
