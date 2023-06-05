from django.shortcuts import render
import uuid
import csv
import pytz
import pandas as pd
from datetime import datetime, timedelta, time
from pytz import timezone
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Store, StoreStatus, StoreHours, Report, ReportData



def read_csv(request):
    """
    This function handles the upload and processing of CSV files containing store-related data.

    Parameters:
        request: The HTTP request object.

    Returns:
        A success reponse of uploading file - success.html.
    
    Scope of Improvement:
        - Optimize database operations with bulk insert/update operations.
        - Implement polling to fetch file after every hour from a file / messaging broker queue. 
        - Implement retry mechanisms if any connections gets down. 
        - Handle corner cases such as missing or invalid data.
        - Incorporate logging .
        - Develop unit tests for code verification.
    """
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['file']
        # Check if it's a csv file 
        if not csv_file.name.endswith('.csv'):
            return render(request, 'error.html', {'error': 'Please upload a CSV file.'})
        
        df = pd.read_csv(csv_file)

        #Process the data and store it in the database

        # Store Status data
        if 'status' in df.columns:  
            for _, row in df.iterrows():
                store_id = row['store_id']
                timestamp_utc = pd.to_datetime(row['timestamp_utc'])
                status = row['status']
                try:
                    store = Store.objects.get(store_id=store_id)
                    StoreStatus.objects.create(store=store, timestamp_utc=timestamp_utc, status=status)
                except Store.DoesNotExist:
                    continue
        # Store Hours data
        elif 'day' in df.columns:  
            for _, row in df.iterrows():
                store_id = row['store_id']
                day_of_week = row['day']
                start_time_local = (row['start_time_local'])
                end_time_local = (row['end_time_local'])
                try:
                    store = Store.objects.get(store_id=store_id)
                    store_hours, _ = StoreHours.objects.get_or_create(store=store, day_of_week=day_of_week, start_time_local=start_time_local, end_time_local=end_time_local)

                    store_hours.save()
                except Store.DoesNotExist:
                    continue
        # Store Timezone data
        elif 'timezone_str' in df.columns:  
            for _, row in df.iterrows():
                store_id = row['store_id']
                timezone_str = row['timezone_str']
                Store.objects.update_or_create(store_id=store_id, defaults={'timezone_str': timezone_str})

         # Render a success template or redirect to another page
        return render(request, 'success.html')
    
    return render(request, 'upload.html')


def generate_report(request):

    """
    This function generates a report by calculating the uptime and downtime of stores based on the store's data ,
    timestamps and business hours.

    Parameters:
        request: The HTTP request object.

    Returns:
        A JSON response containing the generated report ID.


    Scope of Improvement:
        -Add error handling and exception catching for potential errors during database operations.
        -Implement aggregation / caching for faster efficiency.
        -Optimize the calculation logic to reduce redundant computations and improve efficiency.
        -Implement proper logging.
        -Implement query optimizations for more efficient database interactions.

    """

    

    #max_timestamp can be used as the one greatest in file / current 

    #max_timestamp = StoreStatus.objects.order_by('-timestamp_utc').first().timestamp_utc
    max_timestamp = datetime.now()

    # retrieve flat list of store_id values from the Store model in Django.
    store_ids = Store.objects.values_list('store_id', flat=True)

    report_id = str(uuid.uuid4())
    report = Report.objects.create(report_id=report_id, status='Running')

    for store_id in store_ids:
        store = Store.objects.get(store_id=store_id)
        store_hours = StoreHours.objects.filter(store=store)

        # calculate the starting timestamps for the last hour, last day, and last week based on  max_timestamp.
        last_hour_start = max_timestamp - timedelta(hours=1)
        last_day_start = max_timestamp - timedelta(days=1)
        last_week_start = max_timestamp - timedelta(weeks=1)


        uptime_last_hour , downtime_last_hour= calculate_uptime(store, last_hour_start, max_timestamp, store_hours) 
        uptime_last_day , downtime_last_day = map( lambda x : x / 60 , calculate_uptime(store, last_day_start, max_timestamp, store_hours))
        uptime_last_week , downtime_last_week = map( lambda x : x/ 60, calculate_uptime(store, last_week_start, max_timestamp, store_hours))


        ReportData.objects.create(report=report, store_id=store_id,
                                  uptime_last_hour=uptime_last_hour, uptime_last_day=uptime_last_day,
                                  uptime_last_week=uptime_last_week, downtime_last_hour=downtime_last_hour,
                                  downtime_last_day=downtime_last_day, downtime_last_week=downtime_last_week)

    report.status = 'Complete'
    report.save()

    return JsonResponse({'report_id': report_id})




def get_report(request, report_id):

    """
    Retrieves a report with the given report ID and returns it as a CSV file if the report is complete.

    Parameters:
        - request: The HTTP request object.
        - report_id: The ID of the report to retrieve.

    Returns:
        - If the report ID is missing, returns a JSON response with an error message and status code 400.
        - If the report is not found, returns a JSON response with an error message and status code 404.
        - If the report is running, returns a JSON response with the status value 'Running'.
        - If the report is complete, returns a CSV file as a response for download.

    Scope of Improvements:
        - Error handling can be enhanced.
        - Implementation of caching mechanisms to store the generated CSV files temporarily
         and serve them directly without re-generating them every time a request is made for the same report.
        - We can use asynchronous processing to avoid blocking the main request/response cycle.
    """

    if not report_id:
        return JsonResponse({'error': 'Report ID is missing.'}, status=400)
    
    try:
        report = Report.objects.get(report_id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found.'}, status=404)
    

    if report.status == 'Running':
        return JsonResponse({'status': 'Running'})
    elif report.status == 'Complete':
        csv_data = generate_csv(report)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report.csv"'

        writer = csv.writer(response)
        for row in csv_data:
            writer.writerow(row)

        return response
    




def calculate_uptime(store, start_time, end_time, store_hours):

    """
    Calculates the uptime and downtime for a store within a given time range.

    Parameters:
        - store: The store object for which to calculate uptime.
        - start_time: The start time of the time range.
        - end_time: The end time of the time range.
        - store_hours: QuerySet of store hours entries for the store.

    Returns:
        A tuple containing the total uptime and downtime in minutes.

    Scope of Improvement: 
        - We can optimize the database queries by using bulk operations or aggregations instead of querying for
         each hour separately.
        - Implement caching to get the previuosly calcuated data and update the results with uptime and downtime
        of this polling interval. This will significantly reduce the time to generate report in polling intervals.
        - We can optimize algorithm to calculate uptime and downtime, such as dividing the time range into larger 
        chunks (e.g., days) and calculating uptime/downtime for each chunk instead of hour by hour . 
        - By using aggregations , we can limit the number of database query to only one. 

    """

    timezone_obj = pytz.timezone(store.timezone_str)
    start_time = timezone_obj.localize(start_time)
    end_time = timezone_obj.localize(end_time)
    uptime = timedelta()
    downtime = timedelta()
    current_time = start_time

    while current_time < end_time:
        next_time = current_time + timedelta(hours=1)


        business_hours = store_hours.filter(day_of_week=current_time.weekday()).first()

        if business_hours:
            start_time_local = datetime.combine(current_time.date(), business_hours.start_time_local)
            end_time_local = datetime.combine(current_time.date(), business_hours.end_time_local)
        else:
            # Default values for start_time_local and end_time_local
            start_time_local = datetime.combine(current_time.date(), time(0, 0, 0))
            end_time_local = datetime.combine(current_time.date(), time(23, 59, 59))


        # Make start_time_local and end_time_local timezone-aware
        start_time_local = timezone_obj.localize(start_time_local)
        end_time_local = timezone_obj.localize(end_time_local)

        # Handle overlapping windows
        if start_time_local > next_time or end_time_local < current_time:
            # No overlap with the current hour, skip it
            current_time = next_time
            continue

        if start_time_local < current_time:
            start_time_local = current_time

        if end_time_local > next_time:
            end_time_local = next_time

        store_status = StoreStatus.objects.filter(
            store=store,
            timestamp_utc__gte=start_time_local,
            timestamp_utc__lt=end_time_local,
            status='active'
        ).exists()

        if store_status:
            uptime += end_time_local - start_time_local
        else :
            downtime += end_time_local - start_time_local
    
        current_time = next_time

    return uptime.total_seconds() / 60 , downtime.total_seconds() / 60




def generate_csv(report):

    """
    Generates a CSV file based on the data in the ReportData model associated with the given report.

    Parameters:
        report (Report): The report object.

    Returns:
        list: A list representing rows in the CSV file.

    Scope of Improvement:
        - Add error handling for cases where the report object is not found or there is an issue with
         retrieving the associated ReportData objects.
        - If the number of ReportData objects is large, we can consider implementing pagination or streamlining
         the retrieval process to minimize memory usage.
        - We can separate the logic from here to improve modularity and reusability.
    """

    report_data = ReportData.objects.filter(report=report)

    csv_data = [
        ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']
    ]

    for data in report_data:
        csv_data.append([
            data.store_id,
            data.uptime_last_hour,
            data.uptime_last_day,
            data.uptime_last_week,
            data.downtime_last_hour,
            data.downtime_last_day,
            data.downtime_last_week,
        ])

    return csv_data