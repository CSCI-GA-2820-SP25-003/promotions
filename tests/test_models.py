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
        self.assertEqual(found_promotion.product_id, promotion.product_id)