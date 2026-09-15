Feature: Admin category management
  As an admin user
  I want to manage product categories
  So that the catalog hierarchy stays organized

  Background:
    Given the admin user is logged into the admin panel
    And the admin opens the category list page

  Scenario 1: View the category list
    When the admin views the category list
    Then the categories grid is displayed

  Scenario 2: Search categories by name
    Given a category exists with a known name
    When the admin searches the category list by that name
    Then the category appears in the search results

  Scenario 3: Create a category with a valid name
    When the admin creates a new category with a valid name
    Then the category is visible in the category list
    And a success notification is shown

  Scenario 4: Reject creating a category with an empty name
    When the admin attempts to create a category without a name
    Then a name required validation message is displayed
    And the category is not created

  Scenario 5: Edit an existing category name
    Given a category exists with a known name
    When the admin edits the category name to a new valid name
    Then the updated category name appears in the category list

  Scenario 6: Delete a single category from the edit page
    Given a category exists with a known name
    When the admin deletes the category from the edit page
    Then the category is no longer listed in the category list

  Scenario 7: Delete selected categories from the list page
    Given multiple categories exist with known names
    When the admin selects those categories and deletes the selection
    Then the selected categories are no longer listed in the category list

  Scenario 8: Filter categories by published status
    Given a published category exists with a known name
    When the admin filters the category list to published only
    Then the published category appears in the filtered results
    When the admin filters the category list to unpublished only
    Then the published category does not appear in the filtered results