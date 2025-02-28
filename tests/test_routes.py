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
TestPromotion API Service Test Suite
"""

# pylint: disable=duplicate-code
from datetime import date
import os
import logging
from unittest import TestCase
import json
import sys
import random
sys.path.append('..')
from wsgi import app
from service.common import status
from service.models import db, Promotion, Category
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


    def _create_promotions(self, count):
        """Helper function to create multiple promotions"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            
            if test_promotion.product_id is None:
                test_promotion.product_id = random.randint(1000, 9999)
            
            response = self.client.post(BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = response.get_json()

            test_promotion.id = new_promotion["id"]
            test_promotion.product_id = new_promotion["product_id"]
            promotions.append(test_promotion)

        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ##-------------------------------------------------------------------##

    def test_create_promotion_success(self):
        """
        Test case to create new promotion.
        """
        # Define the input payload for a valid promotion
        test_promotion = PromotionFactory()
        # Post to the promotions endpoint
        response = self.client.post(BASE_URL, json=test_promotion.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["category"], test_promotion.category.name)
        self.assertEqual(new_promotion["discount_x"], test_promotion.discount_x)
        self.assertEqual(new_promotion["discount_y"], test_promotion.discount_y)
        self.assertEqual(new_promotion["product_id"], test_promotion.product_id)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["validity"], test_promotion.validity)
        self.assertEqual(new_promotion["start_date"], test_promotion.start_date.isoformat())
        self.assertEqual(new_promotion["end_date"], test_promotion.end_date.isoformat())

        # TO BE DONE
        # also needs to check the location header once GET route is created

    ##-------------------------------------------------------------------##
    
    def test_discount_x_validation_create_promotion(self):
        """
        Test case to validate that discount_x can only be an int.
        """
        test_json = PromotionFactory().serialize()
        test_json["discount_x"] = 1.1
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        del test_json["discount_x"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.get_json()["discount_x"], 0)

    ##-------------------------------------------------------------------##
    
    def test_discount_y_validation_create_promotion(self):
        """
        Test case to validate that discount_y can only be an int or None.
        """
        test_json = PromotionFactory().serialize()
        test_json["discount_y"] = 1.1
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        test_json["discount_y"] = None
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["discount_y"], None)

        test_json = PromotionFactory().serialize()
        del test_json["discount_y"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["discount_y"], None)

    ##-------------------------------------------------------------------##
    
    def test_product_id_validation_create_promotion(self):
        """
        Test case to validate that product_id can only be an int.
        """
        test_json = PromotionFactory().serialize()
        test_json["product_id"] = "123"
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        del test_json["product_id"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##-------------------------------------------------------------------##

    def test_validity_validation_create_promotion(self):
        """
        Test case to validate that validity can only be a bool.
        """
        test_json = PromotionFactory().serialize()
        test_json["validity"] = 1
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        del test_json["validity"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["validity"], False)
    ##-------------------------------------------------------------------##

    def test_missing_product_id_create_promotion(self):
        """
        Test case to check missing product_id.
        """
        test_json = PromotionFactory().serialize()
        del test_json["product_id"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##-------------------------------------------------------------------##

    def test_missing_product_description_create_promotion(self):
        """
        Test case to check missing product_description.
        """
        test_json = PromotionFactory().serialize()
        del test_json["description"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    ##-------------------------------------------------------------------##

    def test_date_create_promotion(self):
        """
        Test case to check invalid start_date and end_date
        """
        test_json = PromotionFactory().serialize()
        test_json["start_date"] = "some date"
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        test_json["end_date"] = "some date"
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        test_json["start_date"] = "2025-02-01"
        test_json["end_date"] = "2025-01-01"
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        test_json = PromotionFactory().serialize()
        del test_json["start_date"]
        del test_json["end_date"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["start_date"], date.today().isoformat())
        self.assertEqual(response.get_json()["end_date"], date.today().isoformat())

        test_json = PromotionFactory().serialize()
        del test_json["start_date"]
        test_json["end_date"] = "2025-01-01"
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_a_promotion(self):
        """It should return a Promotion if the promotion_id exists in the database"""
        test_promo = self._create_promotions(1)[0]

        resp = self.client.get(f"{BASE_URL}/{test_promo.id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        data = resp.get_json()

        self.assertEqual(data["name"], test_promo.name)

        self.assertEqual(data["category"], test_promo.category.name)
        self.assertEqual(data["discount_x"], test_promo.discount_x)
        self.assertEqual(data["discount_y"], test_promo.discount_y)
        self.assertEqual(data["product_id"], test_promo.product_id)
        self.assertEqual(data["description"], test_promo.description)
        self.assertEqual(data["validity"], test_promo.validity)
        self.assertEqual(data["start_date"], test_promo.start_date.isoformat())
        self.assertEqual(data["end_date"], test_promo.end_date.isoformat())
    
    def test_get_promotion_not_found(self):
        """It should not Get a promotion thats not found"""
        error_id = 66666
        promotion = PromotionFactory()
        promotion.id = error_id
        response = self.client.get(f"{BASE_URL}/{error_id}", json=promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)