from marshmallow import Schema, fields, ValidationError,  validate
from PIL import Image #pip install Pillow, dependency for products image.
import urllib.request






class ProductCategorySchema(Schema):

    category =  fields.String( validate=[validate.Length(max=100, min=2)])



class ProductSchema(Schema):
    class Meta: ordered = True
    
    id = fields.Int(dump_only = True)
    product_name = fields.String(required=True, validate=[validate.Length(max=100, min=2)])
    product_price = fields.Integer() 
    product_brand = fields.String( validate=[validate.Length(max=100, min=2)])
    product_desc = fields.String(validate=[validate.Length(max=10000, min=1)])
    product_category = fields.Nested(ProductCategorySchema)
    product_image = fields.Method(required=True, deserialize='load_image')

    def load_image(img):
        urllib.request.urlretrieve( 'image url', "alt.png")
        try:
            img  = Image.open(path, "alt.png")
        except IOError:
            print("image cannot be found")
            pass

    



# cat_list = ["Supermarket", "Health & Beauty", "Computing", "Home & Office", "Electronics", "Fashion", "Phones & Tablets", "Baby Products", "Gaming", "Sports", "Other" ] 
  
