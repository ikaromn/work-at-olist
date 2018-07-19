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
