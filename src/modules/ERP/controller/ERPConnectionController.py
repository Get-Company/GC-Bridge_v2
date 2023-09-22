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
        # Example
        # self._erp.getSpecialObject(self._erp_special_objects["soAppObject"])
        self.special_objects_dict = {
            "soLager": 0,
            "soVorgang": 1,
            "soDokumente": 2,
            "soKontenAnalyse": 3,
            "soAppObject": 4,
            "soWandeln": 5,
            "soDoublette": 6,
            "soEvents": 7,
            "soNachricht": 8,
            "soVariablen": 9,
            "soDrucken": 10,
            "soBanking": 11,
            "soBuchungen": 12,
            "soEBilanz": 13,
            "soOffenePosten": 14,
            "soZahlungsverkehr": 15,
            "soAusgabeVerzeichnis": 16,
            "soTableDefinition": 17,
            "soAdrSpezPr": 18,
            "soModificationMonitor": 19,
            "soProjekte": 20
        }

        # Example
        # available_categories = str(erp_app.GetAppVar(self._erp_app_var["ArtikelKategorien"]))

        self.app_variablen_dict = {
            "ArtikelVerkaufspreise": 0,
            "ArtikelVarianten": 1,
            "ArtikelRabattsaetze": 2,
            "ArtikelBilder": 3,
            "ArtikelBezeichnungen": 4,
            "ArtikelKategorien": 5,
            "FreieArtikelKategorien": 6,
            "ArtikelGewicht": 7
        }


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
            message = f"ERP connects to:'{erp_config.MANDANT}' with user: '{erp_config.BENUTZER}'"
            self.logger.info(message)

    def ensure_connected(self):
        if self._erp is None:
            self.connect()

    def close(self):
        if self._erp is not None:
            self._erp.DeInit()
            self._erp = None
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
            self.logger.info(f"__del__ was called, but erp is already None. ERP: '{self._erp}'")
            return True
