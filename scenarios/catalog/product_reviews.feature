Feature: Admin product review management
  As an admin user
  I want to moderate product reviews
  So that storefront feedback stays accurate and appropriate

  Background:
    Given the admin user is logged into the admin panel
    And the admin opens the product reviews list page
    And at least one product review exists (sample data or storefront seed)

  Scenario 1: View the product review list
    When the admin views the product review list
    Then the product reviews grid is displayed
    And approve, disapprove, and delete selected actions are available

  Scenario 2: Search product reviews by text
    Given a product review exists with a known title
    When the admin searches the product review list by that title
    Then the product review appears in the search results

  Scenario 3: Edit Title and ReviewText
    Given a product review exists with a known title
    When the admin edits the review Title and ReviewText to new valid values
    Then the updated title appears in the product review list
    And a success notification is shown

  Scenario 4: Reject saving a review with an empty Title
    Given a product review exists with a known title
    When the admin opens the review for edit and clears the Title
    And the admin attempts to save the review
    Then a Title required validation message is displayed
    And the review remains on the edit page

  Scenario 5: Reject saving a review with empty ReviewText
    Given a product review exists with a known title
    When the admin opens the review for edit and clears the ReviewText
    And the admin attempts to save the review
    Then a ReviewText required validation message is displayed
    And the review remains on the edit page

  Scenario 6: Approve selected product reviews
    Given a disapproved product review exists with a known title
    When the admin selects that review and chooses approve selected
    Then the review is approved in the product review list

  Scenario 7: Disapprove selected product reviews
    Given an approved product review exists with a known title
    When the admin selects that review and chooses disapprove selected
    Then the review is disapproved in the product review list

  Scenario 8: Delete selected product reviews
    Given a product review exists that was seeded for deletion
    When the admin selects that review and deletes the selection
    Then the review is no longer listed in the product review list
