from behave import when, then
from selenium.webdriver.common.by import By

ID_PREFIX = 'promotion_'


@when('I visit the "Home Page"')
def step_visit_home_page(context):
    """Make a call to the base URL."""
    context.driver.get(context.BASE_URL)


@then('I should see "{message}" in the title')
def step_check_title_contains(context, message):
    """Check the document title for a specified message."""
    assert message in context.driver.title, f'"{message}" not in page title: {context.driver.title}'


@then('I should not see "{text_string}"')
def step_check_no_error_text(context, text_string):
    """Ensure that the specified text is not present in the page body."""
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    assert text_string not in element.text, error_msg
