''' IMPORTS '''
# std py packages

# 3-rd party py packages
import requests

# local py packages
import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()

''' GLOBALS/PARAMS '''
# Parameters received from the user
PARAMS = demisto.params()

# TOKEN
TOKEN = PARAMS.get('token')

# Service base URL
BASE_URL = 'https://jsonwhois.com'

# Headers to be sent in requests
HEADERS = {
    'Accept': 'application/json',
    'Authorization': f'Token token={TOKEN}'
}

# Self signed certificate so no need to verify by default
USE_SSL = not demisto.params().get('insecure', False)

''' HELPER FUNCTIONS '''
@logger
def http_request(method, url_suffix, params=None, max_retry=3):
    # A wrapper for requests lib to send our requests and handle requests and responses better
    res = requests.request(
        method,
        BASE_URL + url_suffix,
        verify=USE_SSL,
        params=params,
        data=None,
        headers=HEADERS
    )
    # Handle error responses gracefully
    if res.status_code not in {200}:
        if max_retry > 0:
            max_retry -= 1
            return http_request(method=method,
                                url_suffix=url_suffix,
                                params=params,
                                max_retry=max_retry)
        raise Exception(f'Error enrich url with JsonWhoIS API, status code {res.status_code}')
    return res.json()


def dict_by_ec(cur_dict: dict):
    """ Create dict (Json) by entry contexts convention
    Capitalize first char, remove nulls
    :param cur_dict: dictionary
    :return: dictionary by conventions
    """
    if not cur_dict:
        return None
    return {key.capitalize(): cur_dict[key] for key in cur_dict if cur_dict[key]}


def list_by_ec(cur_list: list, key_needed):
    """ Create list of dict (Json) by entry contexts convention
    Capitalize first char in dict, remove nulls, remove not needed parameters
    :param cur_list: list of dict
    :param key_needed: key to save
    :return: modified list by description above
    """
    if not cur_list:
        return None
    cur_list = [createContext(index, removeNull=True) for index in cur_list]

    def cur_ec(index):
        return {key.capitalize(): index[key] for key in index if key in key_needed}
    cur_list = [cur_ec(contact) for contact in cur_list]
    return cur_list


''' COMMANDS + REQUESTS FUNCTIONS '''


@logger
def whois(url: str) -> tuple:
    """Get Rest API raw from JsonWhoIs service
    :param url: url to search on
    :return: dict object of JsonWhoIs service
    """
    # Perform request
    params = {
        'domain': url
    }
    raw = http_request(method='GET',
                       url_suffix='/api/v1/whois',
                       params=params)

    # entry context by code convention
    ec_temp = {
        'DomainStatus': raw.get('status'),
        'NameServers': list_by_ec(raw.get('nameservers'), key_needed=['name']),
        'CreationDate': raw.get('created_on'),
        'UpdatedDate': raw.get('updated_on'),
        'ExpirationDate': raw.get('expires_on'),
        'Registrar': dict_by_ec(raw.get('registrar')),
        'Registrant': list_by_ec(raw.get('registrant_contacts'), key_needed=['name', 'phone', 'email']),
        'Admin': list_by_ec(raw.get('admin_contacts'), key_needed=['name', 'phone', 'email'])
    }

    # Clear unused fields
    ec_temp = createContext(ec_temp, removeNull=True)

    # Build all ec
    ec = {
        'Domain': {
            'WHOIS': ec_temp
        }
    }

    return ec, raw


@logger
def whois_command():
    """Whois command"""
    # Get url arg
    url = demisto.args().get('query')
    # Get parsed entry context and raw data
    ec, raw = whois(url)

    # Create human-readable format
    ec_shortcut = ec['Domain']['WHOIS']
    human_readable = ''
    if 'Admin' in ec_shortcut:
        human_readable += tableToMarkdown(name='Admin account', t=ec_shortcut['Admin'])
    if 'NameServers' in ec_shortcut:
        human_readable += tableToMarkdown(name='Name servers', t=ec_shortcut['NameServers'])
    if 'Registrant' in ec_shortcut:
        human_readable += tableToMarkdown(name='Registrant', t=ec_shortcut['Registrant'])
    if 'Registrar' in ec_shortcut:
        human_readable += tableToMarkdown(name='Registrar', t=ec_shortcut['Registrar'])

    # Others table
    others_keys = ['DomainStatus', 'CreationDate', 'UpdatedDate', 'ExpirationDate']
    ec_others = {key: ec_shortcut[key] for key in ec_shortcut if key in others_keys}
    human_readable += tableToMarkdown(name='Others', t=ec_others)

    return_outputs(readable_output=human_readable,
                   outputs=ec,
                   raw_response=raw)


@logger
def test_module():
    ec, raw = whois('demisto.com')
    status = ec.get('Domain').get('WHOIS').get('DomainStatus')
    if not status:
        demisto.results('Testing demisto.com url failed')
    demisto.results('ok')


''' EXECUTION'''


def main():
    LOG('Command being called is %s' % (demisto.command()))
    handle_proxy()
    try:
        if demisto.command() == 'whois':
            whois_command()
        if demisto.command() == 'test-module':
            test_module()

    # Log exceptions
    except Exception as e:
        return_error(str(e))


# python2 uses __builtin__ python3 uses builtins
if __name__ == "__builtin__" or __name__ == "builtins":
    main()
