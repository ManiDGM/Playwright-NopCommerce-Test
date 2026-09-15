Feature: Admin product management
  As an admin user
  I want to manage catalog products
  So that the product catalog stays accurate

  Background:
    Given the admin user is logged into the admin panel
    And the admin opens the product list page

  Scenario 1: View the product list
    When the admin views the product list
    Then the products grid is displayed

  Scenario 2: Search products by name
    Given a product exists with a known name
    When the admin searches the product list by that name
    Then the product appears in the search results

  Scenario 3: Create a product with a valid name
    When the admin creates a new product with a valid name
    Then the product is visible in the product list
    And a success notification is shown

  Scenario 4: Reject creating a product with an empty name
    When the admin attempts to create a product without a name
    Then a name required validation message is displayed
    And the product is not created

  Scenario 5: Edit an existing product name
    Given a product exists with a known name
    When the admin edits the product name to a new valid name
    Then the updated product name appears in the product list

  Scenario 6: Delete a single product from the edit page
    Given a product exists with a known name
    When the admin deletes the product from the edit page
    Then the product is no longer listed in the product list

  Scenario 7: Delete selected products from the list page
    Given multiple products exist with known names
    When the admin selects those products and deletes the selection
    Then the selected products are no longer listed in the product list

  Scenario 8: Go to a product by SKU from the list page
    Given a product exists with a known SKU
    When the admin goes directly to that SKU from the product list
    Then the product edit page for that product is displayed
