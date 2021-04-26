import xml.etree.ElementTree as ET

def print_tag_and_text(tag, text):
    print(tag + " : " + text)

def main():
    tree = ET.parse('srx xml.txt')
    root = tree.getroot()
    address_book = root[0][6][2]
    for item in address_book:
        
        # Exporting all addresses
        if item.tag == 'address':
            for address in item:
                if address.tag == 'name':
                        print_tag_and_text(address.tag, address.text)
        
        # Exporting all address-sets
        if item.tag == 'address-set':
            for address_set in item:
                if address_set.tag == 'name':
                    print_tag_and_text(address_set.tag, address_set.text)
                elif address_set.tag == 'description':
                    print_tag_and_text(address_set.tag, address_set.text)
                elif address_set.tag == 'address':
                    for name in address_set:
                        print_tag_and_text(name.tag, name.text)

if __name__ == "__main__":
    main()

