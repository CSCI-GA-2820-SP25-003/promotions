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

from flask import jsonify, request, url_for, make_response, abort
from flask import current_app as app  # Import Flask application
from service.models import Promotion, Category
from service.common import status  # HTTP Status Codes
from flask import Blueprint, request, jsonify
from service.models import Promotion, DataValidationError
from datetime import datetime, date


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

##----------------------------------------------------------------------------##


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

    # TO BE DONE: also return the location of the newly created promotion once GET promotion is created
    return jsonify(promotion.serialize()), status.HTTP_201_CREATED


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Return all the promotions"""
    # To be done


######################################################################
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

    return make_response("", status.HTTP_204_NO_CONTENT)


# all pass
