# Bulk Alumni Upload Guide

## Overview
This feature allows administrators to upload multiple alumni records at once using CSV or Excel files. The system can automatically generate emails and passwords for entries that don't have them.

## Endpoint
**POST** `/api/v1/users/bulk-upload-alumni`

**Authentication:** Admin only (requires valid JWT token)

## Supported File Formats
- `.csv` (Comma Separated Values)
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

## Required Columns

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| full_name | ✅ Yes | Full name of the alumni | John Doe |
| series | ✅ Yes | Graduation year/batch | 2020 |

## Auto-Generated Fields

If these fields are missing, the system will generate them automatically:

| Field | Auto-Generation Logic | Example |
|-------|----------------------|---------|
| email | Generated from name.series@alumni.rca.com | john.doe.2020@alumni.rca.com |
| password | Random 12-character secure password | aB3xY9mK4pQ7 |

**Note:** Auto-generated credentials will be returned in the API response so you can send them to the alumni.

## Optional Columns

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| email | String | Custom email (if not auto-generated) | alumni@example.com |
| password | String | Custom password (if not auto-generated) | mypassword123 |
| phone_number | String | Phone number | +8801712345678 |
| blood_group | String | Blood group | A+, A-, B+, B-, O+, O-, AB+, AB- |
| department | String | Department | CSE, EEE, CE, ME |
| university_id | String | Student ID | 2020123456 |
| is_employed | Boolean | Employment status | true, false, yes, no |
| current_company | String | Current company name | Tech Corp |
| designation | String | Job title | Software Engineer |
| work_location | String | Work location | Dhaka, Bangladesh |
| linkedin_profile | String | LinkedIn URL | https://linkedin.com/in/username |

## CSV File Example

```csv
full_name,series,email,password,phone_number,blood_group,department,university_id,is_employed,current_company,designation,work_location
John Doe,2020,john.doe@example.com,password123,+8801712345678,A+,CSE,2020123456,true,Tech Corp,Software Engineer,Dhaka
Jane Smith,2019,,,+8801812345678,B+,EEE,2019123456,true,Digital Solutions,Senior Developer,Chittagong
Ahmed Khan,2021,,,+8801912345678,O+,CE,2021123456,false,,,Rajshahi
Fatima Rahman,2018,,,,A-,CSE,,true,Global Tech,Team Lead,Dhaka
```

**Note:** Rows 2-5 have empty email and password fields - these will be auto-generated!

## Excel File Format

Create an Excel file with the first row containing column headers (same as CSV):
- Row 1: Headers (email, password, full_name, etc.)
- Row 2+: Data for each alumni

## Usage Example

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/users/bulk-upload-alumni" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@alumni_data.csv"
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/api/v1/users/bulk-upload-alumni"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}
files = {
    "file": open("alumni_data.csv", "rb")
}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

## Response Format

```json
{
  "total": 5,
  "success": 5,
  "failed": 0,
  "errors": [],
  "created_users": [
    {
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "series": "2020"
    },
    ...
  ],
  "auto_generated_credentials": [
    {
      "row": 2,
      "email": "jane.smith.2019@alumni.rca.com",
      "full_name": "Jane Smith",
      "email_generated": true,
      "password": "aB3xY9mK4pQ7",
      "password_generated": true
    },
    {
      "row": 3,
      "email": "ahmed.khan.2021@alumni.rca.com",
      "full_name": "Ahmed Khan",
      "email_generated": true,
      "password": "xT5nM8qR2kL9",
      "password_generated": true
    }
  ]
}
```

**Important:** Save the `auto_generated_credentials` - these contain the passwords for accounts where credentials were auto-generated!

## Error Handling

The endpoint will:
- Validate each row individually
- Skip rows with errors and continue processing
- Return detailed error information for failed rows
- Only commit successful entries to the database
- Rollback all changes if a critical error occurs

## Common Errors

1. **"User already exists"** - Email is already registered
2. **"Missing required fields: full_name and series are mandatory"** - Full name or series column is empty
3. **"Invalid file format"** - File is not CSV or Excel
4. **"No filename provided"** - File upload is missing

## Tips

1. **Only full_name and series are required** - Everything else can be auto-generated or left empty
2. Always test with a small sample file first
3. Auto-generated emails follow pattern: `firstname.lastname.series@alumni.rca.com`
4. Auto-generated passwords are 12-character secure random strings
5. **Save auto-generated credentials** from the response to send to alumni
6. Blood group format: Use standard notation (A+, B-, etc.)
7. Boolean fields: Use true/false, yes/no, or 1/0
8. Remove any empty rows at the end of your file

## Email Generation Logic

When email is not provided:
1. If `university_id` exists: Uses `university_id.series@alumni.rca.com`
2. Otherwise: Uses `firstname.lastname.series@alumni.rca.com`
3. If duplicate: Adds counter `firstname.lastname.series.1@alumni.rca.com`

Examples:
- John Doe, 2020 → `john.doe.2020@alumni.rca.com`
- University ID: 2020123456, 2020 → `2020123456.2020@alumni.rca.com`

## Sample Files

A sample CSV file is provided: `sample_alumni_upload.csv`

## Dependencies

For Excel file support, ensure `openpyxl` is installed:
```bash
pip install openpyxl
```

Or add to `pyproject.toml`:
```toml
dependencies = [
    ...
    "openpyxl>=3.0.0",
]
```
