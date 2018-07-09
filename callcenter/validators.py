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
        call_data = kwargs['call_data']
        if call_data['type'] == 2:
            return self.__existent_pair_record(call_data['call_id'])

        return False

    def __existent_pair_record(self, call_id):
        if CallRecord.objects.filter(
            call_id=call_id
        ).count() > 1:

            return True

        return False

    def prepare_bill_data(self, call_record_data):
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
        if month and year:
            self.__make_validation(int(month), int(year))
        else:
            self.__get_previous_month()

        return {
            'month': self.month,
            'year': self.year
        }

    def __make_validation(self, month, year):
        if (year > 9999 or month > 12)\
                or (year < 0 or month < 1):
            raise InvalidBillDate("Insert a valid date")

        if year > self.actual_date.year:
            raise InvalidBillDate("Year requested is bigger than actual")

        if (year == self.actual_date.year and month == self.actual_date.month)\
                or (year == self.actual_date.year
                    and self.actual_date.month == 1):
            raise InvalidBillDate("The bill to this month isn't closed yet")

        self.month = month
        self.year = year

    def __get_previous_month(self):
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
        self.call_start = CallRecord.objects.get(
            call_id=call_id, type=START_TYPE
        ).timestamp

        self.call_end = CallRecord.objects.get(
            call_id=call_id, type=END_TYPE
        ).timestamp

        cost = self.__generate_call_cost()

        return cost

    def __generate_call_cost(self):
        price_rules = PriceRule.objects.all()

        for price_rule in price_rules:
            start_in_range = self.__start_in_charge_period(
                price_rule.start_period,
                price_rule.end_period,
                self.call_start.time()
            )

            if start_in_range:
                self.__set_fixed_charge(price_rule.fixed_charge)

            self.__calculate_price_by_period(price_rule)

        full_cost = self.call_price + self.fixed_charge

        return full_cost

    def __start_in_charge_period(self, start_period, end_period, call_start):
        if start_period <= end_period:
            if start_period <= call_start:
                return call_start <= end_period

        return start_period <= call_start or call_start <= end_period

    def __set_fixed_charge(self, fixed_charge):
        """
        Set fixed charge if aren't setted
        """
        if not self.fixed_charge:
            self.fixed_charge = fixed_charge

    def __calculate_price_by_period(self, price_rule):
        """
        Calculate the cost in de current period case call started
        in this period rule
        """
        for day_occurance in self.__list_days_in_call_period(
                self.call_start, self.call_end):
            charge_start_period = self.__replace_time_in_day_occurence(
                day_occurance, price_rule.start_period
            )
            charge_end_period = self.__replace_time_in_day_occurence(
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

    def __list_days_in_call_period(self, start, end):
        """
        Return a list of days that was occurred in start and end period
        """
        return list(rrule(DAILY, dtstart=start, until=end))

    def __replace_time_in_day_occurence(self, day_occurence, rule_period):
        """
        Set the time of rule in a day occurence
        """
        return day_occurence.replace(
            hour=rule_period.hour,
            minute=rule_period.minute,
            second=rule_period.second,
            microsecond=rule_period.microsecond,
        )
