
# StoreMonitoring

StoreMonitoring is a Django-based microservice for monitoring the status and hours of operation of multiple stores. It provides functionality to upload CSV files containing store status, store hours, and store timezone data, which are then processed and stored in the database.

## Features

- Upload CSV files containing store status, store hours, and store timezone data.
- Process and store the uploaded data in the database.
- Retrieve and display store status, hours, and timezone information.

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/Chirag-Agrawal/StoreMonitoring.git
   ```

2. **Create and activate a virtual environment:**

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```
   pip install -r requirements.txt
   ```

4. **Set up the database:**

   ```
   python manage.py migrate
   ```

5. **Run the development server:**

   ```
   python manage.py runserver
   ```

6. **Access the application:**

   Open your web browser and visit `http://localhost:8000`.

## Usage

1. **Upload CSV files:**

   - Visit the upload page at `http://localhost:8000/kitchens/upload`.
   - Choose a CSV file containing store status, store hours, or store timezone data.
   - Click the "Upload" button to process and store the data.

2. **View store reports:**

   - Once the data is uploaded and processed, reports can be generated.
   - Visit the trigger report page at `http://localhost:8000/kitchens/trigger_report` to generate a new report.
   - Reports are automatically generated for the first 10 stores and include information such as uptime, downtime, and timestamps.
   - The generated report will be assigned a unique report ID.

3. **Access individual reports:**

   - To view a specific report, use the report ID in the URL.
   - Visit `http://localhost:8000/kitchens/get_report/{report_id}` to view the details of a report.

## Contributing

Contributions to StoreMonitoring are welcome! If you find any bugs, have suggestions for improvements, or would like to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Django](https://www.djangoproject.com/) - Web framework for Python
- [Pandas](https://pandas.pydata.org/) - Data manipulation library in Python

Feel free to customize this README file according to your project's specific details and requirements.