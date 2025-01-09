# DNS Record Fetcher

A full-stack web application that allows users to fetch and display DNS records for any given domain. This application uses a Python Flask backend to query DNS records and a modern HTML/CSS/JavaScript frontend for user interaction.

## Features

- Fetches various DNS record types, including:
  - **A**
  - **AAAA**
  - **MX**
  - **CNAME**
  - **NS**
  - **TXT**
  - **SOA**
- Displays DNS records in a user-friendly format.
- Handles errors gracefully (e.g., invalid domains, no DNS records found).
- Clean and responsive frontend interface.

## Technologies Used

### Backend:
- **Python**: Main backend logic.
- **Flask**: Lightweight framework for handling HTTP requests.
- **dnspython**: Library for querying DNS records.

### Frontend:
- **HTML5**: Structuring the web pages.
- **CSS3**: Styling the web interface.
- **JavaScript**: Fetching data from the backend asynchronously and dynamically displaying it.

## Installation and Usage

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/dns-record-fetcher.git
cd dns-record-fetcher
```
### Step 2: Install Dependencies
```bash
pip install flask dnspython
```
### Step 3: Run the Application
```bash
python dns_record.py
```
### Step 4: Access the Application
Open your browser and go to:
http://127.0.0.1:5000/

### How It Works
**Homepage**:
Enter a domain name (e.g., example.com).
Click the "Fetch DNS Records" button.
**DNS Record Results**:
View the DNS records grouped by type (e.g., A, MX, NS).
Handles invalid inputs and errors gracefully with user-friendly messages.
