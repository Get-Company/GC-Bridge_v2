from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgePriceEntity import BridgePriceEntity
from ..entities.BridgeMarketplaceEntity import (BridgeMarketplaceEntity,
                                                BridgeProductMarketplacePriceAssoc)
import math


class BridgePriceController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgePriceEntity()
        super().__init__(bridge_entity=self._bridge_entity)

    def upsert_price_for_all_marketplaces(self, bridge_price_entity, bridge_product_entity):
        """
        Upserts prices for all marketplaces linked to the given product. The method updates the existing price entity
        or inserts a new one, based on the marketplace factor.

        Args:
            bridge_price_entity (BridgePriceEntity): The price entity to be upserted.
            bridge_product_entity (BridgeProductEntity): The product entity for which prices are being set.
        """
        try:
            for marketplace in BridgeMarketplaceEntity.query.all():
                # Logic for each marketplace will be implemented here
                bridge_price_entity_new = BridgePriceEntity().update(bridge_price_entity)
                factor = marketplace.factor if marketplace.factor is not None else 1.0
                # Check if there is an existing association between the product and the marketplace
                try:
                    existing_association = BridgeProductMarketplacePriceAssoc.query.filter_by(
                        product_id=bridge_product_entity.id,
                        marketplace_id=marketplace.id
                    ).one_or_none()

                    if existing_association:
                        # self.logger.info(f"Updating price for product {bridge_product_entity.id} and marketplace {marketplace.id}")

                        if not existing_association.use_fixed_price:
                            # Calculate the price based on the marketplace factor
                            existing_association.price.price = self.calculate_price_by_factor(bridge_price_entity.price,factor)
                            existing_association.price.rebate_price = self.calculate_price_by_factor(bridge_price_entity.rebate_price, factor)
                            existing_association.price.special_price = self.calculate_price_by_factor(bridge_price_entity.special_price, factor)

                            self.db.session.flush()
                        else:
                            print(f"Using fixed price for product {bridge_product_entity.get_name()}")
                            # self.logger.info("Using fixed price, no update needed")

                    else:
                        # If no existing association is found, create a new one
                        try:
                            self.logger.info(f"Creating new association for product {bridge_product_entity.id} and marketplace {marketplace.id}")

                            # Determine the price based on the marketplace factor
                            bridge_price_entity_new.price = self.calculate_price_by_factor(bridge_price_entity.price,factor)
                            bridge_price_entity_new.rebate_price = self.calculate_price_by_factor(bridge_price_entity.rebate_price, factor)
                            bridge_price_entity_new.special_price = self.calculate_price_by_factor(bridge_price_entity.special_price, factor)

                            # Create a new price entity
                            self.db.session.add(bridge_price_entity_new)
                            self.db.session.flush()  # Flush to obtain new_price.id

                            # Create a new association with the new price
                            new_association = BridgeProductMarketplacePriceAssoc(
                                price_id=bridge_price_entity_new.id,
                                marketplace_id=marketplace.id,
                                product_id=bridge_product_entity.id,
                                use_fixed_price=False  # Default to using fixed price
                            )
                            self.db.session.add(new_association)
                            self.db.session.flush()  # Flush to save the new association
                            bridge_price_entity_new = None

                        except Exception as inner_e:
                            self.logger.error(f"An error occurred while creating a new association: {inner_e}")
                            # Continue to the next marketplace or handle differently

                except Exception as inner_e:
                    self.logger.error(f"An error occurred while checking for existing association: {inner_e}")
                    # You may choose to continue to the next marketplace or handle differently

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            self.db.session.rollback()

    def calculate_price_by_factor(self, price, factor):
        """
        Calculates the price by multiplying it with a given factor and then rounds it up to the nearest 5 cents.

        Args:
            price (float): The original price.
            factor (float): The factor by which the price will be multiplied.

        Returns:
            float: The calculated price, rounded up to the nearest 5 cents.
        """
        if not price:
            return None

        # Multiply the price with the factor
        calculated_price = price * factor

        # Round up to the nearest 5 cents
        rounded_price = math.ceil(calculated_price * 20) / 20

        return rounded_price
