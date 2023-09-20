
class Tests:
    def __init__(self, name=None):
        if name:
            self.name = name

    def erp_dataset_infos(self):
        from src.controller.ERP.ERPConnectionController import ERPConnectionController
        erp_obj = ERPConnectionController()
        erp_obj.connect()
        from src.controller.ERP.ERPDatasetController import ERPDatasetController
        erp_controller = ERPDatasetController(erp_obj=erp_obj, dataset_name=None)
        return erp_controller.get_list_datasets()

    def upsert_all_datasets_to_bridge(self):
        from src.controller.ERP.ERPDatasetsController import ERPDatasetsController
        from src.controller.ERP.ERPConnectionController import ERPConnectionController
        erp_obj = ERPConnectionController()
        erp_obj.connect()
        datasets_controller = ERPDatasetsController(erp_obj=erp_obj)
        upsert = datasets_controller.upsert_all_to_bridge()

    def indices(self):
        from src.controller.ERP.ERPDatasetController import ERPDatasetController
        from src.controller.ERP.ERPConnectionController import ERPConnectionController

        erp_obj = ERPConnectionController()
        erp_obj.connect()

        ArtikelI = ERPDatasetController(erp_obj=erp_obj)
        ArtikelI.get_list_indices_from_dataset("Adressen")
        erp_obj.close()

