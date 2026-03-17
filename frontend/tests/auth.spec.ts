import { test, expect } from '@playwright/test';

test.describe('Aion Tutor Auth Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the root login page
    await page.goto('http://localhost:3000');
  });

  test('Guest Access button works and redirects to onboarding', async ({ page }) => {
    // Find Guest Access button and click it
    const guestButton = page.getByRole('button', { name: /Guest Access/i });
    await expect(guestButton).toBeVisible();
    await guestButton.click();

    // Verify redirect to /onboarding
    await expect(page).toHaveURL(/.*onboarding/);
    await expect(page.getByText(/Personalize your learning journey/i)).toBeVisible();
  });

  test('Sign In and Create Account buttons have different colors', async ({ page }) => {
    const primaryButton = page.locator('button[type="submit"]');

    // Default state: Sign In (Blue)
    await expect(primaryButton).toHaveText(/Sign In/i);
    await expect(primaryButton).toHaveClass(/bg-blue-600/);

    // Toggle to Create Account
    await page.getByRole('button', { name: /New here\? Create an account/i }).click();

    // Now should be Create Account (Teal)
    await expect(primaryButton).toHaveText(/Create Account/i);
    await expect(primaryButton).toHaveClass(/bg-teal-600/);
  });

  test('Handles invalid login credentials with a clear error', async ({ page }) => {
    await page.getByPlaceholder('name@example.com').fill('wrong@example.com');
    await page.getByPlaceholder('Password').fill('notthepassword');
    await page.getByRole('button', { name: /Sign In/i, exact: true }).click();

    // Check for our custom error message mapping
    await expect(page.getByText(/Invalid email or password/i)).toBeVisible();
  });
});
