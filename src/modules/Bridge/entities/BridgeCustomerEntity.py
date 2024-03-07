from pprint import pprint

from src import db
from datetime import datetime

from .BridgeMarketplaceEntity import BridgeCustomerMarketplaceAssoc


class BridgeCustomerEntity(db.Model):
    __tablename__ = 'bridge_customer_entity'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.String(255), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    vat_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.now())

    # One-to-Many relation to addresses
    addresses = db.relationship(
        'BridgeCustomerAddressEntity',
        back_populates='customer',
        lazy=True,
        foreign_keys='[BridgeCustomerAddressEntity.customer_id]'
    )

    # One-to-One-Relations
    standard_shipping_address_id = db.Column(db.Integer, db.ForeignKey('bridge_customer_address_entity.id', use_alter=True, name='fk_shipping_address', ondelete="CASCADE"))
    standard_shipping_address = db.relationship(
        'BridgeCustomerAddressEntity',
        foreign_keys=[standard_shipping_address_id],
        uselist=False,
        back_populates="shipping_customer"
    )

    standard_billing_address_id = db.Column(db.Integer, db.ForeignKey('bridge_customer_address_entity.id', use_alter=True, name='fk_billing_address', ondelete="CASCADE"))
    standard_billing_address = db.relationship(
        'BridgeCustomerAddressEntity',
        foreign_keys=[standard_billing_address_id],
        uselist=False,
        back_populates="billing_customer"
    )

    # Many-to-Many relation to marketplaces
    marketplaces = db.relationship(
        'BridgeMarketplaceEntity',
        secondary='bridge_customer_marketplace_assoc',
        back_populates='customers',
        overlaps="customer,customer_assoc,marketplace"
    )

    marketplace_assoc = db.relationship(
        'BridgeCustomerMarketplaceAssoc',
        back_populates='customer',
        overlaps="marketplaces, customers"
    )

    orders = db.relationship("BridgeOrderEntity", back_populates="customer")

    # Getter and Setter
    def get_id(self):
        return self.id

    def get_erp_number(self):
        return self.erp_nr

    def set_erp_number(self, erp_nr):
        self.erp_nr = erp_nr

    def get_erp_nr(self):
        return self.erp_nr

    def set_erp_nr(self, erp_nr):
        self.erp_nr = erp_nr

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_vat_id(self):
        if self.vat_id:
            return self.vat_id
        else:
            return None

    def set_vat_id(self, vat_id):
        self.vat_id = vat_id

    def get_standard_shipping_address_id(self):
        return self.standard_shipping_address_id

    def set_standard_shipping_address_id(self, address_id):
        self.standard_shipping_address_id = address_id

    def get_standard_billing_address_id(self):
        return self.standard_billing_address_id

    def set_standard_billing_address_id(self, address_id):
        self.standard_billing_address_id = address_id

    def get_created_at(self):
        return self.created_at

    def get_updated_at(self):
        return self.updated_at

    def get_customer_marketplace_id(self, marketplace_id):
        customer_marketplace_assoc = (BridgeCustomerMarketplaceAssoc.query
                                   .filter(BridgeCustomerMarketplaceAssoc.marketplace_id == marketplace_id,
                                           BridgeCustomerMarketplaceAssoc.customer_id == self.get_id()
                                   ).one_or_none())
        if customer_marketplace_assoc:
            pprint(customer_marketplace_assoc.customer_marketplace_id)
            return customer_marketplace_assoc.customer_marketplace_id

    def update(self, bridge_entity_new):
        """
        Updates the current instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeCustomerEntity): The new instance with updated values.

        Returns:
            BridgeCustomerEntity: The updated instance if update was successful.
            bool: False if update failed.
        """
        try:
            self.set_erp_number(bridge_entity_new.get_erp_number())
            self.set_email(bridge_entity_new.get_email())
            self.set_vat_id(bridge_entity_new.get_vat_id())
            self.set_standard_shipping_address_id(bridge_entity_new.get_standard_shipping_address_id())
            self.set_standard_billing_address_id(bridge_entity_new.get_standard_billing_address_id())
            self.updated_at = datetime.now()

            return self

        except Exception as e:
            print(f"Error updating BridgeCustomerEntity: {e}")
            return False

    def to_dict(self):
        return {
            'id': self.id,
            'erp_nr': self.erp_nr,
            'email': self.email,
            'vat_id': self.vat_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'addresses': [address.to_dict() for address in self.addresses],
            'standard_shipping_address': self.standard_shipping_address.to_dict(),
            'standard_billing_address': self.standard_billing_address.to_dict()
        }

    def __repr__(self):
        return f"<BridgeCustomerEntity(id={self.id}, erp_nr='{self.erp_nr}', email='{self.email}', vat_id='{self.vat_id}', created_at='{self.created_at}', edited_at='{self.edited_at}')>"


class BridgeCustomerAddressEntity(db.Model):
    __tablename__ = 'bridge_customer_address_entity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    erp_combined_id = db.Column(db.String(255), nullable=True)   # Format: "AdresseID;AnschriftID;AnsprechpartnerID"
    erp_nr = db.Column(db.Integer, nullable=True)
    sw6_id = db.Column(db.String(255), nullable=True)
    erp_ans_nr = db.Column(db.Integer, nullable=True)
    erp_asp_nr = db.Column(db.Integer, nullable=True)
    name1 = db.Column(db.String(255), nullable=False)
    name2 = db.Column(db.String(255), nullable=False)
    name3 = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    street = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    land = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    edited_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    customer_id = db.Column(db.Integer, db.ForeignKey('bridge_customer_entity.id', ondelete='CASCADE'))
    customer = db.relationship('BridgeCustomerEntity', back_populates='addresses', foreign_keys=[customer_id])

    shipping_customer = db.relationship(
        'BridgeCustomerEntity',
        back_populates='standard_shipping_address',
        uselist=False,
        foreign_keys='[BridgeCustomerEntity.standard_shipping_address_id]'

    )

    billing_customer = db.relationship(
        'BridgeCustomerEntity',
        back_populates='standard_billing_address',
        uselist=False,
        foreign_keys='[BridgeCustomerEntity.standard_billing_address_id]'
    )

    # Getter and Setter for id
    def get_id(self):
        return self.id

    def set_id(self, id):
        pass
        try:
            if id is None or id < 0:
                raise ValueError("ID cannot be None or negative.")
            self.id = id
        except ValueError as e:
            print(f"Error setting id: {e}")

    # Getter and Setter for erp_combined_id
    def get_erp_combined_id(self):
        if self.erp_combined_id:
            return self.erp_combined_id
        else:
            return None

    def get_id_for_erp_adresse_from_combined_id(self):
        if self.erp_combined_id:
            return self.erp_combined_id.split(';')[0]
        else:
            return None

    def get_id_for_erp_anschrift_from_combined_id(self):
        if self.erp_combined_id:
            return self.erp_combined_id.split(';')[1]
        else:
            return None

    def get_id_for_erp_ansprechpartner_from_combined_id(self):
        if self.erp_combined_id:
            return self.erp_combined_id.split(';')[2]
        else:
            return None

    def set_erp_combined_id(self, erp_adresse_id, erp_anschrift_id, erp_ansprechpartner_id):
        try:
            if not all([erp_adresse_id, erp_anschrift_id, erp_ansprechpartner_id]):
                raise ValueError("All ERP IDs (Adresse, Anschrift, Ansprechpartner) must be provided.")
            self.erp_combined_id = f"{erp_adresse_id};{erp_anschrift_id};{erp_ansprechpartner_id}"
        except ValueError as e:
            print(f"Error setting erp_combined_id: {e}")

    # Getter and Setter for erp_nr
    def get_erp_nr(self):
        return self.erp_nr

    def set_erp_nr(self, erp_nr):
        try:
            if not erp_nr:
                raise ValueError("ERP number cannot be empty.")
            self.erp_nr = erp_nr
        except ValueError as e:
            print(f"Error setting erp_nr: {e}")

    # Getter and Setter for sw6_id
    def get_sw6_id(self):
        return self.sw6_id

    def set_sw6_id(self, sw6_id):
        try:
            if not sw6_id:
                raise ValueError("SW6 ID cannot be empty.")
            self.sw6_id = sw6_id
        except ValueError as e:
            print(f"Error setting sw6_id: {e}")

    # Getter and Setter for erp_ans_nr
    def get_erp_ans_nr(self):
        return self.erp_ans_nr

    def set_erp_ans_nr(self, erp_ans_nr:int):
        try:
            if erp_ans_nr is None:
                raise ValueError("ERP anschriften number cannot be empty.")
            self.erp_ans_nr = erp_ans_nr
        except ValueError as e:
            print(f"Error setting erp_ans_nr: {e}")

    # Getter and Setter for erp_asp_nr
    def get_erp_asp_nr(self):
        return self.erp_asp_nr

    def set_erp_asp_nr(self, erp_asp_nr):
        try:
            if erp_asp_nr is None:
                raise ValueError("ERP ansprechpartner number cannot be empty.")
            self.erp_asp_nr = erp_asp_nr
        except ValueError as e:
            print(f"Error setting erp_asp_nr: {e}")

    # Getter and Setter for name1
    def get_name1(self):
        return self.name1

    def set_name1(self, name1):
        try:
            if not name1:
                raise ValueError("Name1 cannot be empty.")
            self.name1 = name1
        except ValueError as e:
            print(f"Error setting name1: {e}")

    # Getter and Setter for name2
    def get_name2(self):
        return self.name2

    def set_name2(self, name2):
        self.name2 = name2  # No validation needed for nullable field

    # Getter and Setter for name3
    def get_name3(self):
        return self.name3

    def set_name3(self, name3):
        self.name3 = name3  # No validation needed for nullable field

    # Getter and Setter for department
    def get_department(self):
        return self.department

    def set_department(self, department):
        self.department = department  # No validation needed for nullable field

    # Getter and Setter for street
    def get_street(self):
        return self.street

    def set_street(self, street):
        try:
            if not street:
                raise ValueError("Street cannot be empty.")
            self.street = street
        except ValueError as e:
            print(f"Error setting street: {e}")

    # Getter and Setter for postal_code
    def get_postal_code(self):
        return self.postal_code

    def set_postal_code(self, postal_code):
        try:
            if not postal_code:
                raise ValueError("Postal code cannot be empty.")
            self.postal_code = postal_code
        except ValueError as e:
            print(f"Error setting postal_code: {e}")

    # Getter and Setter for city
    def get_city(self):
        return self.city

    def set_city(self, city):
        try:
            if not city:
                raise ValueError("City cannot be empty.")
            self.city = city
        except ValueError as e:
            print(f"Error setting city: {e}")

    # Getter and Setter for land
    def get_land(self):
        return self.land

    def set_land(self, land):
        try:
            if not land:
                raise ValueError("Land cannot be empty.")
            self.land = land
        except ValueError as e:
            print(f"Error setting land: {e}")

    # Getter and Setter for email
    def get_email(self):
        return self.email

    def set_email(self, email):
        try:
            if not email:
                raise ValueError("Email cannot be empty.")
            self.email = email
        except ValueError as e:
            print(f"Error setting email: {e}")

    # Getter and Setter for title
    def get_title(self):
        return self.title

    def set_title(self, title):
        try:
            if not title:
                raise ValueError("Title cannot be empty.")
            self.title = title
        except ValueError as e:
            print(f"Error setting title: {e}")

    # Getter and Setter for first_name
    def get_first_name(self):
        return self.first_name

    def set_first_name(self, first_name):
        try:
            if not first_name:
                raise ValueError("First name cannot be empty.")
            self.first_name = first_name
        except ValueError as e:
            print(f"Error setting first_name: {e}")

    # Getter and Setter for last_name
    def get_last_name(self):
        return self.last_name

    def set_last_name(self, last_name):
        try:
            if not last_name:
                raise ValueError("Last name cannot be empty.")
            self.last_name = last_name
        except ValueError as e:
            print(f"Error setting last_name: {e}")

    # Getter for created_at
    def get_created_at(self):
        return self.created_at

    # Getter for edited_at
    def get_edited_at(self):
        return self.edited_at

    def update(self, bridge_entity_new):
        """
        Updates the current BridgeCustomerAddressEntity instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeCustomerAddressEntity): The new BridgeCustomerAddressEntity instance with updated values.
        """
        # Update erp_combined_id
        # self.set_erp_combined_id(bridge_entity_new.get_erp_combined_id())

        # Update erp_nr
        # self.set_erp_nr(bridge_entity_new.get_erp_nr())

        # Update ans_nr
        # self.set_erp_ans_nr(bridge_entity_new.get_erp_ans_nr())

        # Update asp_nr
        # self.set_erp_asp_nr(bridge_entity_new.get_erp_asp_nr())

        # Update name1
        self.set_name1(bridge_entity_new.get_name1())

        # Update name2
        self.set_name2(bridge_entity_new.get_name2())

        # Update name3
        self.set_name3(bridge_entity_new.get_name3())

        # Update department
        self.set_department(bridge_entity_new.get_department())

        # Update street
        self.set_street(bridge_entity_new.get_street())

        # Update postal_code
        self.set_postal_code(bridge_entity_new.get_postal_code())

        # Update city
        self.set_city(bridge_entity_new.get_city())

        # Update land
        self.set_land(bridge_entity_new.get_land())

        # Update email
        self.set_email(bridge_entity_new.get_email())

        # Update title
        self.set_title(bridge_entity_new.get_title())

        # Update first_name
        self.set_first_name(bridge_entity_new.get_first_name())

        # Update last_name
        self.set_last_name(bridge_entity_new.get_last_name())

        # Update edited_at
        self.edited_at = datetime.now()

        return self

    def to_dict(self):
        return {
            'id': self.id,
            'erp_combined_id': self.erp_combined_id,
            'erp_nr': self.erp_nr,
            'sw6_id': self.sw6_id,
            'erp_ans_nr': self.erp_ans_nr,
            'erp_asp_nr': self.erp_asp_nr,
            'name1': self.name1,
            'name2': self.name2,
            'name3': self.name3,
            'department': self.department,
            'street': self.street,
            'postal_code': self.postal_code,
            'city': self.city,
            'land': self.land,
            'email': self.email,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None
        }

    def get_title_firstname_lastname(self):
        return f"{self.get_title()} {self.get_first_name()} {self.get_last_name()}"

    def __repr__(self):
        return (f"<BridgeCustomerAddressEntity(id={self.id}, erp_combined_id='{self.erp_combined_id}', "
                f"name1='{self.name1}', city='{self.city}', email='{self.email}', "
                f"created_at='{self.created_at}', edited_at='{self.edited_at}')>")

