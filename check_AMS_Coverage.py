import sys
import requests
import yaml
from datetime import datetime, timedelta
from urllib.parse import urljoin

def download_and_parse_yaml(yaml_file):
    base_url = "https://raw.githubusercontent.com/awslabs/aws-config-rules/master/aws-config-conformance-packs/"
    yaml_url = urljoin(base_url, yaml_file)
    
    print(f"Downloading and parsing: {yaml_url}")
    try:
        # Download the YAML file
        response = requests.get(yaml_url)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse YAML content
        yaml_content = yaml.safe_load(response.text)
        
        # Extract required information
        rules = yaml_content.get('Resources', {})
        results = []
        
        for rule_name, rule_info in rules.items():
            if rule_info.get('Type') == 'AWS::Config::ConfigRule':
                properties = rule_info.get('Properties', {})
                config_rule_name = properties.get('ConfigRuleName', '')
                source = properties.get('Source', {})
                owner = source.get('Owner', '')
                source_identifier = source.get('SourceIdentifier', '')
                
                results.append({
                    'ConfigRuleName': config_rule_name,
                    'Owner': owner,
                    'SourceIdentifier': source_identifier
                })
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML content: {e}")
        return None
    
# Load and parse AMS config rule in the local CSV file ams_config_rules/ams_config_rules.csv and extract Identifier, DocLink, and Service values 
def parse_ams_config_rules () :
    print("Parsing AMS config rules...")
    ams_config_rules = []
    with open('ams_config_rules/ams_config_rules.csv', 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 4:
                name, identifier, doc_link, service = parts
                ams_config_rules.append({
                    'Name': name,
                    'SourceIdentifier': identifier,
                    'DocLink': doc_link,
                    'Service': service
                })
    return ams_config_rules

# Compare the items in the "results" and "ams_config_rules" list with same SourceIdentifier and build an html page with a table showing the difference, along with total matched values
def compare_and_generate_html(results, ams_config_rules,html_content):
    print("Comparing and generating HTML...")
    matched_count = 0
    unmatched_count = 0
    additional_ams_rules_count = 0
    html_unmatched_content = ""
    html_ams_content = ""
    html_content = html_content
    
    # Find rules covered under AMS set of config rules

    for result in results:
        for ams_config_rule in ams_config_rules:
            if result['SourceIdentifier'] == ams_config_rule['SourceIdentifier']:
                html_content += f"""
                <tr>
                    <td><a href={ams_config_rule['DocLink']}>{result['ConfigRuleName']}</a></td>
                    <td>{result['Owner']}</td>
                    <td>{result['SourceIdentifier']}</td>
                    <td>{ams_config_rule['Service']}</td>
                </tr>
                """
                matched_count += 1
                break

     # List ones not covered by AMS Config Rules
    for result in results:
        if not any(ams_config_rule['SourceIdentifier'] == result['SourceIdentifier'] for ams_config_rule in ams_config_rules):
            html_unmatched_content += f"""
            <tr style="background-color: #aacccc">
                <td>{result['ConfigRuleName']}</td>
                <td>{result['Owner']}</td>
                <td>{result['SourceIdentifier']}</td>
                <td></td>
            </tr>
            """
            unmatched_count += 1
   
    # Get all remaining unmatched items from ams_config_rules
    for ams_config_rule in ams_config_rules:
        if not any(result['SourceIdentifier'] == ams_config_rule['SourceIdentifier'] for result in results):
            additional_ams_rules_count += 1
            html_ams_content += f"""
            <tr style="background-color: #ffcccc">
                <td><a href={ams_config_rule['DocLink']}>{ams_config_rule['Name']}</a></td>
                <td>{ams_config_rule['SourceIdentifier']}</td>
                <td></td>
                <td></td>
            </tr>
            """ 

    # Join Rules not matched with AMS Config Rules
    html_content += """
    <tr style="background-color: #ddcccc;"> <th colspan="4"> Rules not matched with AMS Config Rules: </th> </tr>
    {html_unmatched_content}
    """.format(html_unmatched_content=html_unmatched_content)

    # Join all remaining unmatched AMS Config Rules
    html_content += """
    <tr style="background-color: #bbcccc;"> <th colspan="4"> Additional AMS Config Rules: </th> </tr>
    {html_ams_content}
    """.format(html_ams_content=html_ams_content)

    html_content += """
        </table>
        <ul>
        <li><p><h3>Total Config Rules in your Compliance Framework: {}</p></h3>
        <li><p><h3>Total Rules covered by AMS Config Rules: {}</p></h3>
        <li><p><h3>Percentage covered by AMS Config Rules: {:.2f}%</p></h3>
        <li><p><h3>Remaining Rules not in AMS Config Rules: {}</p></h3>
        <li><p><h3>Additional AMS Rules: {}</p></h3>
        <li><p><h3>Total AMS Config Rules: {}</p></h3>

        </ul>
        </body>
        </html>
        """.format(len(results), matched_count, (matched_count / len(results)) * 100, unmatched_count, additional_ams_rules_count, len(ams_config_rules))
    
    with open('ams_config_rules_comparison.html', 'w') as file:
        file.write(html_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python download_config_rules.py <yaml_file_name>")
        print("Example: python check_AMS_Coverage.py Operational-Best-Practices-for-APRA-CPG-234.yaml")
        sys.exit(1)
    
    yaml_file = sys.argv[1]

    html_content = ""
    # Start making main page
    html_content = """
        <html>
        <head>
            <title>AMS Config Rules Comparison</title>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <h1>AMS Config Rules Comparison</h1>
        """

    html_content += f"""
        <u>Compliance pack:</u> <b>{yaml_file}</b>
        <p>
        <p><b>Updated on:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} local time
        <br> </br>
        <table>
            <tr>
                <th>ConfigRuleName</th>
                <th>Owner</th>
                <th>SourceIdentifier</th>
                <th>Service</th>
            </tr>
        """


    try:
        results = download_and_parse_yaml(yaml_file)
        if results:
            #print(results) - for DEBUG
            ams_config_rules = parse_ams_config_rules()
            if ams_config_rules:
                # print(ams_config_rules) - for DEBUG
                compare_and_generate_html(results, ams_config_rules, html_content)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
