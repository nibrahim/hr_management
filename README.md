# Vcard generator

This Python script converts data from a CSV file into VCards (.vcf) format. Each row in the CSV file corresponds to an individual's contact information, and the script creates a VCard for each person.

    
   CSV file named "names.csv" with the following columns: Last Name, First Name, Title, Email, and Phone

## Usage

   Place the "names.csv" file in the same directory as the script.
    
   VCards will be generated and saved in a directory named "v_cards."


The generated VCards include the following information:

    Full Name
    Organization and Title
    Work Phone
    Work Address
    Email Address

Output Directory

  If the "v_cards" directory does not exist, the script will create it to store the generated VCards.
