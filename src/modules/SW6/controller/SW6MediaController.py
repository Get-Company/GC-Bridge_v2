from pprint import pprint

import config
from ..controller.SW6AbstractController import SW6AbstractController
from ..entities.SW6MediaEntity import SW6MediaEntity
from src.modules.Bridge.controller.BridgeMediaController import BridgeMediaController


class SW6MediaController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = BridgeMediaController()

        super().__init__(
            sw6_entity=SW6MediaEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        """ No need to check if media entity exists in the db """
        pass

    def set_relations(self, bridge_entity, sw6_json_data):
        """ No need to set relations"""
        pass

    def downsert(self, bridge_entity):
        """ Nothing to donwser """

    def upsert_product_media(self, bridge_entity):
        """
        Function to either insert or update product media.
        If media is already in SW6 it skips that media item,
        otherwise, it attempts an upload of media to SW6.

        Args:
            bridge_entity(bridge_entity): Bridge entity containing media to be uploaded.
        """
        try:
            # Begin media upload process if `medias` attribute is populated in bridge_entity
            if bridge_entity.media_assocs:
                for media_assoc in bridge_entity.media_assocs:
                    media = media_assoc.media
                    try:
                        # If media already exists in SW6, skip it
                        if self.is_in_sw6(bridge_entity=media):
                            # print("Media already in SW6, continue")
                            continue
                        else:
                            sw6_json_data = {
                                "id": media.get_sw6_id(),  # Fetch SW6 id for the media
                                "mediaFolderId": config.SW6Config.MEDIA_FOLDERS["product"]
                            }
                            result = self.get_entity().bulk_uploads(sw6_json_data=sw6_json_data)
                            # Successful upload will call upload_media
                            if result['success']:
                                self.upload_media(bridge_media_entity=media)
                            else:
                                pprint(result)
                    except Exception as e:
                        # Log any errors encountered during individual media upload process
                        self.logger.error(
                            f'Error encountered while handling media upload process for media item {media}: {str(e)}')
                        continue

        except Exception as e:
            # Log any errors encountered during the overall media upload process
            self.logger.error(f'Error encountered during media upload process: {str(e)}')
            raise

    def upload_media(self, bridge_media_entity):
        """
        This function is used to upload media entity to a specific endpoint

        Parameters:
        bridge_media_entity: An instance of the media entity that will be used for the upload

        Returns:
        No return items for this function
        """
        try:
            # Prepare the query string parameters to be passed in the request
            query_string = {
                "extension": bridge_media_entity.get_file_type(),  # Fetch the file extension
                "fileName": bridge_media_entity.get_file_name()  # Fetch the file name
            }
            # Prepare the Payload for the request
            payload = {"url": bridge_media_entity.get_media_url()}

            # Perform a POST request to the specific endpoint for the upload
            self.get_entity().sw6_client.request_post(
                request_url=f"/_action/{self.get_entity().endpoint_name}/{bridge_media_entity.get_sw6_id()}/upload",
                additional_query_params=query_string,
                payload=payload
            )
        except Exception as e:
            # Log any errors that occur during the upload process
            self.logger.error(f'Error uploading media {str(e)}')

    def set_product_media_relation(self, bridge_entity):
        self.remove_product_media_relation(bridge_entity=bridge_entity)
        if bridge_entity.media_assocs:
            for index, media_assoc in enumerate(bridge_entity.media_assocs):
                payload = {
                    "productId": bridge_entity.get_sw6_id(),
                    "position": index,
                    "mediaId": media_assoc.media.get_sw6_id()
                }
                self.get_entity().sw6_client.request_post(f"/product-media/", payload=payload, additional_query_params={"_response":"detail"})
        else:
            print(f"No media for {bridge_entity}. Could not set relation")
            self.logger.error(f"No media for {bridge_entity}. Could not set relation")

    def remove_product_media_relation(self, bridge_entity):
        product_media_id_list = self.get_entity().search_api_ids_by_(index_field="productId",
                                                                     search_value=bridge_entity.get_sw6_id(),
                                                                     endpoint_name="product-media")
        if product_media_id_list["total"] >= 1:
            for id in product_media_id_list["data"]:
                result = self.get_entity().sw6_client.request_delete(f"/product-media/{id}")
                if 'errors' in result:
                    self.logger.error(result['errors'])
        return True


