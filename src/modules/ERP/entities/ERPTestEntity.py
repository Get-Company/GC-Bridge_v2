from src.modules.ERP.controller.ERPConnectionController import ERPConnectionController

erp = ERPConnectionController().get_erp()
# Field Types and how to read them:
field_types = {
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
# Adressen Example on how to get a specific field like AdrNr by Index Field WShopID and Index WShopID:6825
adressen_ds = erp.DataSetinfos.Item("Adressen").CreateDataSet()  # Create the complete Dataset "Adressen"
found = adressen_ds.FindKey("WShopID", 6825)
if found:
    print(adressen_ds.Fields("AdrNr").AsString)

# Anschriften Example on how to get a specific fields like AdrNr, WShopID and the FieldType of AdrNr by Index Field AdrNrAnsNr and Indicies AdrNr:10026, AnsNr: 0
anschriften_ds = erp.DataSetinfos.Item("Anschriften").CreateDataSet()  # Create the complete Dataset "Anschriften"
found = anschriften_ds.FindKey("AdrNrAnsNr", ["10026", 0])  # Set the cursor in index 'Nr' with value 10026, return bool and adresse_ds is set to 'Nr' 10026
if found:
    adrnr_buchner = anschriften_ds.Fields("AdrNr").AsString  # Return the field AdrNr as AsString
    wshopid = anschriften_ds.Fields("WShopId").AsString
    field_type = anschriften_ds.Fields("AdrNr").FieldType  # Get the FieldType and compare the list of field_types for the right casting
    how_to_cast_field = field_types[field_type]
    print("AdrNr:", adrnr_buchner, "| FieldType:", field_type, "| To cast as:", how_to_cast_field, "| WShopId:", wshopid)

# Ansprechpartner Example on how to get a range between the index field AdrNrAnsNrAspNr by the indicies AdrNr:10026, AnsNr:0, AspNr:0 and AdrNr:10026, AnsNr:0, AspNr:0
ansprechpartner_ds = erp.DataSetinfos.Item("Ansprechpartner").CreateDataSet()
ansprechpartner_ds.Indices.Item("AdrNrAnsNrAspNr").Select()  # Set the Index to AdrNrAnsNr
ansprechpartner_ds.SetRangeStart()  # Start the Range with following Fields and Values
ansprechpartner_ds.Fields("AdrNr").AsString = "10026"
ansprechpartner_ds.Fields("AnsNr").AsInteger = 0
ansprechpartner_ds.Fields("AspNr").AsInteger = 0
ansprechpartner_ds.SetRangeEnd()  # End the range by the limiting values
ansprechpartner_ds.Fields("AdrNr").AsString = "10026"
ansprechpartner_ds.Fields("AnsNr").AsInteger = 0
ansprechpartner_ds.Fields("AspNr").AsInteger = 0
ansprechpartner_ds.ApplyRange()  # Apply the range and clean the dataset. Now the dataset only contains data within the range

# Example how to loop through a range
if ansprechpartner_ds.IsRanged() and ansprechpartner_ds.RecordCount >= 1:
    ansprechpartner_ds.First()
    while not ansprechpartner_ds.Eof:   # Do while we are not at the end - Eof
        print(
            ansprechpartner_ds.Fields("AdrNr").AsString,
            ansprechpartner_ds.Fields("AnsNr").AsString,
            ansprechpartner_ds.Fields("AspNr").AsString,
            ansprechpartner_ds.Fields("AnspAufbau").AsInteger,
        )
        ansprechpartner_ds.Next()  # Set to the next row of data
