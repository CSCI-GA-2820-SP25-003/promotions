"""
Models for Promotion

All of the models are stored in this module

Attributes:
category (enum) - category of the promotion
discount_x (integer) - the discount percentage or other numbers associated with the promotion category
discount_y (integer) - the secondary promotion attribute (i.e. buy discount_x get discount_y free)
product_id (integer) - the id of the product associated with the discount
description (string) - description of the promotion
validity (boolean) - whether the promotion is valid/running
start_date (string) - the start date of the sale
end_date (string) - the end date of the sale
"""

from datetime import date
from enum import Enum

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Category(Enum):
    """Enumeration for available Promotion Category"""

    UNKNOWN = 0
    PERCENTAGE_DISCOUNT_X = 1
    BUY_X_GET_Y_FREE = 2
    SPEND_X_SAVE_Y = 3


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(
        db.Enum(Category), nullable=False, server_default=Category.UNKNOWN.name
    )
    discount_x = db.Column(db.Integer(), nullable=False, default=0)
    discount_y = db.Column(db.Integer(), nullable=True, default=None)
    product_id = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    validity = db.Column(db.Boolean(), nullable=False, default=False)
    start_date = db.Column(db.Date(), nullable=False, default=date.today())
    end_date = db.Column(db.Date(), nullable=False, default=date.today())
    # Database auditing fields
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Promotion from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
            "discount_x": self.discount_x,
            "discount_y": self.discount_y,
            "product_id": self.product_id,
            "description": self.description,
            "validity": self.validity,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]

            if "category" in data:
                self.category = Category[data["category"].upper()]

            if "discount_x" in data:
                if isinstance(data["discount_x"], int):
                    self.discount_x = data["discount_x"]
                else:
                    raise DataValidationError(
                        "Invalid type for int [discount_x]: "
                        + str(type(data["discount_x"]))
                    )

            if "discount_y" in data:
                if isinstance(data["discount_y"], int) or data["discount_y"] == None:
                    self.discount_y = data["discount_y"]
                else:
                    raise DataValidationError(
                        "Invalid type for int [discount_y]: "
                        + str(type(data["discount_y"]))
                    )

            if isinstance(data["product_id"], int):
                self.product_id = data["product_id"]
            else:
                raise DataValidationError(
                    "Invalid type for int [product_id]: "
                    + str(type(data["product_id"]))
                )

            self.description = data["description"]

            if "validity" in data:
                if isinstance(data["validity"], bool):
                    self.validity = data["validity"]
                else:
                    raise DataValidationError(
                        "Invalid type for bool [validity]: "
                        + str(type(data["validity"]))
                    )

            if "start_date" in data:
                if isinstance(data["start_date"], str):
                    self.start_date = date.fromisoformat(data["start_date"])
                else:
                    raise DataValidationError(
                        "Invalid type for string [start_date]: "
                        + str(type(data["start_date"]))
                    )

            if "end_date" in data:
                if isinstance(data["end_date"], str):
                    end_date = date.fromisoformat(data["end_date"])
                    if end_date >= self.start_date:
                        self.end_date = end_date
                    else:
                        raise DataValidationError("Invalid end date before start date")
                else:
                    raise DataValidationError(
                        "Invalid type for string [end_date]: "
                        + str(type(data["end_date"]))
                    )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data "
                + str(error)
            ) from error
        except ValueError as error:
            raise DataValidationError(str(error))
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Promotions in the database"""
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Promotion by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
