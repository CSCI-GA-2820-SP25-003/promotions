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

"""
Promotion Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Promotion
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Promotion
from service.common import status  # HTTP Status Codes

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Promotion REST API Service",
            version="1.0",
            paths=url_for("list_promotions", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    POST API to create a new promotion.
    Product ID and Promotion Description have to be present, the rest of them have default values.
    """
    app.logger.info("Request to Create a Promotion...")
    check_content_type("application/json")

    promotion = Promotion()
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    promotion.deserialize(data)

    promotion.create()
    app.logger.info("Promotion with new id [%s] saved", promotion.id)

    location_url = url_for("get_promotions", promotion_id=promotion.id, _external=True)
    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


# ----------------------
#    READ A PROMOTION
# ----------------------
@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotions(promotion_id):
    """GET API to read a promotion"""
    app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)

    # Attempt to find the promotion and abort if not found
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"promotion with id '{promotion_id}' was not found.",
        )

    app.logger.info("Returning promotion: %s", promotion.name)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """
    GET API to list all promotions.
    """
    app.logger.info("Request to List all Promotions...")

    all_promotions = Promotion.all()
    promotion_list = [promo.serialize() for promo in all_promotions]

    return jsonify(promotion_list), status.HTTP_200_OK


@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotions(promotion_id):
    """
    Update a promotion

    This endpoint will update a promotion based the body that is posted
    """
    app.logger.info("Request to Update a promotion with id [%s]", promotion_id)
    check_content_type("application/json")

    # Attempt to find the promotion and abort if not found
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"promotion with id '{promotion_id}' was not found.",
        )

    # Update the promotion with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    promotion.deserialize(data)

    # Save the updates to the database
    promotion.update()

    app.logger.info("promotion with ID: %d updated.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


#####################################################################
# Checks the ContentType of a request
######################################################################


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Delete a Promotion
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotions(promotion_id):
    """
    Delete a Promotion

    This endpoint will delete a Promotion based the id specified in the path
    """
    app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)
    promotion = Promotion()
    promotion = Promotion.find(promotion_id)

    if promotion:
        promotion.delete()

    return {}, status.HTTP_204_NO_CONTENT
