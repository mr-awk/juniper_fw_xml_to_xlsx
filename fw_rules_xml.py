import xml.etree.ElementTree as ET
import pandas as pd
import getopt, sys

def print_tag_and_text(tag, text):
    print(tag + ": " + text + ', ', end='')

def get_text_object(tag):
    return tag.text

def get_tag_object(object):
    return object.tag

def get_address(address_book_item):
    for address in address_book_item:
        match get_tag_object(address):
            case 'name':
                name = get_text_object(address)
            case 'description':
                description = get_text_object(address)
            case 'ip-prefix':
                ip_prefix = get_text_object(address)
    return  ([name] 
            + [description] 
            + [ip_prefix])

def get_address_set(address_book_item):
    for address_set in address_book_item:
        match get_tag_object(address_set):
            case 'name':
                name = get_text_object(address_set)
            case 'description':
                description = get_text_object(address_set)
            case 'address':
                addresses_in_set =  (addresses_in_set +
                                get_text_object(address_set[0]) +
                                '\n')
    return  ([name]
            + [description]
            + [addresses_in_set])

def get_submatch(subpolicy):
    sub_match_app = ''
    sub_match_dest_addr = ''
    sub_match_source_addr = ''
    for match in subpolicy:
        match get_tag_object(match):
            case 'source-address':
                sub_match_source_addr = (sub_match_source_addr +
                                    get_text_object(match) +
                                    '\n')
            case 'destination-address':
                sub_match_dest_addr = ( sub_match_dest_addr +
                                    get_text_object(match) +
                                    '\n')
            case 'application':
                sub_match_app = sub_match_app + get_text_object(match) + '\n'
    return  ([sub_match_source_addr]
            + [sub_match_dest_addr]
            + [sub_match_app])

def get_subpolicy(policy_item):
    for subpolicy in policy_item:
        match get_tag_object(subpolicy):
            case 'name':
                subpol_name = get_text_object(subpolicy)
            case 'match':
                sub_match = get_submatch(subpolicy)
    return  ([subpol_name]
            + sub_match)

def get_policy(policy_item):
    match get_tag_object(policy_item):
        case 'from-zone-name':
            from_zone_name = get_text_object(policy_item)
        case 'to-zone-name':
            to_zone_name = get_text_object(policy_item)
        case 'policy':
            subpolicy = get_subpolicy(policy_item)
    return  ([from_zone_name]
            + [to_zone_name]
            + subpolicy)

def get_term(application_item):
    for term in application_item:
        match term.tag:
            case 'destination-port':
                term_label_dest_port = term.text
            case 'protocol':
                term_label_protocol = term.text
        if len(term_label_dest_port) > 0 and len(term_label_protocol) > 0:
            term_label = (  term_label +
                        term_label_dest_port +
                        '/' +
                        term_label_protocol +
                        '\n')
        term_label_dest_port = ''
        term_label_protocol = ''
        return term_label

def get_application(application):
    term_label = ''
    protocol = ''
    dest_port = ''
    source_port = ''
    term_label_dest_port = ''
    term_label_protocol = ''
    for application_item in application:
        match get_tag_object(application_item):
            case 'name':
                name = get_text_object(application_item)
            case 'protocol':
                protocol = get_text_object(application_item)
            case 'destination-port':
                dest_port = get_text_object(application_item)
            case 'source-port':
                source_port = get_text_object(application_item)
            case 'term':
                term_label = get_term(application_item)
    return  ([name]
            + [source_port]
            + [dest_port]
            + [protocol]
            + [term_label])

def read_policies_in_policies(sec_item, writer):
    policies = []
    print("Reading policies in policies")
    for policy in sec_item:
        if get_tag_object(policy) == 'policy':
            for policy_item in policy:
                policies.append(get_policy(policy_item))
                
            # When collected all policies, save it to excel
            df3 = pd.DataFrame( policies,
                                columns=[   'from-zone-name',
                                            'to-zone-name',
                                            'name',
                                            'source-address',
                                            'destination-address',
                                            'application']
                                            )
            df3.to_excel(writer, index=False, sheet_name='Policies')

def get_addresses(address_book_item, writer):
    addresses = []
    # When collected all addresses, save it to excel
    addresses.append(get_address(address_book_item))
    df1 = pd.DataFrame( addresses,
                        columns=['Name','Description','IP Address'])
    df1.to_excel(writer, index=False, sheet_name='Addresses')

def get_address_sets(address_book_item, writer):
    address_sets = []
    # When collected all address-sets, save it to excel
    address_sets.append(get_address_set(address_book_item))
    df2 = pd.DataFrame( address_sets,
                        columns=['Name','Description','Addresses'])
    df2.to_excel(writer, index=False, sheet_name='Address-sets')

def read_addresses_and_address_sets_in_address_book(sec_item, writer):
    print("Reading addresses and address-sets in address-book")
    for address_book_item in sec_item:
        match get_tag_object(address_book_item):
            case 'address':
                get_addresses(address_book_item, writer)
            case 'address-set':
                get_address_sets(address_book_item, writer)

def read_sec_item(sec_item, writer):
    match get_tag_object(sec_item):
        case 'address-book':
            read_addresses_and_address_sets_in_address_book(sec_item, writer)
        case 'policies':
            read_policies_in_policies(sec_item, writer)

def get_security(conf_item, writer):
    for sec_item in conf_item:
        read_sec_item(sec_item, writer)

def read_application(application, writer):
    applications = []
    # When collected all applications, save it to excel
    applications.append(get_application(application))
    
    df4 = pd.DataFrame( applications,
                        columns=[   'Name',
                                    'Source port',
                                    'Destination port',
                                    'Protocol',
                                    'Destination ports/protocol']
                                    )
    df4.to_excel(writer, index=False, sheet_name='Applications')

def read_application_set(application, writer):
    application_set = []
    application_in_set = ''
    for app_set_item in application:
        match app_set_item.tag:
            case 'name':
                name = app_set_item.text
            case 'application':
                application_in_set = application_in_set + app_set_item[0].text + '\n'

    application_set.append([name] + [application_in_set])
    application_in_set = ''

    df5 = pd.DataFrame(application_set, columns=['Name','Applications'])
    df5.to_excel(writer, index=False, sheet_name='Application-sets')

def get_applications(conf_item, writer):
    print("Reading applications and applications-sets in configuration")
    for application in conf_item:
        match get_tag_object(application):
            case 'application':
                read_application(application, writer)
            case 'application-set':
                read_application_set(application, writer)

def get_conf_item(root_item, writer):
    for conf_item in root_item:
        match get_tag_object(conf_item):
            case 'security':
                get_security(conf_item, writer)
            case 'applications':
                get_applications(conf_item, writer)

def get_configuration(root_item, writer):
    if get_tag_object(root_item) == 'configuration':
        get_conf_item(  root_item,
                        writer)

def main():
    args = sys.argv[1:]
    options = "hi:o:"
    long_options = ["help", "input=", "output="]
    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            if currentArg in ("-h", "--help"):
                print("Showing help")
            elif currentArg in ("-i", "--input"):
                inputfile = currentVal
            elif currentArg in ("-o", "--output"):
                outputfile = currentVal
    except getopt.error as err:
        print(str(err))

    if len(inputfile) <= 0:
        inputfile = 'srx.xml'

    tree = ET.parse(inputfile)
    root = tree.getroot()

    if len(outputfile) <= 0:
        outputfile = 'test.xlsx'

    writer = pd.ExcelWriter(outputfile, engine='xlsxwriter')

    for root_item in root:
        get_configuration(root_item, writer)

    writer.save()

if __name__ == '__main__':
    main()
