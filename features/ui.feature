Feature: The promotion service back-end
    As a Promotion admin
    I need a RESTful catalog service
    So that I can keep track of all my promotions


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion REST API Service" in the title
    And I should not see "404 Not Found"
