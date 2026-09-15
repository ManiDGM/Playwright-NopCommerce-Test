Feature: Admin manufacturer management
  As an admin user
  I want to manage product manufacturers
  So that brand listings stay organized

  Background:
    Given the admin user is logged into the admin panel
    And the admin opens the manufacturer list page

  Scenario 1: View the manufacturer list
    When the admin views the manufacturer list
    Then the manufacturers grid is displayed

  Scenario 2: Search manufacturers by name
    Given a manufacturer exists with a known name
    When the admin searches the manufacturer list by that name
    Then the manufacturer appears in the search results

  Scenario 3: Create a manufacturer with a valid name
    When the admin creates a new manufacturer with a valid name
    Then the manufacturer is visible in the manufacturer list
    And a success notification is shown

  Scenario 4: Reject creating a manufacturer with an empty name
    When the admin attempts to create a manufacturer without a name
    Then a name required validation message is displayed
    And the manufacturer is not created

  Scenario 5: Edit an existing manufacturer name
    Given a manufacturer exists with a known name
    When the admin edits the manufacturer name to a new valid name
    Then the updated manufacturer name appears in the manufacturer list

  Scenario 6: Delete a single manufacturer from the edit page
    Given a manufacturer exists with a known name
    When the admin deletes the manufacturer from the edit page
    Then the manufacturer is no longer listed in the manufacturer list

  Scenario 7: Delete selected manufacturers from the list page
    Given multiple manufacturers exist with known names
    When the admin selects those manufacturers and deletes the selection
    Then the selected manufacturers are no longer listed in the manufacturer list

  Scenario 8: Filter manufacturers by published status
    Given a published manufacturer exists with a known name
    When the admin filters the manufacturer list to published only
    Then the published manufacturer appears in the filtered results
    When the admin filters the manufacturer list to unpublished only
    Then the published manufacturer does not appear in the filtered results
