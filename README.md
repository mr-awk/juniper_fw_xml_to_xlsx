# Juniper Firewall Configuration XML to Excel xlsx

This script makes Juniper SRX firewall XML exports more readable in Excel format, better for validation processes.

## Usage

```bash
python3 fw_rules_xml.py -i <inputfile> -o <outputfile>
```

### Options

- `-i, --input`: Input XML file (default: srx.xml)
- `-o, --output`: Output Excel file (default: test.xlsx)
- `-h`: Show help message

### Examples

```bash
# Using default files (srx.xml -> test.xlsx)
python3 fw_rules_xml.py

# Specifying custom input and output files
python3 fw_rules_xml.py -i config.xml -o output.xlsx

# Show help
python3 fw_rules_xml.py -h
```

## Output

The script generates an Excel workbook with the following sheets:
- **Addresses**: Individual address objects
- **Address-sets**: Groups of addresses
- **Policies**: Security policies with source/destination zones and match criteria
- **Applications**: Application definitions
- **Application-sets**: Groups of applications
