# StoreMonitoring

StoreMonitoring is a Django-based microservice for monitoring the status and hours of operation of multiple stores. It provides functionality to upload CSV files containing store status, store hours, and store timezone data, which are then processed and stored in the database.
Features	
Upload CSV files containing store status, store hours, and store timezone data.
Process and store the uploaded data in the database.
Retrieve and display store status, hours, and timezone information.
Installation
Clone the repository:
bashCopy code
git clone https://github.com/Chirag-Agrawal/StoreMonitoring.git 
Create and activate a virtual environment:
bashCopy code
python3 -m venv venv source venv/bin/activate 
Install the dependencies:
Copy code
pip install -r requirements.txt 
Set up the database:
Copy code
python manage.py migrate 
Run the development server:
Copy code
python manage.py runserver 
Access the application in your browser at http://localhost:8000.
Usage
Upload CSV files:
Visit the upload page at http://localhost:8000/kitchens/upload.
Choose a CSV file containing store status, store hours, or store timezone data.
Click the "Upload" button to process and store the data.
View store reports:
Once the data is uploaded and processed, reports can be generated.
Visit the trigger report page at http://localhost:8000/kitchens/trigger_report to generate a new report.
Reports are generated for  stores and include information such as uptime, downtime, and timestamps.
The generated report will be assigned a unique report ID.
Access individual reports:
To view a specific report, use the report ID in the URL.
Visit http://localhost:8000/kitchens/get_report/{report_id} to view the details of a report.

