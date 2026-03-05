# Personal Finance Tracker

A comprehensive web application built with Django to help users track their income and expenses, manage multiple wallets, and maintain a clear overview of their financial health. 

## 🚀 Features

* **User Authentication (`accounts`)**: Secure sign-up, login, and profile management.
* **Wallet Management (`wallets`)**: Create and manage multiple accounts or cards to track distinct balances.
* **Transaction Tracking (`finance`)**: Record daily income and expenses, categorize transactions, and view financial history.
* **Customer Support (`support`)**: Integrated ticketing or support app to handle user inquiries and feedback.
* **Multi-language Support (`locale`)**: Internationalization (i18n) support for making the application accessible in multiple languages.
* **Responsive UI**: Clean, template-driven frontend utilizing custom HTML and CSS.

## 🛠️ Tech Stack

* **Backend**: Python, Django
* **Database**: SQLite3 (Development) 
* **Frontend**: HTML5, CSS3

## 📂 Project Structure

```text
money_tracker/
├── accounts/       # User authentication and profile management
├── config/         # Main Django project settings and routing
├── core/           # Shared utilities and base functionalities
├── finance/        # Income/expense logging and categorization logic
├── locale/         # Translation files for multi-language support
├── static/css/     # Static stylesheets
├── support/        # Helpdesk or user support functionalities
├── templates/      # Global HTML templates
├── wallets/        # Wallet and balance management
├── manage.py       # Django project management script
└── db.sqlite3      # Local development database
⚙️ Local Setup and Installation
Clone the repository:

Bash
git clone [https://github.com/abdurakhmanovjohn/money_tracker.git](https://github.com/abdurakhmanovjohn/money_tracker.git)
cd money_tracker
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:
(Assuming a requirements.txt exists. If not, you will need to install Django manually: pip install django)

Bash
pip install -r requirements.txt
Apply database migrations:

Bash
python manage.py migrate
Create a superuser (optional, for admin access):

Bash
python manage.py createsuperuser
Run the development server:

Bash
python manage.py runserver
The application will be available at http://127.0.0.1:8000/.
