Feature: The promotion service back-end
    As a Promotion developer
    I need a RESTful catalog service
    So that I can keep track of all my promotions


Background:
    Given the following promotions
        | name      | category              | discount_x | discount_y | product_id | description               | validity | start_date  | end_date    |
        | Summer50  | PERCENTAGE_DISCOUNT_X |    50      |            |     1001      | Summer half-off sale   | true     | 2025-02-01  | 2025-06-01  |
        | BOGO Deal | BUY_X_GET_Y_FREE      |     1      |      1     |     2000      | Buy one get one free   | true     | 2025-04-01  | 2025-12-31  |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion REST API Service" in the title
    And I should not see "404 Not Found"
