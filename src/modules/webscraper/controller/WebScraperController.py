from pprint import pprint

import openpyxl

from .WebScraperAbstractController import WebScraperAbstractController


class WebScraperController(WebScraperAbstractController):
    def __init__(self, file_name):
        self.file_name = file_name
        self.wb = self.excel_create_or_load()
        super().__init__(
            file_name=file_name
        )

    def get_addresses_bestattungsvergleich_de(self):
        base_url = 'https://www.bestattungsvergleich.de/'
        html = self.fetch_page(base_url)
        soup = self.scraper(html, 'html.parser')
        states = {
            'Baden-Württemberg': 'verzeichnis/bestatter-in-baden-wuerttemberg',
            'Bayern': 'verzeichnis/bestatter-in-bayern',
            'Berlin': 'verzeichnis/bestatter-in-berlin',
            'Brandenburg': 'verzeichnis/bestatter-in-brandenburg',
            'Bremen': 'verzeichnis/bestatter-in-bremen',
            'Hamburg': 'verzeichnis/bestatter-in-hamburg',
            'Hessen': 'verzeichnis/bestatter-in-hessen',
            'Mecklenburg-Vorpommern': 'verzeichnis/bestatter-in-mecklenburg-vorpommern',
            'Niedersachsen': 'verzeichnis/bestatter-in-niedersachsen',
            'Nordrhein-Westfalen': 'verzeichnis/bestatter-in-nordrhein-westfalen',
            'Rheinland-Pfalz': 'verzeichnis/bestatter-in-rheinland-pfalz',
            'Saarland': 'verzeichnis/bestatter-in-saarland',
            'Sachsen': 'verzeichnis/bestatter-in-sachsen',
            'Sachsen-Anhalt': 'verzeichnis/bestatter-in-sachsen-anhalt',
            'Schleswig-Holstein': 'verzeichnis/bestatter-in-schleswig-holstein',
            'Thüringen': 'verzeichnis/bestatter-in-thueringen'
        }

        for state_name, state_url in states.items():
            print(f"Scraping state: " + state_name)

            # Erstellen eines neuen Sheets für jedes Bundesland
            state_sheet = self.wb.create_sheet(title=state_name)
            # Hinzufügen der Spaltenüberschriften
            state_sheet.append(["Name", "Straße", "PLZ", "Ort"])

            # Durchsuchen jeder Seite des Bundeslandes nach Adressen
            for page in range(1, 30):  # Beispiel: Seiten 1 bis 5
                page_url = f"https://www.bestattungsvergleich.de/{state_url}/seite/{page}"
                print("Scraping page: " + page_url)
                page_html = self.fetch_page(page_url)
                page_soup = self.scraper(page_html, 'html.parser')

                # Extrahieren der Adressdaten
                local_business_elements = page_soup.find_all(itemtype="http://schema.org/LocalBusiness")
                for element in local_business_elements:
                    name = element.find(itemprop="name").get_text(strip=True) if element.find(itemprop="name") else "Unbekannt"

                    address_element = element.find(itemtype="http://schema.org/PostalAddress")
                    if address_element:
                        street = address_element.find(itemprop="streetAddress").get_text(strip=True) if address_element.find(itemprop="streetAddress") else ""
                        postal_code = address_element.find(itemprop="postalCode").get_text(strip=True) if address_element.find(itemprop="postalCode") else ""
                        city = address_element.find(itemprop="addressLocality").get_text(strip=True) if address_element.find(itemprop="addressLocality") else ""

                        # Hinzufügen der Daten zum Excel-Sheet
                        state_sheet.append([name, street, postal_code, city])

        # Speichern des Excel-Workbooks
        self.excel_save_workbook()

    def get_addresses_evangelische_kirchen_bayern(self):
        """
        Diese Methode gibt alle Adressen evangelischer Kirchen in Bayern zurück.
        """
        dekanate_url = "https://landeskirche.bayern-evangelisch.de/service.php?o=dekanatmap&f=getDekanatMapData&r=json"
        dekanate_response = self.requests.get(dekanate_url)
        dekanate_response.raise_for_status()

        dekanate_list = [{
            "dekCode": dekanat_info["dekCode"],
            "elkbid": dekanat_info["elkbid"]
        } for dekanat_info in dekanate_response.json()["paths"].values()]

        kirchen_sheet = self.excel_add_sheet("Bayern")

        for dekanat in dekanate_list:
            gemeinde_url = f"https://landeskirche.bayern-evangelisch.de/service.php?o=dekanatmap&f=getDekanatInfo&dl=user&dekCode={dekanat['dekCode']}&elkbid={dekanat['elkbid']}&r=json"
            print(gemeinde_url)
            response = self.requests.get(gemeinde_url)
            response.raise_for_status()

            for gemeinde in response.json()["content"]["gemeinden"]:
                title = gemeinde.get('title')
                street = gemeinde.get('street')
                plz = gemeinde.get('pcode')
                city = gemeinde.get('locality')

                kirchen_sheet.append([title, street, plz, city])

        self.excel_save_workbook()
        return True

    def get_addresses_katholische_kirchen_munic(self):
        soup_links = self.parse_html("https://www.erzbistum-muenchen.de/pfarrei/linkliste-pfarreien/84000")
        link_elements = soup_links.find_all('a', class_="web")
        for link_element in link_elements:
            link = link_element.get('href')
            soup_pfarrei = self.parse_html(link)
            pfarrei_info_element = soup_pfarrei.find('h2', class_="orga-info")


