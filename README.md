# M5-20260106

## Library Data Project

### Scenario

The library is currently manually reporting and dealing with data exported from its systems. This is taking more and more time out of employees days and will suffer from human error with this getting worse as the volumes increase. These limitations are stopping stakeholders, employees and customers from benefitting from the data.

### Goals 

We are looking to design and implement a data pipeline using Python, using Git for version control, tested using unittest and deploted via Docker. This solution will handle example CSV files, producing data that can be reported on with BI tools or fed into other systems.

## Script purposes

The script should process the CSV data using functions to perform the following transformation.

- Format the column headers for consistency
- Remove empty rows with Id's we cannot match
- Format data types
- Standardise identifiers to ensure joins
- Enrich the data with calculated columns
- Flag invalid data for reporting so users are aware
- Generates a CSV file/Writes to the SQL Server database.

## Script testing

Testing is to be created for functions using unittest to ensure the expected outputs.

## Deployment
The script is to be containerised with Docker and Argparse to allow it to be run with configurable arguments for the output.



