import streamlit as st
import psycopg2
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
import re

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'company_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

client = OpenAI(
    api_key=os.getenv('GROQ_API_KEY'),
    base_url="https://api.groq.com/openai/v1"
)

def get_database_schema():
    return """
Database Schema:

1. departments
   - id (SERIAL PRIMARY KEY)
   - name (VARCHAR(100))

2. employees
   - id (SERIAL PRIMARY KEY)
   - name (VARCHAR(100))
   - department_id (INT)
   - email (VARCHAR(255))
   - salary (DECIMAL(10,2))

3. products
   - id (SERIAL PRIMARY KEY)
   - name (VARCHAR(100))
   - price (DECIMAL(10,2))

4. orders
   - id (SERIAL PRIMARY KEY)
   - customer_name (VARCHAR(100))
   - employee_id (INT)
   - order_total (DECIMAL(10,2))
   - order_date (DATE)

Relationships:
- employees.department_id → departments.id
- orders.employee_id → employees.id
"""

def validate_sql(sql_query):
    lower_query = sql_query.lower()
    forbidden = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create', 'grant', 'revoke', '--', ';--', '/*', '*/', 'xp_', 'sp_']
    
    for word in forbidden:
        if word in lower_query:
            return False, f"Forbidden SQL keyword detected: {word}"
    
    if not lower_query.strip().startswith('select'):
        return False, "Only SELECT queries are allowed"
    
    return True, "Valid"

def natural_language_to_sql(user_query):
    schema = get_database_schema()
    
    prompt = f"""You are a SQL expert. Convert the following natural language query into a PostgreSQL SQL query.

{schema}

Rules:
1. Only generate SELECT queries
2. Use proper JOINs when needed
3. Return ONLY the SQL query, nothing else
4. Use appropriate WHERE clauses, GROUP BY, ORDER BY as needed

User Query: {user_query}

SQL Query:"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a SQL expert who converts natural language to SQL queries. Return only the SQL query without any explanation or markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    sql_query = response.choices[0].message.content.strip()
    sql_query = re.sub(r'```sql\s*', '', sql_query)
    sql_query = re.sub(r'```\s*', '', sql_query)
    sql_query = sql_query.strip()
    
    return sql_query

def execute_query(sql_query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        return results, columns, None
    except Exception as e:
        return None, None, str(e)

def hybrid_search(user_query):
    sql_query = natural_language_to_sql(user_query)
    is_valid, message = validate_sql(sql_query)
    
    if not is_valid:
        return None, None, None, f"Security Error: {message}"
    
    results, columns, error = execute_query(sql_query)
    return results, columns, sql_query, error

st.set_page_config(page_title="Natural Language Database Search", layout="wide")

st.title("Natural Language Database Search")
st.markdown("Query the company database using natural language.")

with st.sidebar:
    st.header("Example Queries")
    st.markdown("""
    Try these example queries:
    
    **Employee Queries:**
    - Show all employees in Engineering department
    - Who earns more than 70000?
    - List employees with their department names
    
    **Order Queries:**
    - Show total orders by employee
    - What are the top 5 largest orders?
    - Show orders from last 30 days
    
    **Product Queries:**
    - List all products sorted by price
    - Show products under $100
    - What is the average product price?
    
    **Complex Queries:**
    - Show employees who handled orders over $5000
    - Which department has the highest average salary?
    - Show customer orders with employee details
    """)

st.markdown("---")
user_query = st.text_input("Enter your query:", placeholder="e.g., Show all employees in the Engineering department")

col1, col2 = st.columns([1, 5])
with col1:
    search_button = st.button("Search", type="primary", width="stretch")
with col2:
    if st.button("Clear", width="stretch"):
        st.rerun()

if search_button and user_query:
    with st.spinner("Processing your query..."):
        results, columns, sql_query, error = hybrid_search(user_query)
    
    if error:
        st.error(f"Error: {error}")
    elif results is not None:
        with st.expander("Generated SQL Query", expanded=False):
            st.code(sql_query, language="sql")
        
        st.success(f"Found {len(results)} results")
        
        if len(results) > 0:
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df, width="stretch", hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        else:
            st.info("No results found for your query.")
    else:
        st.error("An unexpected error occurred.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Natural Language Database Interface</small>
</div>
""", unsafe_allow_html=True)
