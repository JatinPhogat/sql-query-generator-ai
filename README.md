# Natural Language Database Search And SQL Query Generator

A Streamlit application that converts natural language queries to SQL for querying a PostgreSQL database.

## Demo Video (1080 P)

[Google drive link](https://drive.google.com/file/d/1Q4SWAiYedu39GbyCvosHW3IF0qzYR43d/view?usp=drive_link)
*Follow the link to watch how the application converts natural language queries into SQL and displays results*
*Please update your video quality setting to 1080p while watching*

## Requirements

- Python 3.8+
- PostgreSQL
- Groq API Key

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Copy `.env.example` to `.env` and update with your credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=company_db
DB_USER=postgres
DB_PASSWORD=your_password

GROQ_API_KEY=your_groq_api_key
```

3. Initialize the database:
```bash
python database_setup.py
```

4. Run the application:
```bash
streamlit run app.py
```

## Database Schema

**departments**
- id, name

**employees**
- id, name, department_id, email, salary

**products**
- id, name, price

**orders**
- id, customer_name, employee_id, order_total, order_date

## Features

- Natural language to SQL conversion
- SQL injection prevention
- Interactive query interface
- CSV export functionality
