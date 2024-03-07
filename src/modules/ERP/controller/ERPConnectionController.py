"""
This Object is for creating the connection to büro+ microtech. You can get all different Datasets
"""
from ..ERPCoreController import ERPCoreController
import win32com.client as win32
import pythoncom
import pywintypes
from config import ERPConfig


class ERPConnectionController(ERPCoreController):
    def __init__(self):
        super().__init__()

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ERPConnectionController, cls).__new__(cls)
            cls._instance._erp = None  # Initialisieren Sie das Attribut hier
        return cls._instance

    def connect(self):
        if self._erp is None:
            erp_config = ERPConfig()
            pythoncom.CoInitialize()
            self._erp = win32.dynamic.Dispatch("BpNT.Application")
            self._erp.Init(f'{erp_config.FIRMA}', "", f'{erp_config.BENUTZER}', '')
            self._erp.SelectMand(erp_config.MANDANT)
            message = f"ERP connects to:'{erp_config.MANDANT}' with user: '{erp_config.BENUTZER}'. "
            message += f"The Mandant State is:{self._erp.GetMandState()} | Process ID: {self._erp.GetSpecialObject(4).GetAppProcessId()}"
            self.logger.info(message)

    def ensure_connected(self):
        if self._erp is None:
            self.connect()

    def close(self):
        if self._erp is not None:
            self._erp.DeInit()
            self._erp = None
            pythoncom.CoInitialize()
            self.logger.info(f"Erp is set to None. ERP:'{self._erp}'")
            return True
        else:
            self.logger.info(f"Erp is already None. ERP: '{self._erp}'")
            return True

    def get_erp(self):
        self.ensure_connected()
        return self._erp

    def __del__(self):
        if self._erp is not None:
            self.close()
            self.logger.info(f"__del__ was called and forwarded to self.close() ERP: '{self._erp}'")
        else:
            self.close()
            self.logger.info(f"__del__ was called, but erp is already None. ERP: '{self._erp}'. Calling close to be sure!")

