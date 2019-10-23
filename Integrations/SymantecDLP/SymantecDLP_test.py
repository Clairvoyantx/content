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


def test_parse_custom_attribute():
    from SymantecDLP import parse_custom_attribute
    custom_attribute_group_list = [
        {
            'customAttribute': [
                {
                    'name': 'cn',
                    'value': None
                }
            ],
            'name': 'Default Attribute Group'
        },
        {
            'customAttribute': [
                {
                    'name': 'Resolution',
                    'value': None
                },
                {
                    'name': 'First Name',
                    'value': 'Admin'
                }
            ],
            'name': 'Predefined'
        }
    ]
    args_all = {'custom_attributes': 'all'}
    custom_attribute_all_list_output = [
        {'name': 'cn'},
        {'name': 'Resolution'},
        {'name': 'First Name', 'value': 'Admin'}
    ]
    assert custom_attribute_all_list_output == parse_custom_attribute(custom_attribute_group_list, args_all)
    args_none = {'custom_attributes': 'none'}
    assert [] == parse_custom_attribute(custom_attribute_group_list, args_none)
    args_custom = {'custom_attributes': 'custom'}
    with raises(DemistoException, match='When choosing the custom value for custom_attributes argument -'
                                        ' the custom_values list must be filled with custom attribute names.'
                                        ' For example: custom_value=ca1,ca2,ca3'):
        parse_custom_attribute(custom_attribute_group_list, args_custom)
    args_custom['custom_values'] = 'cn, First Name, bbb'
    custom_attribute_custom_list_output = [
        {'name': 'cn'},
        {'name': 'First Name', 'value': 'Admin'}
    ]
    assert custom_attribute_custom_list_output == parse_custom_attribute(custom_attribute_group_list, args_custom)
    args_custom['custom_values'] = 'aaa'
    assert [] == parse_custom_attribute(custom_attribute_group_list, args_custom)
    args_group = {'custom_attributes': 'group'}
    with raises(DemistoException, match='When choosing the group value for custom_attributes argument -'
                                        ' the custom_values list must be filled with group names.'
                                        ' For example: custom_value=g1,g2,g3'):
        parse_custom_attribute(custom_attribute_group_list, args_group)
    args_group['custom_values'] = 'Default Attribute Group, Predefined, uuu'
    custom_attribute_group_list_output = [
        {'name': 'cn'},
        {'name': 'Resolution'},
        {'name': 'First Name', 'value': 'Admin'}
    ]
    assert custom_attribute_group_list_output == parse_custom_attribute(custom_attribute_group_list, args_group)
