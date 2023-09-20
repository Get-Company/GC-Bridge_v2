"""
These examples are considered that
Examples:
    Print the Bez1 from the Artikle 900000:
    erp_art = ERPArtikelEntity(search_value="900000")
    print(erp_art.get_("Bez1"))

    Print the 900000 Umsatz from März 2023:
    erp_art = ERPArtikelEntity(search_value="900000")
    print(erp_art.get_nested_ums(2023,


"""
from datetime import datetime
from typing import List, Union, Tuple, Any, Dict

from ..ERPCoreController import ERPCoreController
from ..controller.ERPConnectionController import ERPConnectionController


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

    def __init__(self, dataset_name, dataset_index, search_value=None, range_end=None):
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
            self._erp = ERPConnectionController().get_erp()

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

            # initialize Search Value as Empty:
            self._search_value = None
            # When the cursor is set, this attributes changes to True
            self._found = False
            if search_value:
                self.logger.info(f"Search Value provided: {search_value}. Call self.set_search_value.")
                self.set_search_value(search_value=search_value)
                self.logger.info(f"Search Value is set. Call self.set_cursor.")
                self.set_cursor()

            # Set range if range_end
            self._range_end = None
            self._is_ranged = False
            if range_end:
                self.set_range_end(range_end=range_end)
                # Set the range on the dataset
                self.range_set()
                self.set_is_ranged()
                self.set_range_count()

            # Initialize range_count as empty
            self._range_count = None

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
                'Double': 'AsString'
            }

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
        self.logger.info(f"Is Dataset ranged: {ranged}")
        self._is_ranged = ranged

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

        Parameters:
            range_count: Integer representing the count of the range.

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
        if self._range_count is None:
            self.logger.warning("Range Count is not set")
            self.set_range_count()

        return self._range_count

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
        self.start_transaction()
        self.edit_()

        try:
            field = self._created_dataset.Fields(field_name)
            if field:
                self.field_writer(field, value)
                self.logger.info(f"Value '{value}' set in field '{field_name}' of DataSet '{self.get_dataset_name()}'.")
                self.post()
                return True
        except Exception as e:
            self.logger.error(f"Error while setting value '{value}' to field '{field_name}' of DataSet '{self.get_dataset_name()}': {e}")
        finally:
            self.commit()

        return False

    # First start transaction. The datasets are blocked
    def post(self) -> bool:
        """
        Commit changes made to the current record of the dataset.

        Returns:
            bool: True if changes were committed successfully, False otherwise.
        """

        try:
            dataset_state = self._created_dataset.State
            if dataset_state in ['dsEdit', 'dsInsert']:
                self._created_dataset.Post()
                self.logger.info(f"Changes to DataSet '{self.get_dataset_name()}' have been successfully committed from '{dataset_state}' state.")
                return True
            else:
                self.logger.info(f"DataSet '{self.get_dataset_name()}' is in '{dataset_state}' state, no changes to commit.")
        except Exception as e:
            self.logger.error(f"Error while committing changes to DataSet '{self.get_dataset_name()}': {e}")
            self.rollback()  # If there's an error, rollback any changes

        return False

    def start_transaction(self):
        """
        Begin a database transaction for the current dataset.

        This function locks the current dataset for exclusive use, ensuring data integrity during
        operations that involve multiple steps. The transaction continues until a 'post' method
        (commit) is called or the transaction is explicitly rolled back.

        Returns:
            None

        Raises:
            Exception: If there's an issue starting a transaction on the dataset.
        """
        try:
            self._created_dataset.StartTransaction()
            self.logger.info(f"Transaction started for dataset '{self._dataset_name}'. Dataset is now locked for exclusive use.")
        except Exception as e:
            self.logger.error(f"An error occurred while starting a transaction for the dataset '{self._dataset_name}': {str(e)}")
            raise

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
            self.logger.info(f"Dataset '{self._dataset_name}' has been set to edit mode.")
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
            self.logger.info(f"Prepared to add a new record to the dataset '{self._dataset_name}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while preparing to add a new record to the dataset '{self._dataset_name}': {str(e)}")
            raise

    def commit(self):
        """
        Commit changes made to the current dataset during a transaction.

        This function saves all changes made to the dataset since the start of the transaction
        and releases the lock, allowing other operations to access the dataset.

        Returns:
            None

        Raises:
            Exception: If there's an issue committing changes to the dataset.
        """
        try:
            self._created_dataset.Commit()
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
            self.logger.info(f"Changes rolled back for dataset '{self._dataset_name}'. Lock released.")
        except Exception as e:
            self.logger.error(f"An error occurred while rolling back changes to the dataset '{self._dataset_name}': {str(e)}")
            raise

    def set_cursor(self) -> bool:
        """
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

    def range_set(self) -> bool:
        """
        Set a range on the dataset based on the provided index, search value, and range end.

        Returns:
            A boolean indicating if the range was successfully set.
        """
        if not self.get_dataset_index() or not self.get_search_value() or not self.get_range_end():
            self.logger.error("Required values (Dataset Index, Search Value, Range End) are not set. Cannot set the range.")
            return False

        found = self._created_dataset.SetRange(
            self.get_dataset_index(),
            self.get_search_value(),
            self.get_range_end()
        )

        if found:
            self.logger.info(f"Range successfully set for Index: {self.get_dataset_index()} with start value {self.get_search_value()} and end value {self.get_range_end()}.")
            self.range_first()
        else:
            self.logger.warning("Failed to set the range.")

        return found

    def range_first(self):
        self._created_dataset.First()

    def range_eof(self):
        return self._created_dataset.Eof

    def range_next(self):
        self._created_dataset.Next()

    def range_count(self):
        if self._is_ranged:
            range_count = self._created_dataset.RecordCount()
            self.logger.info(f"Dataset range count. {range_count}")
            self.set_range_count(range_count=range_count)
            return True
        else:
            self.logger.warning("Dataset range count called, but dataset is not ranged!")

    """ Utility Methods """

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

    def get_all_fields(self) -> List[Dict[str, str]]:
        """
        Retrieve all fields from the dataset.

        This method fetches all the fields present in the dataset and returns
        them as a list of dictionaries. Each dictionary contains the 'Name'
        and 'Info' attributes of a field.

        Returns:
            list: A list of dictionaries where each dictionary represents a field in the dataset.
                  Each dictionary has two keys: 'Name' and 'Info'.
                  If the dataset is not available or there are no fields,
                  an empty list is returned.

        Example:
            result = obj.get_all_fields()
            # Possible output:
            # [{'Name': 'FieldName1', 'Info': 'FieldInfo1'}, {'Name': 'FieldName2', 'Info': 'FieldInfo2'}, ...]

        """
        dataset = self.get_created_dataset()
        if dataset:
            return [{'Name': field.Name, 'Info': field.Info} for field in dataset.Fields]
        return []

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



