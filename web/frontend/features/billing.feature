Feature: As a person who writes code on ScraperWiki
  I want to pay for private scrapers with a credit card
  So that I can have private scrapers easily and using the
  payment method I'm used to.

  Scenario: I can see available plans
    When I visit the pricing page
    Then I should see the "Individual" payment plan
    And I should see the "Small Business" payment plan
    And I should see the "Corporate" payment plan
  
  Scenario: I can choose to purchase the Individual plan
    Given user "test" with password "pass" is logged in
    And the "Self Service Vaults" feature exists
    And I have the "Self Service Vaults" feature enabled
    When I visit the pricing page
    And I click on the "Individual" "Buy now" button
    Then I should be on the payment page
    And I should see "Individual"
    And I should see "$9"
  
  Scenario: I can choose to purchase the Small Business plan
    Given user "test" with password "pass" is logged in
    And the "Self Service Vaults" feature exists
    And I have the "Self Service Vaults" feature enabled
    When I visit the pricing page
    And I click on the "Small Business" "Buy now" button
    Then I should be on the payment page
    And I should see "Small Business"
    And I should see "$29"

  Scenario: I can choose to purchase the Corporate plan
    Given user "test" with password "pass" is logged in
    And the "Self Service Vaults" feature exists
    And I have the "Self Service Vaults" feature enabled
    When I visit the pricing page
    And I click on the "Corporate" "Buy now" button
    Then I should be on the payment page
    And I should see "Corporate"
    And I should see "$299"

  Scenario: I enter invalid payment details
    Given I have chosen the "Individual" plan
    When I enter my contact information
    And I enter "Test Testerson" as the billing name
    And I enter "sdfsdf" as the credit card number
    And I enter "123" as the CVV
    And I enter "06/14" as the expiry month and year
    And I enter the billing address
    And I click "Subscribe"
    Then I should see "Invalid"
    And I should see "$9"

  Scenario: I enter valid payment details
    Given I have chosen the "Individual" plan
    And I have entered my payment details
    When I click "Subscribe"
    Then I should be on the vaults page
    And I should see "Thanks for upgrading your account!"
