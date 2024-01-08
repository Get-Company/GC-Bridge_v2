"""
These examples are considered that
Examples:
    Print the Bez1 from the Artikle 900000:
    erp_art = ERPArtikelEntity(search_value="900000")
    print(erp_art.get_("Bez1"))

    Print the 900000 Umsatz from März 2023:
    erp_art = ERPArtikelEntity(search_value="900000")
    print(erp_art.get_nested_ums(2023,

    Set Rembremerting in Na2 of first address [0] in customer [10026] for Anschriften Entity
    erp_ans = ERPAnschriftenEntity(search_value=[10026,0])
    erp_ans.start_transaction()
    erp_ans.set_("Na2", "Rembremerting")
    erp_ans.commit()

"""
from datetime import datetime
from typing import List, Union, Tuple, Any, Dict
# Is used to get the basename of the image
import os
from abc import abstractmethod
import requests

from ..ERPCoreController import ERPCoreController
from ..controller.ERPConnectionController import ERPConnectionController
from config import GCBridgeConfig
from ...Bridge.entities.BridgeMediaEntity import BridgeMediaEntity


class ERPAbstractEntity(ERPCoreController):
    """
    Abstract class for interacting with ERP datasets.

    Attributes:
        erp: Singleton instance of ERPConnectionController.
        dataset_name: Name of the dataset within the ERP system.
        index_field: Name of the field used for indexing the dataset.
        dataset_infos: Information about all datasets in the ERP system.
        created_dataset: Cached created dataset object.
    """

    def __init__(self,
                 dataset_name,
                 dataset_index,
                 search_value=None,
                 range_end=None,
                 filter_expression=None):
        """
        Initialize the ERPAbstractEntity.

        Parameters:
            dataset_name (str): Name of the dataset.
            dataset_index (str): Name of the field used for indexing.
            search_value (str, optional): Value to search within the dataset. Defaults to None.
            range_end (str, optional): Defines the end of a range for dataset queries. Defaults to None.
        """
        super().__init__()

        try:
            #1 Get the singleton instance of ERPConnectionController
            erp_co_ctrl = ERPConnectionController()

            self._erp = erp_co_ctrl.get_erp()
            self._erp_special_objects = erp_co_ctrl.special_objects_dict
            self._erp_app_var = erp_co_ctrl.app_variablen_dict

            #2 Fetch information about all datasets
            self._dataset_infos = None
            self.set_dataset_infos()

            #3 Set DatasetName
            self._dataset_name = None
            self.set_dataset_name(dataset_name=dataset_name)

            #4 Initialize created dataset
            self._created_dataset = None
            self.set_created_dataset()

            #5 Set the Index of the Dataset
            self._dataset_index = None
            self.set_dataset_index(dataset_index=dataset_index)

            # Set the filter
            if filter_expression:
                self.set_filter(filter_expression=filter_expression)


            # initialize Search Value as Empty:
            self._search_value = None
            # When the cursor is set, this attributes changes to True
            self._found = None
            if search_value:
                self.logger.info(f"Search Value provided: {search_value}. Call self.set_search_value.")
                self.set_search_value(search_value=search_value)
                self.logger.info(f"Search Value is set. Call self.set_cursor.")

            # Set range if range_end
            self._range_end = None
            self._is_ranged = False
            self._range_count = None
            if range_end:
                self.set_range_end(range_end=range_end)
                # Set the range on the dataset
                self.range_set()
                self.set_is_ranged()
                self.set_range_count()
            # If we do not have a range, set the cursor
            else:
                self.set_cursor()

            # Initialize nested dataset as none until it is set
            self._nested_dataset = None

            # Field Types and how to read them:
            self.field_types_to_read = {
                'WideString': 'AsString',
                'Float': 'AsFloat',
                'Blob': 'Text',
                'Date': 'AsDatetime',
                'DateTime': 'AsDatetime',
                'Integer': 'AsInteger',
                'Boolean': 'AsInteger',  # AsBoolean: True/False | AsInteger: 1/0
                'Byte': 'AsInteger',
                'Info': 'Text',
                'String': 'AsString',
                'Double': 'AsString',
                'AutoInc': 'AsInteger'
            }
            # Field types and how to write them
            self.field_types_to_write = {
                'WideString': 'AsString',
                'Float': 'AsFloat',
                'Blob': 'Text',
                'Date': 'AsString',
                'DateTime': 'AsString',
                'Integer': 'AsInteger',
                'Boolean': 'AsInteger',  # AsBoolean: True/False | AsInteger: 1/0
                'Byte': 'AsInteger',
                'Info': 'Text',
                'String': 'AsString',
                'Double': 'AsString'
            }

            # Holds the current state of the dataset:
            self._dataset_state = None
            self.set_dataset_state()

            # Holds the fields of the dataset. Is called in different functions
            # by the self.get_dataset_fields
            self._dataset_fields = None

            self.logger.info("%s initialized successfully for dataset: %s", self.__class__.__name__, dataset_name)

        except Exception as e:
            self.logger.error("Error initializing %s for dataset: %s. Error: %s", self.__class__.__name__, dataset_name, str(e))
            raise e

    def set_dataset_infos(self) -> None:
        """
        Set the dataset information for the entity.
        """
        try:
            dataset_infos = self._erp.DatasetInfos
            if dataset_infos:
                self._dataset_infos = dataset_infos
                self.logger.info(f"Dataset information is set.")
            else:
                raise ValueError("Unable to fetch dataset information from ERP.")
        except ValueError as e:
            self.logger.error(f"Error setting dataset information: {str(e)}")
            raise

    def get_dataset_infos(self):
        """
        Retrieve the dataset information of the entity.

        Returns:
            Dataset information.

        Raises:
            ValueError: If dataset information is not set.
        """
        if self._dataset_infos:
            return self._dataset_infos
        else:
            message = "Dataset information is not set"
            self.logger.warning(message)
            raise ValueError(message)

    def set_dataset_name(self, dataset_name: str) -> None:
        """
        Set the dataset name for the entity.

        Parameters:
            dataset_name (str): The name of the dataset.
        """
        try:
            if dataset_name:
                self._dataset_name = dataset_name
                self.logger.info(f"Dataset Name is set to: '{dataset_name}'")
            else:
                raise ValueError("Provided dataset name is None or empty.")
        except ValueError as e:
            self.logger.error(f"Error setting dataset name: {str(e)}")
            raise

    def get_dataset_name(self) -> str:
        """
        Retrieve the dataset name of the entity.

        Returns:
            str: The name of the dataset.

        Raises:
            ValueError: If dataset name is not set.
        """
        if self._dataset_name:
            return self._dataset_name
        else:
            message = "Dataset Name is not set"
            self.logger.warning(message)
            raise ValueError(message)

    def set_dataset_index(self, dataset_index: str) -> None:
        """
        Set the dataset index for the entity.

        Parameters:
            dataset_index (str): The index of the dataset.
        """
        try:
            if dataset_index:
                self._dataset_index = dataset_index
                self.logger.info(f"Dataset Index is set to: '{dataset_index}'")
            else:
                raise ValueError("Provided dataset index is None or empty.")
        except ValueError as e:
            self.logger.error(f"Error setting dataset index: {str(e)}")
            raise

    def get_dataset_index(self) -> str:
        """
        Retrieve the dataset index of the entity.

        Returns:
            str: The index of the dataset.

        Raises:
            ValueError: If dataset index is not set.
        """
        if self._dataset_index:
            return self._dataset_index
        else:
            message = "Dataset Index is not set"
            self.logger.warning(message)
            raise ValueError(message)

    def set_created_dataset(self) -> None:
        """
        Create and set the dataset using the dataset name.
        """
        try:
            if self.get_dataset_name():
                self._created_dataset = self._dataset_infos.Item(self.get_dataset_name()).CreateDataSet()
                self.logger.info(f"Set {self.get_dataset_name()} as created dataset")
            else:
                raise ValueError("Dataset name is not set. Cannot create dataset.")
        except Exception as e:
            self.logger.error(f"Error creating dataset for {self.get_dataset_name()}: {str(e)}")
            raise

    def get_created_dataset(self) -> object: # You can replace 'Any' with the specific type of the dataset if known.
        """
        Retrieve the created dataset.

        Returns:
            Created dataset if available.

        Raises:
            ValueError: If dataset is not created and cannot be created.
        """
        if self._created_dataset:
            return self._created_dataset
        else:
            self.set_created_dataset()
            if self._created_dataset:
                return self._created_dataset
            else:
                message = "Failed to create dataset"
                self.logger.error(message)
                raise ValueError(message)

    def set_search_value(self, search_value: Union[str, int, List[str], List[int]]) -> None:
        """
        Set the search value for querying the dataset.

        Parameters:
            search_value: The value or list of values to be used for searching the dataset.
        """
        try:
            self._search_value = search_value
            self.logger.info(f"Search Value is set to: {search_value}")
        except Exception as e:
            self.logger.error(f"Error setting search value: {str(e)}")
            raise

    def get_search_value(self) -> Union[str, int, List[str], List[int], None]:
        """
        Retrieve the set search value.

        Returns:
            The search value if available, otherwise None.
        """
        if self._search_value:
            return self._search_value
        else:
            self.logger.warning("Search Value is not set")
            return None

    def set_range_end(self, range_end: Union[str, int, List[str], List[int]]) -> None:
        """
        Set the ending value for the range of the dataset.

        Parameters:
            range_end: The ending value or list of values for the range.

        Returns:
            None
        """
        self.logger.info(f"Range End is set to: {range_end}")
        self._range_end = range_end

    def get_range_end(self) -> Union[str, int, List[str], List[int], bool]:
        """
        Get the ending value for the range of the dataset.

        Returns:
            The ending value for the range if set, else returns False.
        """
        if self._range_end:
            return self._range_end
        else:
            self.logger.warning("Range End is not set")
            return False

    def set_is_ranged(self):
        """
        Set the state indicating if the dataset is ranged or not.

        Parameters:
            is_ranged: Boolean value indicating if the dataset is ranged.

        Returns:
            None
        """
        ranged = self._created_dataset.IsRanged()
        count = self._created_dataset.RecordCount
        if ranged and count > 0:
            self.logger.info(f"Is Dataset ranged: {ranged}")
            self._is_ranged = ranged
        else:
            self.logger.warning(f"Ranged: {ranged} and Count: {count}. Dataset is not really ranged!")
            self._is_ranged = False

    def get_is_ranged(self) -> bool:
        """
        Get the state indicating if the dataset is ranged or not.

        Returns:
            True if the dataset is ranged, False otherwise.
        """
        if self._is_ranged is not None:  # Considering it's a boolean
            return self._is_ranged
        else:
            self.logger.warning("is_ranged has not been set")
            return False

    def set_range_count(self) -> None:
        """
        Set the range count for the dataset.

        Returns:
            None
        """
        if self._is_ranged:
            range_count = self._created_dataset.RecordCount
            self.logger.info(f"Dataset range count. {range_count}")
            self._range_count = range_count
        else:
            self.logger.warning("Dataset range count called, but dataset is not ranged!")

    def get_range_count(self) -> Union[int, bool]:
        """
        Get the range count of the dataset.

        Returns:
            Integer value representing the range count if set, False otherwise.
        """
        if not self._range_count:
            self.logger.warning("Range Count is not set")
            self.set_range_count()

        return self._range_count

    def set_filter(self, filter_expression: str):
        if filter_expression:
            self._created_dataset.Filter = filter_expression
            self._created_dataset.Filtered = True
            self.logger.info(f"Filter expression: {filter_expression}")
        else:
            return True

    def set_dataset_state(self, state: Union[int, None] = None) -> None:
        """
        Set the state for the dataset.

        Parameters:
            state: The state value to be set for the dataset. If not provided,
                   the state will be set to the current state of the created dataset.
        """
        try:
            if state is not None:
                self._dataset_state = state
            else:
                self._dataset_state = self._created_dataset.State
            self.logger.info(f"Dataset state is set to: {self._dataset_state}")
        except Exception as e:
            self.logger.error(f"Error setting dataset state: {str(e)}. ERP Dataset state: {self._created_dataset.State}")
            raise

    def get_dataset_state(self) -> int:
        """
        Retrieve the state of the dataset.

        The available states of the datasets are:
            dsInactive = 0,
            dsBrowse = 1,
            dsEdit = 2,
            dsInsert = 3,
            dsSetKey = 4,
            dsCalcFields = 5,
            dsFilter = 6,
            dsNewValue = 7,
            dsOldValue = 8,
            dsCurValue = 9,
            dsBlockRead = 10,
            dsInternalCalc = 11

        Returns:
            The state of the dataset.
        """
        if self._dataset_state is None:
            self.logger.warning("Dataset state is not set. Initializing it now.")
            self.set_dataset_state()
        return self._dataset_state

    def set_dataset_fields(self) -> bool:
        """
        Set the dataset fields to self._dataset_fields by fetching them from the dataset.

        Returns:
            bool: True if the operation was successful, otherwise False.

        Example:
            success = obj.set_dataset_fields()
            # Possible output: True or False
        """
        try:
            dataset = self.get_created_dataset()
            if dataset:
                self._dataset_fields = [{'Name': field.Name, 'Info': field.Info} for field in dataset.Fields]
                self.logger.info("Successfully set dataset fields.")
                return True
            else:
                self.logger.warning("Failed to fetch the dataset or dataset contains no fields.")
                return False
        except Exception as e:
            self.logger.error(f"An error occurred while setting dataset fields: {str(e)}")
            return False

    def get_dataset_fields(self) -> List[Dict[str, str]]:
        """
        Retrieve the dataset fields stored in self._dataset_fields.

        Returns:
            list: A list of dictionaries representing the dataset fields.
                  Each dictionary has two keys: 'Name' and 'Info'.
                  If self._dataset_fields is not set or there are no fields,
                  an empty list is returned.

        Example:
            result = obj.get_dataset_fields()
            # Possible output:
            # [{'Name': 'FieldName1', 'Info': 'FieldInfo1'}, {'Name': 'FieldName2', 'Info': 'FieldInfo2'}, ...]
        """
        try:
            if self._dataset_fields is None:
                self.set_dataset_fields()

            if self._dataset_fields:
                self.logger.info("Successfully retrieved dataset fields.")
                return self._dataset_fields
            else:
                self.logger.warning("self._dataset_fields is not set or contains no fields.")
                return []
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving dataset fields: {str(e)}")
            return []

    """ Read/Write Methods """
    def get_(self, return_field: str) -> Union[str, int, float, bool, datetime]:
        """
        Search for a record based on the dataset index and return a specific value from the given field.

        Parameters:
            return_field: The field name whose value should be returned.

        Returns:
            The value of the return_field for the record where the dataset index matches the search value.
            Returns False if the record is not found.
        """

        # Check if the cursor is set and something was found
        if self._found:
            field_read = self.field_reader(self._created_dataset.Fields(return_field))
            self.logger.info(f"Get Field {return_field}: {field_read}")
            return field_read
        else:
            self.logger.error(f"Value {self.get_search_value()} NOT found in field {self.get_dataset_index()} of DataSet {self.get_dataset_name()}.")

            self.set_cursor()
            return False

    def set_(self, field_name: str, value: Union[str, int, float, bool, datetime]) -> bool:
        """
        Set the value of a specific field in the current record of the dataset.

        Parameters:
            field_name: The name of the field where the value should be set.
            value: The value to set.

        Returns:
            bool: True if the value was set successfully, False otherwise.
        """
        # self.start_transaction()
        self.edit_()

        try:
            field = self._created_dataset.Fields(field_name)
            if field:
                result = self.field_writer(field, value)
                if result:
                    self.logger.info(f"Value '{value}' set in field '{field_name}' of DataSet '{self.get_dataset_name()}'.")
                    self.post()
                else:
                    print(f"Couldn't write {value} to field {field}")
                return True
        except Exception as e:
            self.logger.error(f"Error while setting value '{value}' to field '{field_name}' of DataSet '{self.get_dataset_name()}': {e}")

        return False

    # First start transaction. The datasets are blocked
    def post(self) -> bool:
        """
        Commit changes made to the current record of the dataset.

        Returns:
            bool: True if changes were committed successfully, False otherwise.
        """

        try:
            dataset_state = self.get_dataset_state()
            if dataset_state in [2, 3]:  # 2 is Edit, 3 is Insert
                self._created_dataset.Post()
                self.set_dataset_state()
                self.logger.info(f"Changes to DataSet '{self.get_dataset_name()}' have been successfully committed from '{dataset_state}' state.")
                return True
            else:
                self.logger.info(f"DataSet '{self.get_dataset_name()}' is in '{dataset_state}' state, no changes to commit.")
        except Exception as e:
            self.logger.error(f"Error while committing changes to DataSet '{self.get_dataset_name()}': {e}")
            self.rollback()  # If there's an error, rollback any changes

        return False

    def can_start_transaction(self) -> bool:
        """
        Checks if a transaction can be started or if one already exists.

        Returns:
            True if a transaction can be started; False if a transaction already exists.
        """
        try:
            can_start = self._created_dataset.TryStartTransaction()
            if can_start:
                self.logger.info(f"A transaction can be started for dataset '{self._dataset_name}'.")
            else:
                self.logger.info(f"A transaction already exists for dataset '{self._dataset_name}'.")
            return can_start
        except Exception as e:
            self.logger.error(f"An error occurred while checking the transaction status for dataset '{self._dataset_name}': {str(e)}")
            raise

    def start_transaction(self):
        """
        Begin a database transaction for the current dataset.

        This function locks the current dataset for exclusive use, ensuring data integrity during
        operations that involve multiple steps. The transaction continues until a 'post' method
        (commit) is called or the transaction is explicitly rolled back.

        Returns:
            None

        Raises:
            Exception: If there's an issue starting a transaction on the dataset or if a transaction already exists.
        """
        if self.can_start_transaction():
            try:
                self._created_dataset.StartTransaction()
                self.set_dataset_state()
                self.logger.info(f"Transaction started for dataset '{self._dataset_name}'. Dataset is now locked for exclusive use.")
            except Exception as e:
                self.logger.error(f"An error occurred while starting a transaction for the dataset '{self._dataset_name}': {str(e)}")
                self.rollback()
        else:
            message = f"Cannot start transaction for dataset '{self._dataset_name}' as a transaction already exists."
            self.logger.warning(message)
            raise Exception(message)

    def edit_(self):
        """
        Set the current dataset to edit mode.

        This function allows modifications to be made to the current dataset record.
        After making changes, one would typically call a 'post' method to save the changes.

        Returns:
            None

        Raises:
            Exception: If there's an issue setting the dataset to edit mode.
        """
        try:
            self._created_dataset.Edit()
            self.set_dataset_state()
            self.logger.info(f"Dataset '{self._dataset_name}' has been set to edit mode. Mode: {self._created_dataset.State}")
        except Exception as e:
            self.logger.error(f"An error occurred while setting the dataset '{self._dataset_name}' to edit mode: {str(e)}")
            raise

    def append(self):
        """
        Add a new record to the current dataset.

        This function prepares the dataset to accept a new record. After adding the
        desired data, one would typically call a 'post' method to save the new record.

        Returns:
            None

        Raises:
            Exception: If there's an issue appending a new record to the dataset.
        """
        try:
            self._created_dataset.Append()
            self.set_dataset_state()
            self.logger.info(f"Prepared to add a new record to the dataset '{self._dataset_name}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while preparing to add a new record to the dataset '{self._dataset_name}': {str(e)}")
            raise

    def commit(self):
        """
        Commit changes made to the current dataset during a transaction.

        This function saves all changes made to the dataset since the start of the transaction
        and releases the lock, allowing other operations to access the dataset. Does a rollback
        if the commit raised an error

        Returns:
            None

        Raises:
            Exception: If there's an issue committing changes to the dataset.
        """
        try:
            self._created_dataset.Commit()
            self.set_dataset_state()
            self.logger.info(f"Transaction committed and changes saved for dataset '{self._dataset_name}'. Lock released.")
        except Exception as e:
            self.logger.error(f"An error occurred while committing changes to the dataset '{self._dataset_name}': {str(e)}. Initiating rollback...")
            self.rollback()

    def rollback(self):
        """
        Roll back changes made to the current dataset during a transaction.

        This function undoes all changes made to the dataset since the start of the transaction
        and releases the lock, allowing other operations to access the dataset.

        Returns:
            None

        Raises:
            Exception: If there's an issue rolling back changes to the dataset.
        """
        try:
            self._created_dataset.Rollback()
            self.set_dataset_state()
            self.logger.info(f"Changes rolled back for dataset '{self._dataset_name}'. Lock released.")
        except Exception as e:
            self.logger.error(f"An error occurred while rolling back changes to the dataset '{self._dataset_name}': {str(e)}")
            raise

    def set_cursor(self) -> bool:
        """
        If the dataset is ranged, the cursor is set to the first element.
        Set the cursor position in the dataset based on the provided index and search value.

        Returns:
            A tuple containing:
                - A boolean indicating if the record was found.
                - The dataset object.
        """
        self._found = self._created_dataset.FindKey(self.get_dataset_index(), self.get_search_value())

        if self._found:
            self.logger.info(f"Cursor successfully set to Index: {self.get_dataset_index()} with value "
                             f"{self.get_search_value()}. Type of search_value is: {type(self.get_search_value())}.")
            return True
        else:
            self.logger.warning(f"Failed to set cursor for Index: {self.get_dataset_index()} with value "
                                f"{self.get_search_value()}.")
            return False

    def get_id(self):
        return self.get_("ID")

    def get_erstdat(self):
        """
        Fetches the creation date from the dataset.

        :return: Creation date.
        """
        return self.get_("ErstDat")

    def get_aenddat(self):
        return self.get_("LtzAend")

    """ Nested """
    def get_nested_(self, nested_dataset_name, index_field, search_value, return_field):
        self.set_nested_dataset(nested_dataset_name=nested_dataset_name)

        found = self._nested_dataset.FindKey(index_field, search_value)
        if found:
            field_read = self.field_reader(self._nested_dataset.Fields(return_field))
            return field_read
        return False

    def set_nested_dataset(self, nested_dataset_name):
        self._nested_dataset = self._created_dataset.NestedDataSets(nested_dataset_name)

    def get_nested_dataset(self, nested_dataset_name=None):
        if nested_dataset_name:
            self.set_nested_dataset(nested_dataset_name=nested_dataset_name)

        return self._nested_dataset

    def get_all_nested_datasets(self):
        nested_datasets_list = []
        for nested_dataset in self.get_created_dataset().NestedDataSets:
            nested_datasets_list.append({'Name': nested_dataset.Name, 'Info:': nested_dataset.Info})
        return nested_datasets_list

    """ Ranges """
    def range_set(self, index=None, search_value=None, range_end=None) -> bool:
        """
        Set a range on the dataset based on the provided index, search value, and range end.

        The method attempts to set a range on the dataset using the provided index, search value, and range end.
        If any of these values are not set, the method logs an error and returns False.
        Otherwise, it sets the range and logs the outcome (success or failure).

        Returns:
            bool: True if the range was successfully set, False otherwise.
        """
        if index:
            self.set_dataset_index(dataset_index=index)

        if search_value:
            self.set_search_value(search_value=search_value)

        if range_end:
            self.set_range_end(range_end=range_end)

        # Check if all required values are set
        if not self.get_dataset_index() or not self.get_search_value() or not self.get_range_end():
            self.logger.error(
                "Required values (Dataset Index, Search Value, Range End) are not set. Cannot set the range."
            )
            return False

        try:
            self.logger.info(
                f"Try set_range for Index: {self.get_dataset_index()}:{type(self.get_dataset_index())} with start value {self.get_search_value()}:{type(self.get_search_value())} and end value {self.get_range_end()}:{type(self.get_range_end())}."
            )
            # Attempt to set the range on the dataset
            self._created_dataset.SetRange(
                self.get_dataset_index(),
                self.get_search_value(),
                self.get_range_end()
            )
            # Apply the range
            self._created_dataset.ApplyRange()

            # Log the outcome of the set range operation
            if self._created_dataset.RecordCount >= 1:
                self._is_ranged = True

                self.logger.info(
                    f"Range successfully set for Index: {self.get_dataset_index()} with start value {self.get_search_value()} and end value {self.get_range_end()}."
                )
                self._found = True
                self.range_first()
            else:
                self.logger.warning("Failed to set the range.")
            return self._is_ranged

        except Exception as e:
            # Log any exceptions that occur during the set range operation
            self.logger.error(
                f"An unexpected error occurred while setting the range: {str(e)}"
            )
            return False

    def range_first(self):
        self.logger.info("Try to set the cursor to the first element.")
        self._created_dataset.First()

    def range_nested_first(self):
        self._nested_dataset.First()

    def range_eof(self):
        return self._created_dataset.Eof

    def range_nested_eof(self):
        return self._nested_dataset.Eof

    def range_next(self):
        self.logger.info("Jumping to next Element.")
        self._created_dataset.Next()

    def range_count(self):
        if self._is_ranged:
            range_count = self._created_dataset.RecordCount
            self.logger.info(f"Dataset range count. {range_count}")
            self.set_range_count()
            return range_count
        else:
            self.logger.warning("Dataset range count called, but dataset is not ranged!")
            return None

    """ Utility Methods """
    def find_one(self, search_value, dataset_index):
        if not search_value:
            self.logger.warning("Search Value is needed!")
        else:
            self.set_search_value(search_value)

        if dataset_index:
            self.set_dataset_index(dataset_index=dataset_index)

        found = self.set_cursor()
        return found

    def print_all_datasets(self):
        """Print the names and descriptions of all datasets."""
        for ds_info in self._dataset_infos:
            print(ds_info.Name, '-', ds_info.Bez)

    def get_index_field(self):
        """
        Retrieve index field information from the dataset.

        Returns:
            dict: A dictionary containing index names as keys, and their associated fields as values.

        Example:
            {
                "IndexName1": [{"Name": "FieldName1", "Info": "FieldInfo1"}, ...],
                "IndexName2": [{"Name": "FieldName2", "Info": "FieldInfo2"}, ...],
                ...
            }
        """
        ds = self._dataset_infos.Item(self._dataset_name).CreateDataSet()
        ds.First()
        index_info = {}
        for index in ds.Indices:
            index_name = index.Name
            fields = [{"Name": index_field.Name, "Info": index_field.Info} for index_field in index.IndexFields]
            index_info[index_name] = fields
        return index_info

    def get_all_indicies(self):
        """
        Get all indices from the dataset and return them as a dictionary.

        Returns:
            A dictionary where each key is an index name and the value is a list of dictionaries containing field info.
        """
        indices_dict = {}  # Dictionary to hold the result

        ds = self.get_created_dataset()
        ds.First()

        for index in ds.Indices:
            index_name = index.Name
            index_fields = []

            for index_field in index.IndexFields:
                index_field_dict = {
                    'Name': index_field.Name,
                    'Info': index_field.Info
                }
                index_fields.append(index_field_dict)

            indices_dict[index_name] = index_fields
        self.logger.info(f"")
        return indices_dict

    def field_reader(self, field):
        cast_type = self.field_types_to_read.get(field.FieldType)

        if not cast_type:
            print(f"Unknown FieldType: {field.FieldType}")
            return None

        try:
            # Using the getattr function to dynamically access the attribute or method
            casted_attribute_or_method = getattr(field, cast_type)
            # Check if it's callable (i.e., a method) or just an attribute
            if callable(casted_attribute_or_method):
                casted_value = casted_attribute_or_method()
            else:
                casted_value = casted_attribute_or_method

            return casted_value
        except AttributeError:
            print(f"Field does not have an attribute or method named {cast_type}.")
            return None
        except Exception as e:
            print(f"Error while casting field: {e}")
            return None

    def field_writer(self, field, value):
        """
        Set the value of a field using the appropriate cast type.

        Parameters:
            field: The dataset field whose value needs to be set.
            value: The value to be set to the field.

        Returns:
            bool: True if the field's value is set successfully, False otherwise.
        """

        cast_type = self.field_types_to_write.get(field.FieldType)

        if not cast_type:
            self.logger.warning(f"Unknown FieldType: {field.FieldType}")
            return False

        try:
            # Using the setattr function to dynamically set the attribute or method's value
            setattr(field, cast_type, value)
            self.logger.info(f"Value '{value}' set to field using cast type '{cast_type}'.")
            return True
        except AttributeError:
            self.logger.error(f"Field does not have an attribute or method named {cast_type}.")
            return False
        except Exception as e:
            self.logger.error(f"Error while setting value to field: {e}")
            return False

    def field_exists(self, field_name: str) -> bool:
        """
        Check if a specific field exists in the dataset.

        This method checks if a given field (provided by the field_name parameter) exists in the dataset.

        Args:
            field_name (str): The name of the field to check.

        Returns:
            bool: True if the field exists in the dataset, otherwise False.

        Example:
            exists = obj.field_exists("FieldName1")
            # Possible output: True or False
        """
        try:
            all_fields = self.get_dataset_fields()
            if all_fields:
                # Check if any field in all_fields has a name that matches field_name
                for field in all_fields:
                    if field['Name'] == field_name:
                        self.logger.info(f"The field '{field_name}' exists in {self._dataset_name}.")
                        return True
                self.logger.warning(f"The field '{field_name}' does not exist in {self._dataset_name}.")
                return False
            else:
                self.logger.warning(f"Fields of {self._dataset_name} could not be fetched. No check for Field 'Bild' possible.")
                return False
        except Exception as e:
            self.logger.error(f"An error occurred while checking for the existence of the field '{field_name}': {str(e)} in {self._dataset_name}")
            return False

    def get_erp_app_object(self):
        """
        Retrieve the 'soAppObject' special object from the ERP.

        Returns:
            object or bool: The 'soAppObject' if successful, otherwise False.
        """
        try:
            # Fetch the special ERP object named 'soAppObject'
            erp_app = self._erp.getSpecialObject(self._erp_special_objects["soAppObject"])

            # If the erp_app object is not available, log a warning and return False
            if not erp_app:
                self.logger.warning("Unable to fetch the 'soAppObject' from the ERP.")
                return False

            # Log the successful retrieval of 'soAppObject'
            self.logger.info(f"Successfully retrieved 'soAppObject' from the ERP.")

            return erp_app

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the 'soAppObject': {str(e)}")
            return False

    """ Medias """
    def get_med_file_name(self, media):
        """
        Extracts the file name without the extension from the file_path.
        Example: beispiel_schrank_schublade.jpg returns beispiel_schrank_schublade
        :return: File name without extension or None if an error occurs.
        """
        try:
            base_name = os.path.basename(media)  # Get the last part of the path
            file_name_without_extension = os.path.splitext(base_name)[0]  # Split the base name and get the name part
            if file_name_without_extension:
                return file_name_without_extension
            else:
                self.logger.warning("No file name found in the provided path.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the file path: {str(e)}")
            return None

    def get_med_file_type(self, media):
        """
        Extracts the file type (extension) from the file_path.
        Example: beispiel_schrank_schublade.jpg returns jpg
        :return: File type (extension) without the dot or None if an error occurs.
        """
        try:
            file_type = os.path.splitext(media)[1][1:]  # Split the path and get the extension part without the dot
            if file_type:
                return file_type
            else:
                self.logger.warning("No file type found in the provided path.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the file path: {str(e)}")
            return None

    def get_med_file_size(self, media):
        path = GCBridgeConfig.ASSETS_PATH + GCBridgeConfig.IMG_PATH
        try:
            img_from_web = requests.head(f"{path}/{media}")
            img_from_web.raise_for_status()
            file_size = int(img_from_web.headers.get('Content-Length', 0))
            return file_size
        except requests.RequestException as e:
            self.logger.error(f"An error occurred while calculating the file size from the web: {str(e)}")
            return None

    def get_max_img_nr(self):
        """
        Retrieve the maximum available number of article images from the ERP's special object.

        This method interacts with the 'soAppObject' special object in the ERP to determine
        the total available article images.

        Returns:
            int or bool: The number of available article images if successful, otherwise False.
        """
        try:
            # Get the 'soAppObject' using the method from the parent class
            erp_app = self.get_erp_app_object()

            # If the erp_app object is not available, return False
            if not erp_app:
                return False

            # Retrieve the maximum available article images from the 'soAppObject'
            available_images = erp_app.GetAppVar(self._erp_app_var["ArtikelBilder"])

            # If the available images are not fetched successfully, log a warning and return False
            if not available_images:
                self.logger.warning("Unable to determine the available article images.")
                return False

            # Log the successful retrieval of available images
            self.logger.info(f"Successfully retrieved {available_images} available article images from the ERP.")

            return int(available_images)

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the available article images: {str(e)}")
            return False

    def get_images_file_list(self):
        """
        Retrieve the file names for all available article images from the ERP's special object.

        This method interacts with the ERP to determine the file names for each available
        article image by iterating through all possible image slots.

        Returns:
            list[str] or bool: A list of file names for all available article images if successful, otherwise False.
        """
        if not self.field_exists("Bild"):
            self.logger.error(f"Field 'Bild' does not exist in {self._dataset_name}. Returning False")
            return False

        image_paths = []

        try:
            # Get the maximum number of available images
            max_images = self.get_max_img_nr()

            # If max_images is False or not an integer, return False
            if not isinstance(max_images, int):
                self.logger.warning("Unable to determine the total available images.")
                return False

            # Iterate through each available image slot and retrieve its file path
            for i in range(1, max_images + 1):
                # WTF Microtech?!?!?!?! Why is the first without an index? WHY?
                if i == 1:
                    image_index = "Bild"
                else:
                    if self.field_exists(f"Bild{i}"):
                        image_index = f"Bild{i}"
                    else:
                        continue

                filepath = self._created_dataset.Fields.Item(f"{image_index}").GetEditObject(4).LinkFileName
                self.logger.info(f"Bild String: {filepath}")
                # Check if filepath is valid
                if filepath:
                    # Check if the filepath contains path separators, if not, it's already a filename
                    if os.path.sep in filepath:
                        filename = os.path.basename(filepath)
                    else:
                        filename = filepath

                    # Check if filename is valid before appending
                    if filename:
                        image_paths.append(filename)
                else:
                    self.logger.warning(f"No image given in Field: 'Bild{i}'.")

            # Log the successful retrieval of image paths
            self.logger.info(f"Successfully retrieved {len(image_paths)} image filenames from the ERP.")

            # Now check if we got any image(s), otherwise return None
            if not image_paths:
                self.logger.warning("But unfortunately, no images were found at all. So we return None")
                return None

            return image_paths

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the image filenames: {str(e)}")
            return False

    @abstractmethod
    def map_erp_to_bridge(self):
        pass

    def map_erp_media_to_bridge(self, media):
        bridge_media_entity = BridgeMediaEntity(
            file_name=self.get_med_file_name(media),
            file_type=self.get_med_file_type(media),
            file_size=self.get_med_file_size(media),
            # title should be configered elsewhere
            # description should be configered elsewhere
            created_at=self.get_erstdat(),
            edited_at=self.get_aenddat()
        )
        return bridge_media_entity

    @abstractmethod
    def map_bridge_to_erp(self, bridge_entity):
        pass