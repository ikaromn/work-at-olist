from datetime import datetime
from .models import CallRecord, PriceRule
from .exceptions import InvalidBillDate
import dateutil.relativedelta
from dateutil.rrule import DAILY, rrule
from django.utils import timezone

START_TYPE = 1
END_TYPE = 2


class BillValidator:
    def validate_bill_to_record(self, **kwargs):
        """Validate if call have the start type to generate the bill

        :param kwargs:
          :type call_data: dict
          :param call_data: dictionary with call record

        :rtype: bool
        :returns: True if match pair between Start and End type from call,
                  otherwise, False
        """
        call_data = kwargs['call_data']
        if call_data['type'] == 2:
            return self._existent_pair_record(call_data['call_id'])

        return False

    def _existent_pair_record(self, call_id):
        """Verify if have a pair of call_id

        :type call_id: int
        :param call_id: int to filter how much call_id have in models

        :rtype: bool
        :returns: True if more than 1 call id, otherwise False
        """
        if CallRecord.objects.filter(
            call_id=call_id
        ).count() > 1:

            return True

        return False

    def prepare_bill_data(self, call_record_data):
        """Prepare the bill data to save in bill models

        :type call_record_data: dict
        :param call_record_data: dictionary with call record data

        :returns: dictonary with a valid bill to save in models
        """
        call_id = call_record_data['call_id']
        call_record_intance = CallRecord.objects.get(
            call_id=call_id, type=START_TYPE
        )
        start_call_datetime = call_record_intance.timestamp

        end_call_datetime = call_record_data['timestamp']
        call_duration = end_call_datetime - start_call_datetime
        cost = PriceGenerator().generate_cost(call_id)

        return {
            'call': call_record_intance,
            'cost': cost,
            'call_duration': call_duration,
            'call_start': start_call_datetime,
            'call_end': end_call_datetime,
            'month': int(end_call_datetime.month),
            'year': int(end_call_datetime.year)
        }


class BillDateValidator:
    """
    Class to make all date validation
    """
    actual_date = datetime.now().date()

    def validate_bill_date(self, month=None, year=None):
        """Validade if the bill date is valid or get previous date if are null

        :type month: int
        :param month: (Optional) int with wanted month

        :type year: int
        :param year: (Optional) int with wanted year

        :returns: dictonary with valid year and moth, otherwise raise a invalid
                  bill date exception
        """
        if month and year:
            self._make_validation(int(month), int(year))
        else:
            self._get_previous_month()

        return {
            'month': self.month,
            'year': self.year
        }

    def _make_validation(self, month, year):
        """Make all validations to see if are corrects params

        :type month: int
        :param month: int to validate if a valid month

        :type year: int
        :param year: int to validate if a valid year

        :raises: :class: `IvalidBillDate <exceptions.InvalidBillDate>`
        """
        if ((year > 9999 or month > 12)
                or (year < 0 or month < 1)):
            raise InvalidBillDate("Insert a valid date")

        if year > self.actual_date.year:
            raise InvalidBillDate("Year requested is bigger than actual")

        if ((year == self.actual_date.year and month == self.actual_date.month)
                or (year == self.actual_date.year
                    and self.actual_date.month == 1)):
            raise InvalidBillDate("The bill to this month isn't closed yet")

        self.month = month
        self.year = year

    def _get_previous_month(self):
        """Get previous month
        """
        last_month = self.actual_date - dateutil.relativedelta.relativedelta(
            months=1
        )

        self.month = last_month.month
        self.year = last_month.year


class PriceGenerator:
    fixed_charge = None
    call_price = 0
    call_start = datetime.now()
    call_end = datetime.now()

    def generate_cost(self, call_id):
        """Generate the cost from a call by your period

        :type call_id: int
        :param call_id: int to get call from `CallRecord` models

        :rtype: Decimal
        :returns: Decimal from a cost of call
        """
        self.call_start = CallRecord.objects.get(
            call_id=call_id, type=START_TYPE
        ).timestamp

        self.call_end = CallRecord.objects.get(
            call_id=call_id, type=END_TYPE
        ).timestamp

        cost = self._generate_call_cost()

        return cost

    def _generate_call_cost(self):
        """Generate the cost of call based on price rules

        :rtype: Decimal
        :returns: Decimal from a call cost based on Price Cost Rules
        """
        price_rules = PriceRule.objects.all()

        for price_rule in price_rules:
            start_in_range = self._start_in_charge_period(
                price_rule.start_period,
                price_rule.end_period,
                self.call_start.time()
            )

            if start_in_range:
                self._set_fixed_charge(price_rule.fixed_charge)

            self._calculate_price_by_period(price_rule)

        full_cost = self.call_price + self.fixed_charge

        return full_cost

    def _start_in_charge_period(self, start_period, end_period, call_start):
        """Verify if the call start is on a period

        :type start_period: :class:`datetime.time`
        :param start_period: The start of rule period

        :type end_period: :class:`datetime.time`
        :param end_period: The end of rule period

        :type call_start: :class:`datetime.time`
        :param call_start: The start of call

        :rtype: bool
        :returns: True if the call start is in the range of start and end
                  period, otherwise, False.
        """
        if start_period <= end_period:
            if start_period <= call_start:
                return call_start <= end_period

        return start_period <= call_start or call_start <= end_period

    def _set_fixed_charge(self, fixed_charge):
        """Set fixed charge if aren't setted

        :type fixed_charge: Decimal
        :param fixed_charge: Call fixed charge
        """
        if not self.fixed_charge:
            self.fixed_charge = fixed_charge

    def _calculate_price_by_period(self, price_rule):
        """Calculate the cost in de current period case call started
        in this period rule

        :type price_rule: :class:`PriceRule`
        :param price_rule: Will be used to calculate the cost
        """
        for day_occurance in self._list_days_in_call_period(
                self.call_start, self.call_end):
            charge_start_period = self._replace_time_in_day_occurence(
                day_occurance, price_rule.start_period
            )
            charge_end_period = self._replace_time_in_day_occurence(
                day_occurance, price_rule.end_period
            )

            if charge_end_period < charge_start_period:
                charge_end_period += timezone.timedelta(days=1)

            period_start_to_tax = self.call_start\
                if self.call_start > charge_start_period\
                else charge_start_period

            period_end_to_tax = self.call_end\
                if self.call_end < charge_end_period\
                else charge_end_period

            if period_start_to_tax < period_end_to_tax:
                period_to_charge = period_end_to_tax - period_start_to_tax
                minutes_period = int(period_to_charge.seconds / 60)

                self.call_price += price_rule.call_charge * minutes_period

    def _list_days_in_call_period(self, start, end):
        """Get the days that was occurred between call period

        :type start: :class:`datetime.time`
        :param start: start period from call

        :type end: :class:`datetime.time`
        :param end: end period from call

        :rtype: list
        :returns: list of days that occurred between start & end of call
        """
        return list(rrule(DAILY, dtstart=start, until=end))

    def _replace_time_in_day_occurence(self, day_occurrence, rule_period):
        """Set the time of rule in a day occurence

        :type day_occurrence: :class:`datetime`
        :param day_occurrence: A :class: `datetime` to apply the time

        :type rule_period: :class:`datetime.time`
        :param rule_period: A :class:`datetime.time` to replace into
                            day_ocurrence

        :rtype: :class:`datetime`
        :returns: day_ocurrence with your time replaced by the rule_period
        """
        return day_occurrence.replace(
            hour=rule_period.hour,
            minute=rule_period.minute,
            second=rule_period.second,
            microsecond=rule_period.microsecond,
        )
