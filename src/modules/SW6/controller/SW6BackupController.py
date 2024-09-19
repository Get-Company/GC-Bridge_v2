from ..controller.SW6AbstractController import SW6AbstractController
from config import SSHConfig, DBSW6Config
import paramiko
from datetime import datetime


class SW6BackupController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = None

        self.ssh_config = SSHConfig
        self.db_config = DBSW6Config

        super().__init__(
            sw6_entity=None,
            bridge_controller=None
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        pass

    def set_relations(self, bridge_entity, sw6_json_data):
        pass

    def execute_ssh_command(self, command):
        # SSH-Client initialisieren
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Verbindung herstellen
            client.connect(
                self.ssh_config.HOST,
                self.ssh_config.PORT,
                self.ssh_config.USERNAME,
                self.ssh_config.PASSWORD
            )

            # Befehl ausführen
            stdin, stdout, stderr = client.exec_command(command)

            # Ausgabe und Fehler drucken
            print("Standard Output:", stdout.read().decode())
            print("Standard Error:", stderr.read().decode())

        finally:
            # Verbindung schließen
            client.close()

    def backup_db(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        command = (f"cd webseiten/shopware && "
                   f"mysqldump "
                   f"-h localhost "
                   f"-u {self.db_config.USERNAME} "
                   f"-p{self.db_config.PASSWORD} "  # Yes there is no whitespace between -p and the password!!!
                   f"--no-tablespaces "
                   f"{self.db_config.DB_NAME} > backups/backup_DB_{self.db_config.DB_NAME}_{timestamp}.sql")

        return self.execute_ssh_command(command)

    def backup_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        command = (f"cd webseiten/shopware && "
                   f"zip -r backups/backup_FILES_{timestamp}.zip sw6dev")

        return self.execute_ssh_command(command)
