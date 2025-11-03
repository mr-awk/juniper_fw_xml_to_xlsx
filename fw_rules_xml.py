import xml.etree.ElementTree as ET
import pandas as pd
import sys
import getopt


def get_text_object(element):
    """Helper to safely get text from an element."""
    return element.text if element.text is not None else ''


def get_tag_object(element, tag):
    """Helper to safely get a child element by tag."""
    return element.find(tag)


def get_address(address_element):
    """Extract address information from an address element.
    
    Returns a list: [name, description, ip_prefix]
    """
    # Initialize all variables to empty strings
    name = ''
    description = ''
    ip_prefix = ''
    
    for child in address_element:
        match child.tag:
            case 'name':
                name = get_text_object(child)
            case 'description':
                description = get_text_object(child)
            case 'ip-prefix':
                ip_prefix = get_text_object(child)
    
    return [name, description, ip_prefix]


def get_address_set(address_set_element):
    """Extract address-set information from an address-set element.
    
    Returns a list: [name, description, addresses_in_set]
    """
    # Initialize all variables to empty strings
    name = ''
    description = ''
    addresses_in_set = ''
    
    for child in address_set_element:
        match child.tag:
            case 'name':
                name = get_text_object(child)
            case 'description':
                description = get_text_object(child)
            case 'address':
                # Iterate over children of the address element
                for addr_child in child:
                    if addr_child.tag == 'name':
                        addresses_in_set += get_text_object(addr_child) + '\n'
    
    return [name, description, addresses_in_set]


def get_term(term_element):
    """Extract term information from a term element.
    
    Returns a formatted string: 'dest_port/protocol\\n'
    """
    # Initialize all variables to empty strings
    term_label_dest_port = ''
    term_label_protocol = ''
    
    for child in term_element:
        match child.tag:
            case 'destination-port':
                term_label_dest_port = get_text_object(child)
            case 'protocol':
                term_label_protocol = get_text_object(child)
    
    if len(term_label_dest_port) > 0 and len(term_label_protocol) > 0:
        return term_label_dest_port + '/' + term_label_protocol + '\n'
    return ''


def get_application(application_element):
    """Extract application information from an application element.
    
    Returns a list: [name, source_port, dest_port, protocol, term_label]
    """
    # Initialize all variables to empty strings
    name = ''
    source_port = ''
    dest_port = ''
    protocol = ''
    term_label = ''
    
    for child in application_element:
        match child.tag:
            case 'name':
                name = get_text_object(child)
            case 'protocol':
                protocol = get_text_object(child)
            case 'destination-port':
                dest_port = get_text_object(child)
            case 'source-port':
                source_port = get_text_object(child)
            case 'term':
                term_label += get_term(child)
    
    return [name, source_port, dest_port, protocol, term_label]


def get_application_set(app_set_element):
    """Extract application-set information from an application-set element.
    
    Returns a list: [name, application_in_set]
    """
    # Initialize all variables to empty strings
    name = ''
    application_in_set = ''
    
    for child in app_set_element:
        match child.tag:
            case 'name':
                name = get_text_object(child)
            case 'application':
                # Iterate over children of the application element
                for app_child in child:
                    if app_child.tag == 'name':
                        application_in_set += get_text_object(app_child) + '\n'
    
    return [name, application_in_set]


def get_submatch(match_element):
    """Extract match information from a match element.
    
    Returns a list: [sub_match_source_addr, sub_match_dest_addr, sub_match_app]
    """
    # Initialize all variables to empty strings
    sub_match_source_addr = ''
    sub_match_dest_addr = ''
    sub_match_app = ''
    
    for child in match_element:
        match child.tag:
            case 'source-address':
                sub_match_source_addr += get_text_object(child) + '\n'
            case 'destination-address':
                sub_match_dest_addr += get_text_object(child) + '\n'
            case 'application':
                sub_match_app += get_text_object(child) + '\n'
    
    return [sub_match_source_addr, sub_match_dest_addr, sub_match_app]


def get_subpolicy(subpolicy_element):
    """Extract subpolicy information from a policy element.
    
    Returns a list: [subpol_name, sub_match_source_addr, sub_match_dest_addr, sub_match_app]
    """
    # Initialize all variables to empty strings
    subpol_name = ''
    sub_match_source_addr = ''
    sub_match_dest_addr = ''
    sub_match_app = ''
    
    for child in subpolicy_element:
        match child.tag:
            case 'name':
                subpol_name = get_text_object(child)
            case 'match':
                match_info = get_submatch(child)
                sub_match_source_addr = match_info[0]
                sub_match_dest_addr = match_info[1]
                sub_match_app = match_info[2]
    
    return [subpol_name, sub_match_source_addr, sub_match_dest_addr, sub_match_app]


def get_policy(policy_element):
    """Extract policy information from a policy element.
    
    Returns a list of lists, each: [from_zone_name, to_zone_name, subpol_name, 
                                     sub_match_source_addr, sub_match_dest_addr, sub_match_app]
    """
    # Initialize all variables to empty strings
    from_zone_name = ''
    to_zone_name = ''
    policies_list = []
    
    for child in policy_element:
        match child.tag:
            case 'from-zone-name':
                from_zone_name = get_text_object(child)
            case 'to-zone-name':
                to_zone_name = get_text_object(child)
            case 'policy':
                subpolicy_info = get_subpolicy(child)
                policies_list.append([from_zone_name, to_zone_name] + subpolicy_info)
    
    return policies_list


def process_address_book(address_book_element):
    """Process address-book element and return lists of addresses and address-sets."""
    addresses = []
    address_sets = []
    
    print("Reading addresses and address-sets in address-book")
    
    for child in address_book_element:
        match child.tag:
            case 'address':
                addresses.append(get_address(child))
            case 'address-set':
                address_sets.append(get_address_set(child))
    
    return addresses, address_sets


def process_policies(policies_element):
    """Process policies element and return list of policies."""
    policies = []
    
    print("Reading policies in policies")
    
    for child in policies_element:
        match child.tag:
            case 'policy':
                policies.extend(get_policy(child))
    
    return policies


def process_applications(applications_element):
    """Process applications element and return lists of applications and application-sets."""
    applications = []
    application_sets = []
    
    print("Reading applications and applications-sets in configuration")
    
    for child in applications_element:
        match child.tag:
            case 'application':
                applications.append(get_application(child))
            case 'application-set':
                application_sets.append(get_application_set(child))
    
    return applications, application_sets


def process_security(security_element):
    """Process security element and return addresses, address-sets, and policies."""
    addresses = []
    address_sets = []
    policies = []
    
    for child in security_element:
        match child.tag:
            case 'address-book':
                addr, addr_sets = process_address_book(child)
                addresses.extend(addr)
                address_sets.extend(addr_sets)
            case 'policies':
                policies.extend(process_policies(child))
    
    return addresses, address_sets, policies


def process_configuration(configuration_element):
    """Process configuration element and return all collected data."""
    addresses = []
    address_sets = []
    policies = []
    applications = []
    application_sets = []
    
    for child in configuration_element:
        match child.tag:
            case 'security':
                addr, addr_sets, pols = process_security(child)
                addresses.extend(addr)
                address_sets.extend(addr_sets)
                policies.extend(pols)
            case 'applications':
                apps, app_sets = process_applications(child)
                applications.extend(apps)
                application_sets.extend(app_sets)
    
    return addresses, address_sets, policies, applications, application_sets


def write_to_excel(addresses, address_sets, policies, applications, application_sets, outputfile):
    """Write all data to Excel file."""
    with pd.ExcelWriter(outputfile, engine='xlsxwriter') as writer:
        # Write Addresses sheet
        if addresses:
            df1 = pd.DataFrame(addresses, columns=['Name', 'Description', 'IP Address'])
            df1.to_excel(writer, index=False, sheet_name='Addresses')
        
        # Write Address-sets sheet
        if address_sets:
            df2 = pd.DataFrame(address_sets, columns=['Name', 'Description', 'Addresses'])
            df2.to_excel(writer, index=False, sheet_name='Address-sets')
        
        # Write Policies sheet
        if policies:
            df3 = pd.DataFrame(policies, columns=['from-zone-name', 'to-zone-name', 'name',
                                                   'source-address', 'destination-address', 'application'])
            df3.to_excel(writer, index=False, sheet_name='Policies')
        
        # Write Applications sheet
        if applications:
            df4 = pd.DataFrame(applications, columns=['Name', 'Source port', 'Destination port',
                                                       'Protocol', 'Destination ports/protocol'])
            df4.to_excel(writer, index=False, sheet_name='Applications')
        
        # Write Application-sets sheet
        if application_sets:
            df5 = pd.DataFrame(application_sets, columns=['Name', 'Applications'])
            df5.to_excel(writer, index=False, sheet_name='Application-sets')


def parse_args(argv):
    """Parse command line arguments and return inputfile and outputfile.
    
    Returns: (inputfile, outputfile)
    """
    # Initialize defaults before parsing
    inputfile = 'srx.xml'
    outputfile = 'test.xlsx'
    
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print('fw_rules_xml.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    
    # Parse options
    for opt, arg in opts:
        if opt == '-h':
            print('fw_rules_xml.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
    
    # Validate values after parsing
    if not inputfile:
        inputfile = 'srx.xml'
    if not outputfile:
        outputfile = 'test.xlsx'
    
    return inputfile, outputfile


def main():
    """Main function to parse XML and generate Excel output."""
    # Parse command line arguments
    inputfile, outputfile = parse_args(sys.argv[1:])
    
    # Parse XML file
    tree = ET.parse(inputfile)
    root = tree.getroot()
    
    # Initialize data containers
    addresses = []
    address_sets = []
    policies = []
    applications = []
    application_sets = []
    
    # Process XML tree
    for child in root:
        match child.tag:
            case 'configuration':
                addr, addr_sets, pols, apps, app_sets = process_configuration(child)
                addresses.extend(addr)
                address_sets.extend(addr_sets)
                policies.extend(pols)
                applications.extend(apps)
                application_sets.extend(app_sets)
    
    # Write all data to Excel once
    write_to_excel(addresses, address_sets, policies, applications, application_sets, outputfile)


if __name__ == '__main__':
    main()
