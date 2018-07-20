import json_log_formatter
import django.utils.timezone


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['message'] = message
        if 'time' not in extra:
            extra['time'] = django.utils.timezone.now()
        return extra
