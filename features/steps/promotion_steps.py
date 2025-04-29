from behave import given
import requests


@given('the following promotions')
def step_impl(context):
    """Clear DB and create new promotions via API"""
    url = f"{context.BASE_URL}/promotions"
    response = requests.get(url)
    try:
        promotions = response.json()
        assert isinstance(promotions, list), "Expected a list of promotions"
    except Exception as e:
        raise AssertionError(f"Failed to parse JSON response: {e}\n{response.text}")

    # delete existing promotions
    for promo in promotions:
        if isinstance(promo, dict) and 'id' in promo:
            requests.delete(f"{url}/{promo['id']}")

    # load the database with new promotions
    for row in context.table:
        payload = {
            "name": row["name"],
            "category": row["category"],
            "discount_x": int(row["discount_x"]),
            "discount_y": int(row["discount_y"]) if row["discount_y"] else None,
            "product_id": int(row["product_id"]),
            "description": row["description"],
            "validity": row["validity"].lower() == "true",
            "start_date": row["start_date"],
            "end_date": row["end_date"]
        }
        resp = requests.post(url, json=payload)
        assert resp.status_code == 201, f"Failed to create promotion: {resp.text}"