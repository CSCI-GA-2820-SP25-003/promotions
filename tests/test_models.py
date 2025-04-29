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
Test cases for promotion Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Promotion, DataValidationError, db
from service.common import status
from .factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Promotion   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotion(TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_promotion(self):
        """It should create a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertIsNotNone(promotion.id)
        found = Promotion.all()
        self.assertEqual(len(found), 1)
        data = Promotion.find(promotion.id)
        self.assertEqual(data.name, promotion.name)
        self.assertEqual(data.category, promotion.category)
        self.assertEqual(data.discount_x, promotion.discount_x)
        self.assertEqual(data.discount_y, promotion.discount_y)
        self.assertEqual(data.product_id, promotion.product_id)
        self.assertEqual(data.description, promotion.description)
        self.assertEqual(data.validity, promotion.validity)
        self.assertEqual(data.start_date, promotion.start_date)
        self.assertEqual(data.end_date, promotion.end_date)

    def test_create_promotion_invalid(self):
        """It should give error when trying to create invalid Promotion"""
        promotion = PromotionFactory()
        promotion.discount_x = "something"
        with self.assertRaises(DataValidationError):
            promotion.create()

    def test_update_promotion(self):
        """It should Update a promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)
        # Change it an save it
        promotion.name = "prom1"
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.name, "prom1")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        updated_promo = Promotion.find(original_id)
        self.assertEqual(updated_promo.name, "prom1")

    def test_update_no_id(self):
        """It should not Update a promotion with no id"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_no_id(self):
        """It should not delete anything without valid input"""
        promotion = PromotionFactory()
        with self.assertRaises(DataValidationError):
            promotion.delete()

    def test_read_a_promotion(self):
        """It should Read a promotion"""
        promotion = PromotionFactory()
        promotion.create()
        promo_id = promotion.id
        self.assertEqual(len(Promotion.all()), 1)

        # Fetch it back
        found_promotion = promotion.find(promo_id)
        self.assertIsNotNone(found_promotion)
        self.assertEqual(found_promotion.id, promo_id)
        self.assertEqual(found_promotion.name, promotion.name)
        self.assertEqual(found_promotion.category, promotion.category)
        self.assertEqual(found_promotion.discount_x, promotion.discount_x)
        self.assertEqual(found_promotion.discount_y, promotion.discount_y)
        self.assertEqual(found_promotion.product_id, promotion.product_id)
        self.assertEqual(found_promotion.description, promotion.description)
        self.assertEqual(found_promotion.validity, promotion.validity)
        self.assertEqual(found_promotion.start_date, promotion.start_date)
        self.assertEqual(found_promotion.end_date, promotion.end_date)

    def test_list_all(self):
        """It should list all Promotion"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])

        for _ in range(5):
            PromotionFactory().create()

        promotions = Promotion.all()
        self.assertEqual(len(promotions), 5)

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/api")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Promotion REST API Service")

    def test_find_promotion_name(self):
        """IT should find the promotion with the corresponding name"""
        promotion = PromotionFactory()
        promotion.create()

        data = Promotion.find_by_name(promotion.name)
        self.assertEqual(data.count(), 1)
        self.assertEqual(data.first().id, promotion.id)

    def test_find_promotion_validity(self):
        """It should find the promotions with the corresponding validity"""
        promotion = PromotionFactory()
        promotion.validity = True
        promotion.create()

        data = Promotion.find_by_validity(True)
        self.assertEqual(data.count(), 1)
        self.assertEqual(data.first().id, promotion.id)

        self.assertEqual(Promotion.find_by_validity(False).count(), 0)

        for _ in range(10):
            promotion = PromotionFactory()
            promotion.validity = True
            promotion.create()

        for _ in range(10):
            promotion = PromotionFactory()
            promotion.validity = False
            promotion.create()

        data = Promotion.find_by_validity(True)
        self.assertEqual(data.count(), 11)

        data = Promotion.find_by_validity(False)
        self.assertEqual(data.count(), 10)

    def test_find_promotion_category(self):
        """It should find the promotions with the corresponding category"""
        promotion = PromotionFactory()
        test_category = promotion.category
        promotion.create()

        data = Promotion.find_by_category(test_category)
        self.assertEqual(data.count(), 1)
        self.assertEqual(data.first().category, test_category)

    def test_find_promotion_type_error(self):
        """It should raise TypeError when querying with invalid types"""
        with self.assertRaises(TypeError):
            Promotion.find_by_validity("something")

        with self.assertRaises(TypeError):
            Promotion.find_by_category("something")

        with self.assertRaises(TypeError):
            Promotion.find_by_start_date("something")

        with self.assertRaises(TypeError):
            Promotion.find_by_end_date("something")

        with self.assertRaises(TypeError):
            Promotion.find_by_product_id("something")
