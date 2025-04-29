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
import random
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Promotion, Category
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/promotions"


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
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
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
        resp = self.client.get("/api")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
        self.assertEqual(
            new_promotion["start_date"], test_promotion.start_date.isoformat()
        )
        self.assertEqual(new_promotion["end_date"], test_promotion.end_date.isoformat())

        # check that the location header is correct
        location = response.headers.get("location", None)
        self.assertIsNotNone(location)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["category"], test_promotion.category.name)
        self.assertEqual(new_promotion["discount_x"], test_promotion.discount_x)
        self.assertEqual(new_promotion["discount_y"], test_promotion.discount_y)
        self.assertEqual(new_promotion["product_id"], test_promotion.product_id)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["validity"], test_promotion.validity)
        self.assertEqual(
            new_promotion["start_date"], test_promotion.start_date.isoformat()
        )
        self.assertEqual(new_promotion["end_date"], test_promotion.end_date.isoformat())

    def test_create_promotion_invalid_header(self):
        """It should fail to create promotion with wrong Content-Type in headers"""
        headers = {"Content-Type": "text/plain"}
        response = self.client.post(BASE_URL, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

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

    def test_missing_product_id_create_promotion(self):
        """
        Test case to check missing product_id.
        """
        test_json = PromotionFactory().serialize()
        del test_json["product_id"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_product_description_create_promotion(self):
        """
        Test case to check missing product_description.
        """
        test_json = PromotionFactory().serialize()
        del test_json["description"]
        response = self.client.post(BASE_URL, json=test_json)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        test_json["start_date"] = "some date"
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

    def test_list_promotions_empty(self):
        """
        Test listing promotions when no promotions exist.
        """
        # Set the content type header as expected by check_content_type
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        list_data = response.get_json()
        # Expect an empty list if no promotions exist in the database
        self.assertEqual(len(list_data), 0)

    def test_list_promotions_with_data(self):
        """
        Test listing promotions after creating one promotion.
        """
        payload_list = [PromotionFactory().serialize() for _ in range(50)]
        for payload in payload_list:
            create_response = self.client.post(BASE_URL, json=payload)
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_response = self.client.get(BASE_URL)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        list_data = list_response.get_json()
        self.assertEqual(len(list_data), 50)

    def test_update_promotion(self):
        """It should Update an existing promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["name"] = "promo1"
        promotion_id = new_promotion["id"]
        response = self.client.put(f"{BASE_URL}/{promotion_id}", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_promotion = response.get_json()
        self.assertEqual(updated_promotion["name"], "promo1")

    def test_update_promotion_invalid_header(self):
        """It should Update an existing promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["name"] = "promo1"
        promotion_id = new_promotion["id"]
        response = self.client.put(f"{BASE_URL}/{promotion_id}")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_invalid_data(self):
        """It should return 400 when trying to update with invalid data"""
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_promotion = response.get_json()
        promotion_id = new_promotion["id"]

        invalid_data = {"name": 123, "discount_x": "invalid_number"}
        response = self.client.put(f"{BASE_URL}/{promotion_id}", json=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_promotion_not_found(self):
        """It should return 404 if trying to update a non-existent promotion"""
        invalid_id = 99999
        test_promotion = PromotionFactory()
        test_promotion.id = invalid_id
        response = self.client.put(
            f"{BASE_URL}/{invalid_id}", json=test_promotion.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------

    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        promotions = self._create_promotions(5)
        test_promotion = promotions[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(BASE_URL)
        self.assertEqual(len(response.get_json()), 4)

    def test_delete_non_existing_promotion(self):
        """It should Delete a Promotion even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_create_invalid_request(self):
        """It should give error when not posting a valid request"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        response = self.client.post(f"{BASE_URL}/123")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_by_name(self):
        """It should Query Promotions by name"""
        promotions = self._create_promotions(5)
        test_name = promotions[0].name
        name_count = len(
            [promotion for promotion in promotions if promotion.name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)

        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_query_by_validity(self):
        """It should Query Promotions by validity"""
        promotions = self._create_promotions(10)
        valid_promotions = [
            promotion for promotion in promotions if promotion.validity is True
        ]
        invalid_promotions = [
            promotion for promotion in promotions if promotion.validity is False
        ]
        valid_count = len(valid_promotions)
        invalid_count = len(invalid_promotions)

        response = self.client.get(BASE_URL, query_string="validity=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), valid_count)
        for promotion in data:
            self.assertEqual(promotion["validity"], True)

        response = self.client.get(BASE_URL, query_string="validity=False")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), invalid_count)
        for promotion in data:
            self.assertEqual(promotion["validity"], False)

    def test_query_by_category(self):
        """It should Query Promotions by category"""
        promotions = self._create_promotions(10)
        percent_promotions = [
            promotion
            for promotion in promotions
            if promotion.category == Category.PERCENTAGE_DISCOUNT_X
        ]
        percent_count = len(percent_promotions)

        response = self.client.get(
            BASE_URL, query_string="category=percentage_discount_x"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), percent_count)
        for promotion in data:
            self.assertEqual(promotion["category"], Category.PERCENTAGE_DISCOUNT_X.name)

    def test_query_by_start_date(self):
        """It should Query Promotions by start_date"""
        promotions = self._create_promotions(10)
        test_date = promotions[0].start_date
        test_iso_date = test_date.isoformat()
        test_promotions = [
            promotion for promotion in promotions if promotion.start_date == test_date
        ]
        test_count = len(test_promotions)
        logging.debug("test_date: %s", test_iso_date)

        response = self.client.get(BASE_URL, query_string=f"start_date={test_iso_date}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), test_count)
        for promotion in data:
            self.assertEqual(promotion["start_date"], test_iso_date)

    def test_query_by_end_date(self):
        """It should Query Promotions by end_date"""
        promotions = self._create_promotions(10)
        test_date = promotions[0].end_date
        test_iso_date = test_date.isoformat()
        test_promotions = [
            promotion for promotion in promotions if promotion.end_date == test_date
        ]
        test_count = len(test_promotions)
        logging.debug("test_date: %s", test_iso_date)

        response = self.client.get(BASE_URL, query_string=f"end_date={test_iso_date}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), test_count)
        for promotion in data:
            self.assertEqual(promotion["end_date"], test_iso_date)

    def test_query_by_product_id(self):
        """It should Query Promotions by product_id"""
        promotions = self._create_promotions(10)
        product_id = promotions[0].product_id
        test_promotions = [
            promotion for promotion in promotions if promotion.product_id == product_id
        ]
        test_count = len(test_promotions)

        response = self.client.get(BASE_URL, query_string=f"product_id={product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), test_count)
        for promotion in data:
            self.assertEqual(promotion["product_id"], product_id)

    def test_validate_promotion(self):
        """It should make the Promotion valid"""
        response = self.client.put(f"{BASE_URL}/123/valid")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        valid_promotion = PromotionFactory()
        valid_promotion.validity = True

        invalid_promotion = PromotionFactory()
        invalid_promotion.validity = False

        valid_location = self.client.post(
            BASE_URL, json=valid_promotion.serialize()
        ).headers.get("location", None)
        invalid_location = self.client.post(
            BASE_URL, json=invalid_promotion.serialize()
        ).headers.get("location", None)

        valid_response = self.client.put(f"{valid_location}/valid")
        invalid_response = self.client.put(f"{invalid_location}/valid")

        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)
        self.assertEqual(invalid_response.status_code, status.HTTP_200_OK)

        self.assertEqual(valid_response.get_json()["validity"], True)
        self.assertEqual(invalid_response.get_json()["validity"], True)

    def test_invalidate_promotion(self):
        """It should make the Promotion invalid"""
        response = self.client.delete(f"{BASE_URL}/123/valid")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        valid_promotion = PromotionFactory()
        valid_promotion.validity = True

        invalid_promotion = PromotionFactory()
        invalid_promotion.validity = False

        valid_location = self.client.post(
            BASE_URL, json=valid_promotion.serialize()
        ).headers.get("location", None)
        invalid_location = self.client.post(
            BASE_URL, json=invalid_promotion.serialize()
        ).headers.get("location", None)

        valid_response = self.client.delete(f"{valid_location}/valid")
        invalid_response = self.client.delete(f"{invalid_location}/valid")

        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)
        self.assertEqual(invalid_response.status_code, status.HTTP_200_OK)

        self.assertEqual(valid_response.get_json()["validity"], False)
        self.assertEqual(invalid_response.get_json()["validity"], False)

    def test_extend_promotion_duration_invalid(self):
        """It should give error when having no payload / wrong json attribute / invalid date"""
        response = self.client.put(f"{BASE_URL}/123/extend")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        payload = {"end_date": "2024-01-01"}
        invalid_payload = {"start_date": "2024-01-01"}
        response = self.client.put(f"{BASE_URL}/123/extend", json=payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = PromotionFactory().serialize()
        data["start_date"] = "2025-01-01"
        data["end_date"] = "2025-04-01"
        location = self.client.post(BASE_URL, json=data).headers.get("location", None)

        response = self.client.put(f"{location}/extend", json=invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(f"{location}/extend", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extend_promotion_duration(self):
        """It should change the end_date of the promotion to the specified date"""
        data = PromotionFactory().serialize()
        data["start_date"] = "2025-01-01"
        data["end_date"] = "2025-04-01"
        location = self.client.post(BASE_URL, json=data).headers.get("location", None)

        payload = {"end_date": "2025-05-01"}
        response = self.client.put(f"{location}/extend", json=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"{location}/extend", json=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST HEALTH CHECK
    # ----------------------------------------------------------

    def test_health_check_endpoint(self):
        """It should return a 200 status with 'status':'OK' in the JSON response."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get("status"), "OK")

    def test_health_check_method_not_allowed(self):
        """It should return 405 Method Not Allowed for unsupported HTTP methods on /health."""
        response = self.client.post("/health")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
