######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore restx
"""
Promotion Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Promotion
"""

from functools import wraps
from datetime import datetime, date
from flask import current_app as app  # Import Flask application
from flask import request
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Promotion, Category
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Promotion REST API Service",
    description="This is a promotion microservice server.",
    default="promotions",
    default_label="Promotion operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def frontend_index():
    return app.send_static_file("index.html")


@app.route("/api")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        {
            "name": "Promotion REST API Service",
            "version": "1.0",
            "paths": api.url_for(PromotionCollection, _external=True),
        },
        status.HTTP_200_OK,
    )


######################################################################
# Health Check
######################################################################
@app.route("/health")
def health():
    """Health Checkpoint"""
    app.logger.info("Request for Health Check")
    return ({"status": "OK"}, status.HTTP_200_OK)


create_model = api.model(
    "Promotion",
    {
        "name": fields.String(required=True, description="The name of the Promotion"),
        "category": fields.String(
            required=False,
            description="The category of the Promotion (e.g. Percent discount, Buy X get Y free, Spend X save Y)",
        ),
        "discount_x": fields.Integer(
            required=False, description="Parameter X of the discount type"
        ),
        "discount_y": fields.Integer(
            required=False, description="Parameter Y of the discount type"
        ),
        "product_id": fields.Integer(
            required=True, description="ID of the corresponding product"
        ),
        "description": fields.String(
            required=True, description="Description of the Promotion"
        ),
        "validity": fields.Boolean(
            required=False, description="Whether the promotion is currently valid"
        ),
        "start_date": fields.String(
            required=False, description="The start date of the Promotion"
        ),
        "end_date": fields.String(
            required=False, description="The end date of the Promotion"
        ),
    },
)

# Promotion model
promotion_model = api.inherit(
    "PromotionModel",
    create_model,
    {
        "id": fields.String(
            readyOnly=True, description="The unique id assigned internally by service"
        )
    },
)

extend_model = api.model(
    "ExtendModel",
    {
        "end_date": fields.String(
            required=True, description="The new end date for the Promotion"
        )
    },
)

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument(
    "name", type=str, location="args", required=False, help="List Promotions by name"
)
promotion_args.add_argument(
    "category",
    type=str,
    location="args",
    required=False,
    help="List Promotions by Category",
)
promotion_args.add_argument(
    "validity",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Promotions by validity",
)
promotion_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="List Promotions by product id",
)
promotion_args.add_argument(
    "start_date",
    type=str,
    location="args",
    required=False,
    help="List Promotions by start date",
)
promotion_args.add_argument(
    "end_date",
    type=str,
    location="args",
    required=False,
    help="List Promotions by end date",
)


######################################################################
# Content-Type Decorator
######################################################################
def expect_content_type(expected_type="application/json"):
    """Decorator to check for expected content-type"""

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if request.content_type != expected_type:
                abort(415, f"Content-Type must be {expected_type}")
            return func(*args, **kwargs)

        return decorated

    return decorator


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route("/promotions/<promotion_id>")
@api.param("promotion_id", "The Promotion identifier")
class PromotionResource(Resource):
    """
    PromotionResource class
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("get_promotions")
    @api.response(404, "Promotion not found")
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve and single promotion
        """
        app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc("update_promotions")
    @api.response(404, "Promotion not found")
    @api.response(400, "The posted Promotion data was not valid")
    @api.response(415, "Content-Type must be application/json")
    @api.expect(promotion_model)
    @expect_content_type()
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion
        """
        app.logger.info("Request to Update a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        promotion.deserialize(data)
        promotion.id = promotion_id
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A Promotion
    # ------------------------------------------------------------------
    @api.doc("delete_promotions")
    @api.response(204, "Promotion deleted")
    def delete(self, promotion_id):
        """
        Delete a Promotion
        """
        app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info("Promotion with id [%s] was deleted", promotion_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route("/promotions", strict_slashes=False)
class PromotionCollection(Resource):
    """Handles all interactions with collection of Promotions"""

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc("list_promotions")
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the Promotions"""
        app.logger.info("Request to list Promotions...")
        promotions = []
        args = promotion_args.parse_args()
        if args["name"]:
            app.logger.info("find by name: %s", args["name"])
            promotions = Promotion.find_by_name(args["name"])
        elif args["validity"] is not None:
            app.logger.info("find by validity: %s", args["validity"])
            promotions = Promotion.find_by_validity(args["validity"])
        elif args["category"]:
            app.logger.info("find by category: %s", args["category"])
            promotions = Promotion.find_by_category(Category[args["category"].upper()])
        elif args["start_date"]:
            app.logger.info("find by start_date: %s", args["start_date"])
            start_date = datetime.fromisoformat(args["start_date"])
            promotions = Promotion.find_by_start_date(start_date)
        elif args["end_date"]:
            app.logger.info("find by end_date: %s", args["end_date"])
            end_date = datetime.fromisoformat(args["end_date"])
            promotions = Promotion.find_by_end_date(end_date)
        elif args["product_id"]:
            app.logger.info("find by product_id: %d", args["product_id"])
            promotions = Promotion.find_by_product_id(int(args["product_id"]))
        else:
            promotions = Promotion.all()

        results = [promotion.serialize() for promotion in promotions]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc("create_promotions")
    @expect_content_type()
    @api.expect(promotion_model)
    @api.response(400, "The posted data was not valid")
    @api.response(415, "Content-Type must be application/json")
    @api.marshal_with(promotion_model)
    def post(self):
        """Creates a Promotion"""
        app.logger.info("Request to Create a Promotion")
        promotion = Promotion()
        app.logger.debug("Payload = %s", api.payload)
        promotion.deserialize(api.payload)
        promotion.create()
        app.logger.info("Promotion with new id [%s] created!", promotion.id)
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True
        )
        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {"location": location_url},
        )


######################################################################
#  PATH: /promotions/{id}/valid
######################################################################
@api.route("/promotions/<promotion_id>/valid")
@api.param("promotion_id", "The promotion identifier")
class ValidateResource(Resource):
    """Action to make promotion valid/invalid"""

    @api.doc("validate_promotions")
    @api.response(404, "Promotion not found")
    def put(self, promotion_id):
        """Make a Promotion valid"""
        app.logger.info("Request to make Promotion valid")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        promotion.validity = True
        promotion.update()
        app.logger.info("Promotion with id [%s] has been make valid", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    @api.doc("invalidate_promotions")
    @api.response(404, "Promotion not found")
    def delete(self, promotion_id):
        """Make a Promotion invalid"""
        app.logger.info("Request ot make Promotion invalid")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        promotion.validity = False
        promotion.update()
        app.logger.info("Promotion with id [%s] has been make invalid", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /promotions/{id}/extend
######################################################################
@api.route("/promotions/<promotion_id>/extend")
@api.param("promotion_id", "The promotion identifier")
class ExtendResource(Resource):
    """Action to change the end_date of a Promotion"""

    @api.doc("extend_promotions")
    @api.response(400, "The posted data was not valid")
    @api.response(404, "Promotion not found")
    @api.response(415, "Content-Type must be application/json")
    @api.expect(extend_model, validate=True)
    @expect_content_type()
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """Change the end_date of a Promotion"""
        app.logger.info("Request to change the end_date of promotion")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"promotion with id '{promotion_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        end_date = date.fromisoformat(data.get("end_date"))

        if end_date < promotion.start_date:
            abort(status.HTTP_400_BAD_REQUEST, "New end date is before start date")
        promotion.end_date = end_date
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
