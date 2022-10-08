from marshmallow import Schema, fields, ValidationError,  validate
from werkzeug.security import generate_password_hash
from utils.utilities import password_strength

class CustomerSchema(Schema):
    class Meta: ordered = True
    
    id = fields.Int(dump_only = True)
    firstname = fields.String(validate=[validate.Length(max=100, min=2)])
    lastname = fields.String(validate=[validate.Length(max=100, min=2)])
    phone = fields.String(validate=[validate.Length(max=15, min=2)])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    country = fields.String(validate=[validate.Length(max=100, min=2)])
    state = fields.String(validate=[validate.Length(max=100, min=2)])
    zipcode = fields.Integer()
    city = fields.String(validate=[validate.Length(max=100)])
    street_name = fields.String(validate=[validate.Length(max=100, min=2)])
    username = fields.String(required=True, validate=[validate.Length(max=100)])
    email = fields.Email(required=True)
    password = fields.Method(required=True, deserialize='load_password')
    
    def load_password(self, password):
        if password_strength(password) == True:
            return generate_password_hash(password)