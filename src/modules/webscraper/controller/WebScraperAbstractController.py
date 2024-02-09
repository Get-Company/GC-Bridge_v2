from ..WebScraperCoreController import WebScraperCoreController


class WebScraperAbstractController(WebScraperCoreController):
    def __init__(self, file_name):
        self.file_name = file_name
        super().__init__(
            file_name=file_name
        )


