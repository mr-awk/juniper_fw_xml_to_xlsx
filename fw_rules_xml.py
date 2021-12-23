import xml.etree.ElementTree as ET
import pandas as pd

def print_tag_and_text(tag, text):
    print(tag + ": " + text + ', ', end='')

def main():
    tree = ET.parse('srx.xml')
    root = tree.getroot()

    addresses = []
    address_sets = []
    applications = []
    application_set = []
    policies = []

    application_in_set = ''
    sub_match_source_addr = ''
    sub_match_dest_addr = ''
    sub_match_app = ''
    term_label = ''
    addresses_in_set = ''
    source_port = ''
    dest_port = ''
    protocol = ''

    writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')

    for root_item in root:
        if root_item.tag == 'configuration':
            for conf_item in root_item:
                if conf_item.tag == 'security':
                    for sec_item in conf_item:
                        if sec_item.tag == 'address-book':
                            print("Reading addresses and address-sets in address-book")
                            for address_book_item in sec_item:
                                if address_book_item.tag == 'address':
                                    for address in address_book_item:
                                        if address.tag == 'name':
                                            name = address.text

                                        if address.tag == 'description':
                                            description = address.text

                                        if address.tag == 'ip-prefix':
                                            ip_prefix = address.text

                                    # When collected all addresses, save it to excel
                                    addresses.append([name] + [description] + [ip_prefix])
                                    df1 = pd.DataFrame( addresses,
                                                        columns=['Name','Description','IP Address'])
                                    df1.to_excel(writer, index=False, sheet_name='Addresses')

                                if address_book_item.tag == 'address-set':
                                    for address_set in address_book_item:
                                        if address_set.tag == 'name':
                                            name = address_set.text

                                        if address_set.tag == 'description':
                                            description = address_set.text

                                        if address_set.tag == 'address':
                                            addresses_in_set =  (addresses_in_set +
                                                                address_set[0].text +
                                                                '\n')

                                    # When collected all address-sets, save it to excel
                                    address_sets.append([name] + [description] + [addresses_in_set])
                                    addresses_in_set = ''
                                    df2 = pd.DataFrame( address_sets,
                                                        columns=['Name','Description','Addresses'])
                                    df2.to_excel(writer, index=False, sheet_name='Address-sets')

                        # TODO: Fix this part method
                        if sec_item.tag == 'policies':
                            print("Reading policies in policies")
                            for policy in sec_item:
                                if policy.tag == 'policy':
                                    for policy_item in policy:
                                        if policy_item.tag == 'from-zone-name':
                                            from_zone_name = policy_item.text
                                        if policy_item.tag == 'to-zone-name':
                                            to_zone_name = policy_item.text

                                        if policy_item.tag == 'policy':
                                            for subpolicy in policy_item:
                                                if subpolicy.tag == 'name':
                                                    subpol_name = subpolicy.text
                                                if subpolicy.tag == 'match':
                                                    for match in subpolicy:
                                                        if match.tag == 'source-address':
                                                            sub_match_source_addr = (sub_match_source_addr +
                                                                                     match.text +
                                                                                     '\n')
                                                        if match.tag == 'destination-address':
                                                            sub_match_dest_addr = ( sub_match_dest_addr +
                                                                                    match.text +
                                                                                    '\n')
                                                        if match.tag == 'application':
                                                            sub_match_app = sub_match_app + match.text + '\n'
                                            policies.append(    [from_zone_name] +
                                                                [to_zone_name] +
                                                                [subpol_name] +
                                                                [sub_match_source_addr] +
                                                                [sub_match_dest_addr] +
                                                                [sub_match_app])
                                            sub_match_app = ''
                                            sub_match_dest_addr = ''
                                            sub_match_source_addr = ''

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

                if conf_item.tag == 'applications':
                    print("Reading applications and applications-sets in configuration")
                    for application in conf_item:
                        if application.tag == 'application':
                            for application_item in application:
                                if application_item.tag == 'name':
                                    name = application_item.text
                                if application_item.tag == 'protocol':
                                    protocol = application_item.text
                                if application_item.tag == 'destination-port':
                                    dest_port = application_item.text
                                if application_item.tag == 'source-port':
                                    source_port = application_item.text
                                if application_item.tag == 'term':
                                    for term in application_item:
                                        if term.tag == 'destination-port':
                                            term_label_dest_port = term.text
                                        if term.tag == 'protocol':
                                            term_label_protocol = term.text

                                        if len(term_label_dest_port) > 0 and len(term_label_protocol) > 0:
                                            term_label = (  term_label +
                                                            term_label_dest_port +
                                                            '/' +
                                                            term_label_protocol +
                                                            '\n')
                                            term_label_dest_port = ''
                                            term_label_protocol = ''

                            # When collected all applications, save it to excel
                            applications.append(    [name] +
                                                    [source_port] +
                                                    [dest_port] +
                                                    [protocol] +
                                                    [term_label])
                            term_label = ''
                            protocol = ''
                            dest_port = ''
                            source_port = ''
                            term_label_dest_port = ''
                            term_label_protocol = ''

                            df4 = pd.DataFrame( applications,
                                                columns=[   'Name',
                                                            'Source port',
                                                            'Destination port',
                                                            'Protocol',
                                                            'Destination ports/protocol']
                                                            )
                            df4.to_excel(writer, index=False, sheet_name='Applications')

                        if application.tag == 'application-set':
                            for app_set_item in application:
                                if app_set_item.tag == 'name':
                                    name = app_set_item.text
                                if app_set_item.tag == 'application':
                                    application_in_set = application_in_set + app_set_item[0].text + '\n'
                            application_set.append([name] + [application_in_set])
                            application_in_set = ''

                            df5 = pd.DataFrame(application_set, columns=['Name','Applications'])
                            df5.to_excel(writer, index=False, sheet_name='Application-sets')
    writer.save()
if __name__ == '__main__':
    main()
