# Gauge Financial

Gauge Financial is a comprehensive Personal Finance Management System developed using Python, Django, Pandas, and the OpenAI API. This web application aims to help users efficiently manage their bank statements and transactions, providing an intuitive interface for financial data analysis.

<div style="display: flex; justify-content: space-around;">
    <img src="https://github.com/sahaile/gaugefinancial/blob/master/Screen%20Shot%202024-10-14%20at%2010.40.32%20AM.png" alt="Application Screenshot 1" width="500">
    <img src="https://github.com/sahaile/gaugefinancial/blob/master/Screen%20Shot%202024-10-14%20at%2010.41.24%20AM.png" alt="Application Screenshot 2" width="500">
</div>

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)

## About

Gauge Financial enables users to register, upload bank statements, and analyze their financial data with advanced categorization and visualization features. It is designed to simplify personal finance management and provide valuable insights into spending habits.

## Key Features

- **User Authentication**: Secure user registration and login functionality, allowing users to create accounts and manage their profiles.
  
- **Bank Statement Upload**: Users can upload bank statements in various formats (CSV, XLSX, and XLS). The application validates the uploaded files and extracts relevant transaction data for processing. *(Note: Heroku only allows files up to 30MB to be uploaded. To upload larger files clone repository and run the development server.)*

- **Automated Transaction Categorization**: Utilizing the OpenAI API, the application automatically categorizes transactions into predefined categories (e.g., Utilities, Groceries, Entertainment) and can handle uncategorized transactions intelligently.

- **Financial Insights**: Users can analyze their financial data through comprehensive monthly and yearly summaries, detailing total revenues and expenses. The system provides visualizations for better understanding and decision-making.

- **Bank Statement Management**: Users can view, download, or delete bank statements easily. The application supports searching through uploaded statements to enhance usability.

- **Chat Functionality**: A built-in chat feature allows users to interact with the AI assistant for personalized financial advice based on their transaction history.

- **Profile Management**: Users can update their profiles, change passwords, and manage their accounts directly within the application.

## Technologies Used

- **Python**
- **Django**
- **Pandas**
- **OpenAI API**: Utilized for intelligent transaction categorization.
- **Heroku**

## Getting Started

To set up the project locally, follow these instructions:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/gauge-financial.git
   cd gauge-financial
2. Must include an OpenAI key in views.py
3. **Run the development server**:
   ```bash
    python3 manage.py runserver
4. **Access the application**:
   Open your web browser and go to http://127.0.0.1:8000/.

