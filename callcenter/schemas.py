import coreapi
from rest_framework import schemas
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer


def bill_by_month_schema():
    return schemas.AutoSchema(
        manual_fields=[
            coreapi.Field(
                "phone_number",
                required=True,
                location="path",
                description="The phone number to get the bill"
            ),
            coreapi.Field(
                "month",
                required=False,
                location="query",
                description="The month of the bill",
                type="int"
            ),
            coreapi.Field(
                "year",
                required=False,
                location="query",
                description="The year of the bill",
                type="int"
            ),
        ]
    )


def call_record_create_schema():
    return schemas.ManualSchema(
        fields=[
            coreapi.Field(
                "type",
                required=True,
                location="form",
                description="1 (start type) or 2 (end type)",
                type="integer"
            ),
            coreapi.Field(
                "timestamp",
                required=True,
                location="form",
                description="YYYY-mm-dd HH:MM:SS",
                type="string"
            ),
            coreapi.Field(
                "call_id",
                required=True,
                location="form",
                description="Id of the call",
                type="integer"
            ),
            coreapi.Field(
                "source",
                required=False,
                location="form",
                description="Phone number that initiated the call",
                type="string"
            ),
            coreapi.Field(
                "destination",
                required=False,
                location="form",
                description="Phone number that received the call",
                type="string"
            )
        ]
    )


def price_rule_create_schema():
    return schemas.ManualSchema(
        fields=[
            coreapi.Field(
                "rule_type",
                required=True,
                location="form",
                description="1 (standart rule) or 2 (reduced rule)",
                type="integer"
            ),
            coreapi.Field(
                "fixed_charge"
            ),
            coreapi.Field(
                "call_charge"
            ),
            coreapi.Field(
                "start_period"
            ),
            coreapi.Field(
                "end_period"
            )
        ]
    )


class CustomViewPriceRuleCreateSchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []

        if method == 'POST':
            extra_fields = [
                coreapi.Field(
                    "rule_type",
                    required=True,
                    location="form",
                    description="1 (standart rule) or 2 (reduced rule)",
                    type="integer"
                ),
                coreapi.Field(
                    "fixed_charge",
                    required=True,
                    location="form",
                    description="The price to be charged in call connection",
                    type="number"
                ),
                coreapi.Field(
                    "call_charge",
                    required=True,
                    location="form",
                    description="The price to be charged by call minute",
                    type="number"
                ),
                coreapi.Field(
                    "start_period",
                    required=True,
                    location="form",
                    description="The time period in day that this rule starts."
                                " Format: HH:MM:SS",
                    type="string"
                ),
                coreapi.Field(
                    "end_period",
                    required=True,
                    location="form",
                    description="The time period in day that this rule ends."
                                " Format: HH:MM:SS",
                    type="string"
                )
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields
