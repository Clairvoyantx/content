from pytest import raises
from CommonServerPython import *
from dateutil.parser import parse


def test_get_incident_attributes():
    from SymantecDLP import get_incident_attributes
    attributes_input = {
        'Test': 'test',
        'severity': 'High',
        'custom_attribute_name': 'can',
        'custom_attribute_value': 'cav',
        'data_owner_name': 'don',
        'data_owner_email': 'doe',
        'note': 'note_msg',
        'note_time': '2018-08-06T18:30:50.833000+05:30'
    }
    attributes_output_one = {
        'severity': 'High',
        'note': {
            'dateAndTime': parse('2018-08-06T18:30:50.833000+05:30'),
            'note': 'note_msg'
        },
        'customAttribute': {
            'name': 'can',
            'value': 'cav'
        },
        'dataOwner': {
            'name': 'don',
            'email': 'doe'
        },
    }
    attributes_output_two = {
        'severity': 'High'
    }
    assert attributes_output_one == get_incident_attributes(attributes_input)
    del attributes_input['custom_attribute_name']
    with raises(DemistoException, match="If updating an incident's custom attribute,"
                                        " both custom_attribute_name and custom_attribute_value must be provided."):
        get_incident_attributes(attributes_input)
    del attributes_input['custom_attribute_value']
    del attributes_input['data_owner_email']
    with raises(DemistoException, match="If updating an incident's data owner,"
                                        " both data_owner_name and data_owner_email must be provided."):
        get_incident_attributes(attributes_input)
    del attributes_input['data_owner_name']
    del attributes_input['note_time']
    with raises(DemistoException, match="If adding an incident's note, both note and note_time must be provided."):
        get_incident_attributes(attributes_input)
    del attributes_input['note']
    assert attributes_output_two == get_incident_attributes(attributes_input)


def test_parse_component():
    from SymantecDLP import parse_component
    components_bytes_input = [
        {
            'componentId': 69065,
            'name': 'CCN.txt',
            'componentTypeId': 3,
            'componentType': 'ATTACHMENT_TEXT',
            'content': b'4386280016300125',
            'componentLongId': 69065
        }
    ]
    components_regular_input = [
        {
            'componentId': 69065,
            'name': 'CCN.txt',
            'componentTypeId': 3,
            'componentType': 'ATTACHMENT_TEXT',
            'content': '4386280016300125',
            'componentLongId': 69065
        }
    ]
    components_bytes_output = [
        {
            'ID': 69065,
            'Name': 'CCN.txt',
            'TypeID': 3,
            'Type': 'ATTACHMENT_TEXT',
            'Content': "b'4386280016300125'",
            'LongID': 69065
        }
    ]
    components_regular_output = [
        {
            'ID': 69065,
            'Name': 'CCN.txt',
            'TypeID': 3,
            'Type': 'ATTACHMENT_TEXT',
            'Content': '4386280016300125',
            'LongID': 69065
        }
    ]
    assert components_bytes_output == parse_component(components_bytes_input)
    assert components_regular_output == parse_component(components_regular_input)
