import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * System testing for the whole page.
 * 
 * The test starts with login in on the page with user name 'Playwright'
 * Later navigates to eventlog page to upload an csv file
 * After uploading the csv file navigates to page 'Discovery' and verifies that
 * the newly uploaded even log is in the dropdown menu for event logs.
 */

const __dirname = path.join(process.cwd(), 'tests', 'e2e');

test('Upload event log and verify csv file both in event log page and discovery page', async ({ page }) => {
  await page.goto('http://localhost:5002/');

  const ui5Input = await page.waitForSelector('.username');
  await ui5Input.evaluate((element, value) => {
    const input = element.shadowRoot?.querySelector('input');
    if (input) {
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, 'playwright');
  await page.click('text=Sign in');

  await page.click('[data-route="/eventlogs"]');
  await expect(page).toHaveURL('http://localhost:5002/eventlogs');

  const basePath = path.resolve(__dirname, 'LoanApp.csv');
  const buffer = fs.readFileSync(basePath);
  const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, '');
  const randomName = `LoanApp-${timestamp}.csv`;

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles({
    name: randomName,
    mimeType: 'text/csv',
    buffer,
  });

  await page.waitForTimeout(2000);
  const eventLogHeading = page.getByRole('heading', { name: new RegExp(randomName) });
  await expect(eventLogHeading).toBeVisible();

  const uploadButton = page.getByRole('button', { name: 'Save' });
  await uploadButton.waitFor({ state: 'visible' });
  await uploadButton.click();
  await page.waitForTimeout(5000);

  await page.click('[data-route="/discovery"]');
  await expect(page).toHaveURL('http://localhost:5002/discovery');
  await page.waitForTimeout(2000);

  const select = page.locator('ui5-select').first();
  await expect(select).toBeVisible();
  await select.click();
  await page.waitForTimeout(500);

  const options = page.locator('ui5-option').filter({ hasText: randomName });
  await expect(options).toHaveCount(1);
  await options.first().click();

  await select.evaluate((element: any) => {
    element.dispatchEvent(new CustomEvent('change', {
      detail: { selectedOption: element.selectedOption },
      bubbles: true
    }));
  });

  const selectedText = await select.evaluate((el: any) => el.selectedOption.textContent.trim());
  expect(selectedText).toBe(randomName);

  const valueProp = await select.evaluate((el: any) => el.value);
  expect(valueProp).toBe(randomName);
});
