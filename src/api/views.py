import io
import json
import zipfile

from validate_dns_email import EmailDNSValidator
from flask import Blueprint, request, current_app, Response, send_file
from flask_cors import cross_origin

from src.utils import x_api_key_required
from src.interfaces import APIView
from src.models import Email, ExcelReader, ExcelWriter


api_blueprint = Blueprint('api', __name__)

class ValidateEmailView(APIView):
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
        for email in excel_reader.data['email']:
            try:
                email_validator = EmailDNSValidator(email.lower())
                is_validated = email_validator.validate_email(verify=True, email_protected=True)
                if isinstance(is_validated, bool) and is_validated:
                    excel_writer.add_valid_email({"email": email})
                else:
                    excel_writer.add_invalid_email({"email": email})
            except:
                excel_writer.add_invalid_email({"email": email})
                continue

        df_valid = excel_writer.make_dataframe(excel_writer.valid_emails)
        df_invalid = excel_writer.make_dataframe(excel_writer.invalid_emails)

        excel_writer.make_excel(excel_writer.valid_excel_file, df_valid)
        excel_writer.make_excel(excel_writer.invalid_excel_file, df_invalid)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('archivo1.xlsx', excel_writer.valid_excel_file.read())
            zip_file.writestr('archivo2.xlsx', excel_writer.invalid_excel_file.read())
        zip_buffer.seek(0)

        return send_file(zip_buffer, as_attachment=True, mimetype="application/zip", download_name="BASE DE DATOS BOGOTÁ PARA CORREO.zip")


# adding routes
api_blueprint.add_url_rule(
    '/api/v1/validate/email/',
    view_func=ValidateEmailView.as_view('validate_email_view'),
    methods=["POST"]
)
