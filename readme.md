# GC-Bridge: The Central Synchronization Hub 🌉

GC-Bridge isn't just another synchronization tool; it's the bridge that narrows the gap between your enterprise resource planning and your e-commerce. Enhanced by a responsive web UI, GC-Bridge provides an intuitive and seamless experience.

## Key Features ⭐

- **Modular Architecture 🧩:** Start by synchronizing between Büro+ and Shopware 6. Then expand your bridge to incorporate new modules such as Amazon, Otto-Office, and eBay.

- **Central Data Management 📊:** All your data is centrally managed and normalized in a database, ensuring consistency across all platforms.

- **Responsive Web UI 🌐:** Monitor and manage your data seamlessly with a user-friendly, responsive web interface.

- **Rule System & Rule-Builder 🔧:** A flexible and sophisticated rule system with an intuitive rule builder helps you fine-tune the intricacies of your data flows.

- **Automated Synchronization 🔄:** Ensure all your platforms are always up-to-date and reduce human errors.

- **Central Cronjob ⏲️:** An embedded cronjob manager for regular tasks and processes.

- **Logging System 📜:** Keep track of all operations, errors, and transactions with a comprehensive logging system.

- **Future-Proof 🚀:** Extend your bridge with new modules as you look to expand to new platforms.

## Why GC-Bridge? 🤔

In today's digital world, it's critical that your systems interact seamlessly. Manually updating data across various platforms can be time-consuming and prone to errors. GC-Bridge eliminates these pain points, ensuring consistency and efficiency in your business processes. Whether you're new to e-commerce or already present on multiple big marketplaces, GC-Bridge provides the tools and flexibility you need to succeed.

## Installation 💽

(Include instructions on installation and setup here.)

## Instructions

## Contributing 🤝

(Information on how other developers can contribute to the project.)

## License 📄

(Information about the project's licensing, e.g., MIT, GPL, etc.)

### DB Struktur:
Products:
Haben eine many-to-many-Beziehung zu Marketplaces, da verschiedene Produkte auf verschiedenen Marktplätzen existieren können.
Haben keine direkte Beziehung zu Prices. Die Preisbeziehung wird über Marketplaces definiert.
Sind direkt mit Orders verbunden, was einer many-to-one-Beziehung entspricht, da jede Bestellung mehrere Produkte enthalten kann.

Marketplaces:
Haben eine many-to-many-Beziehung zu Products.
Haben eine one-to-many-Beziehung zu Prices, da jeder Marktplatz verschiedene Preise für verschiedene Produkte haben kann. Jedes Produkt hat dabei nur einen Preis pro Marktplatz.
Haben eine one-to-many-Beziehung zu Customers, da ein Kunde auf verschiedenen Marktplätzen sein kann.
Haben eine one-to-many-Beziehung zu Orders, da ein Marktplatz mehrere Bestellungen haben kann.

Prices:
Haben eine many-to-one-Beziehung zu Marketplaces, da die Preise für Produkte über die Marktplätze definiert werden.
Jedes Produkt hat je Marktplatz einen eigenen Preis, was durch die Beziehung zwischen Marketplaces und Prices reflektiert wird.

Orders:
Haben eine many-to-one-Beziehung zu Customers, da jede Bestellung nur einem Kunden zugeordnet ist.
Haben eine many-to-one-Beziehung zu Marketplaces, da jede Bestellung direkt einem Marktplatz zugeordnet ist.
Haben eine many-to-many-Beziehung zu Products, da eine Bestellung mehrere Produkte enthalten kann.

Customers:
Haben eine many-to-many-Beziehung zu Marketplaces, da Kunden auf verschiedenen Marktplätzen sein können.
Haben eine one-to-many-Beziehung zu Orders, da ein Kunde mehrere Bestellungen haben kann.

