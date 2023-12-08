import io
import json
import zipfile
import threading

from validate_dns_email import EmailDNSValidator
from flask import Blueprint, request, Response, send_file
from flask_cors import cross_origin

from src.utils import x_api_key_required
from src.interfaces import APIView
from src.models import Email, ExcelReader, ExcelWriter


api_blueprint = Blueprint('api', __name__)


class ValidateEmail(APIView):
    parameters =[
        {
            'in': 'header',
            'name': 'x-api-key',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        },
        {
            'in': 'header',
            'name': 'Authorization',
            'type': 'string',
            'required': True,
            'description': 'Access token for authentication'
        },
        {
            'in': 'query',
            'name': 'verify',
            'type': 'boolean',
            'required': False,
            'description': 'Verify email domain exist',
        },
        {
            'in': 'query',
            'name': 'email_protected',
            'type': 'boolean',
            'required': False,
            'description': 'If email domain is protected',
        },
        {
            "in": "body",
            "name": "email",
            "description": "Email to validate",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "user@example.com"
                    },
                }
            }
        },
    ]
    responses = {
        200: {
            "description": "Validate email address",
            "schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "boolean",
                        "description": "Email is required",
                    }
                }
            }
        },
        400: {
            "description": "Email address is required",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Email is required",
                    }
                }
            }
        },
    }

    @x_api_key_required
    @cross_origin(supports_credentials=True)
    def post(self):

        if (request.content_length == 0):
            return Response(json.dumps({"message": "email is required"}), mimetype='application/json', status=400)

        body = request.json

        email = Email.create_email(body['email'])
        email_validator = EmailDNSValidator(email.get_value().lower())

        try:
            is_validated = email_validator.validate_email(verify=True, email_protected=True)
        except:
            is_validated = False

        response = {"results": is_validated}

        return Response(json.dumps(response), mimetype='application/json', status=200)


class ValidateEmailFileView(APIView):
    parameters =[
        {
            'in': 'header',
            'name': 'x-api-key',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        },
        {
            'in': 'header',
            'name': 'Authorization',
            'type': 'string',
            'required': True,
            'description': 'Access token for authentication'
        },
        {
            'in': 'query',
            'name': 'verify',
            'type': 'boolean',
            'required': False,
            'description': 'Verify email domain exist',
        },
        {
            'in': 'query',
            'name': 'email_protected',
            'type': 'boolean',
            'required': False,
            'description': 'If email domain is protected',
        },
        {
            "in": "body",
            "name": "email",
            "description": "Email to validate",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "user@example.com"
                    },
                }
            }
        },
    ]
    responses = {
        200: {
            "description": "Validate email address",
            "schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "boolean",
                        "description": "Email is required",
                    }
                }
            }
        },
        400: {
            "description": "Email address is required",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Email is required",
                    }
                }
            }
        },
    }

    @x_api_key_required
    @cross_origin(supports_credentials=True)
    def post(self):

        if "excel" not in request.files:
            return Response(json.dumps({"message": "excel file is required"}), mimetype='application/json', status=404)

        file = request.files["excel"]
        excel_reader = ExcelReader(file=file)

        if not excel_reader.is_header_valid():
            return Response(json.dumps({"message": "Missing email header in excel"}), mimetype='application/json', status=404)

        excel_writer = ExcelWriter(excel_reader.data)
        df = excel_reader.data

        chunks = [df[i:i+200] for i in range(0, len(df), 200)]
        threads = []

        try:
            for chunk in chunks:
                thread = threading.Thread(
                    target=self.validate_emails,
                    args=(
                        chunk,
                        excel_writer.valid_emails,
                        excel_writer.invalid_emails
                    )
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            df_valid = excel_writer.make_dataframe(excel_writer.valid_emails)
            df_invalid = excel_writer.make_dataframe(excel_writer.invalid_emails)

            excel_writer.make_excel(excel_writer.valid_excel_file, df_valid)
            excel_writer.make_excel(excel_writer.invalid_excel_file, df_invalid)

            zip_buffer = io.BytesIO()
            excel_writer.set_seeks()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                zip_file.writestr('Email validated.xlsx', excel_writer.valid_excel_file.read())
                zip_file.writestr('Email rejected.xlsx', excel_writer.invalid_excel_file.read())
            zip_buffer.seek(0)

            return send_file(zip_buffer, as_attachment=True, mimetype="application/zip", download_name="BASE DE DATOS BOGOTÁ PARA CORREO.zip")

        except Exception as error:
            return Response(json.dumps({"message": str(error)}), mimetype='application/json', status=500)


    def validate_emails(self, data, valid, invalid):
        valid_emails = []
        invalid_emails = []
        for i, email in enumerate(data['email']):
            try:
                email_validator = EmailDNSValidator(email.lower())
                is_validated = email_validator.validate_email(verify=True, email_protected=True)
                if isinstance(is_validated, bool) and is_validated:
                    valid_emails.append({"email": email})
                else:
                    invalid_emails.append({"email": email})
            except:
                invalid_emails.append({"email": email})

        valid.extend(valid_emails)
        invalid.extend(invalid_emails)

# adding routes
api_blueprint.add_url_rule(
    '/api/v1/email/validate/file/',
    view_func=ValidateEmailFileView.as_view('email_validate_file_view'),
    methods=["POST"]
)

api_blueprint.add_url_rule(
    '/api/v1/email/validate/email/',
    view_func=ValidateEmail.as_view('email_validate_email_view'),
    methods=["POST"]
)
