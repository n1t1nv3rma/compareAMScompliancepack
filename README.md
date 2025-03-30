# Check AMS's AWS Config pack coverage against the global open source AWS config compliance packs

A simple python script to compare the [AMS Config rules pack](https://docs.aws.amazon.com/managedservices/latest/accelerate-guide/acc-sec-compliance.html) coverage against the open source [AWS Config global compliance packs](https://github.com/awslabs/aws-config-rules/tree/master/aws-config-conformance-packs)

## Usage
1. Clone the repo.
2. Install required Python packages as per **requirements.txt** in your virt env. or globally
   ```
   pip install -r requirements.txt
   ```
4. From the link above, download the AMS compliance pack in zip format given in the **ams_config_rules.zip** file. Edit the .XLSX file, and delete all columns other than "**Rule Name, Identifier, DocLink, Service**", and save it as CSV (ex: **ams_config_rules.csv**), OR you can use the given *ams_config_rules.csv* file in this repo.
6. Run the script as ** % python download_config_rules.py <open source compliance pack's yaml file name> ** , Example:
   ```
   python check_AMS_Coverage.py Operational-Best-Practices-for-APRA-CPG-234.yaml
   ```
8. The comparrision / result wil be saved in the **ams_config_rules_comparison.html** file.
