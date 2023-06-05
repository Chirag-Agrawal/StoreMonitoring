from django.db import models

class Store(models.Model):
    store_id = models.IntegerField(primary_key=True)
    timezone_str = models.CharField(max_length=100, default='America/Chicago')

class StoreStatus(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)

class StoreHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

class Report(models.Model):
    report_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100)

class ReportData(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    store_id = models.IntegerField()
    uptime_last_hour = models.IntegerField()
    uptime_last_day = models.IntegerField()
    uptime_last_week = models.IntegerField()
    downtime_last_hour = models.IntegerField()
    downtime_last_day = models.IntegerField()
    downtime_last_week = models.IntegerField()
