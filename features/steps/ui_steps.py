from selenium.webdriver.common.by import By
from behave import when, then


@when('I visit the "home page"')
def visit_home_page(context):
    """ vist homepage """
    context.driver.get(context.BASE_URL + "/")


@then('I should see "{text}" in the title')
def check_title_contains_text(context, text):
    """ The page title should contain certain text """
    assert text in context.driver.title, f'"{text}" not found in page title: {context.driver.title}'


@then('I should not see "{text_string}"')
def check_body_does_not_contain(context, text_string):
    body = context.driver.find_element(By.TAG_NAME, 'body')
    assert text_string not in body.text, f'I should not see "{text_string}" in "{body.text}"'
