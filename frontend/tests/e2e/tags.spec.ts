/**
 * E2E Tests for Task Tags Feature (T031, T032)
 *
 * TODO: Set up E2E testing infrastructure before running these tests:
 * 1. Install Playwright:
 *    npm install --save-dev @playwright/test
 * 2. Initialize Playwright:
 *    npx playwright install
 * 3. Create playwright.config.ts
 * 4. Add test script to package.json: "test:e2e": "playwright test"
 *
 * Test Coverage:
 * T031 - Create task with tags:
 * - Navigate to create task page
 * - Fill in task title
 * - Add tags using input + Enter
 * - Add tags using autocomplete
 * - Verify max 10 tags validation
 * - Submit form
 * - Verify task is created with tags
 * - Verify tags are displayed on task card
 *
 * T032 - Edit task tags:
 * - Navigate to edit task page
 * - Verify existing tags are displayed
 * - Add new tags
 * - Remove existing tags
 * - Save changes
 * - Verify tags are updated
 */

/*
import { test, expect, Page } from '@playwright/test';

// Helper function to log in before each test
async function login(page: Page) {
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/tasks');
}

// Helper function to create a task via UI
async function createTask(
  page: Page,
  title: string,
  options: {
    description?: string;
    priority?: 'low' | 'medium' | 'high';
    dueDate?: string;
    tags?: string[];
  } = {}
) {
  await page.goto('http://localhost:3000/tasks/new');

  // Fill in title
  await page.fill('input[name="title"]', title);

  // Fill in optional fields
  if (options.description) {
    await page.fill('textarea[name="description"]', options.description);
  }

  if (options.priority) {
    await page.selectOption('select[name="priority"]', options.priority);
  }

  if (options.dueDate) {
    await page.fill('input[name="due_date"]', options.dueDate);
  }

  // Add tags
  if (options.tags && options.tags.length > 0) {
    const tagInput = page.getByPlaceholder(/add tags/i);
    for (const tag of options.tags) {
      await tagInput.fill(tag);
      await tagInput.press('Enter');
      // Wait for tag chip to appear
      await expect(page.getByText(tag).first()).toBeVisible();
    }
  }

  // Submit form
  await page.click('button[type="submit"]');
}

describe('Task Tags - Create Task (T031)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should create task with tags via Enter key', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');

    // Fill in title
    await page.fill('input[name="title"]', 'Task with tags');

    // Add tags
    const tagInput = page.getByPlaceholder(/add tags/i);
    await tagInput.fill('work');
    await tagInput.press('Enter');

    // Verify tag chip appears
    await expect(page.getByText('work').first()).toBeVisible();

    // Add another tag
    await tagInput.fill('urgent');
    await tagInput.press('Enter');

    await expect(page.getByText('urgent').first()).toBeVisible();

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to tasks page
    await page.waitForURL('**/tasks?created=true');

    // Verify task appears with tags
    await expect(page.getByText('Task with tags')).toBeVisible();
    await expect(page.getByText('work')).toBeVisible();
    await expect(page.getByText('urgent')).toBeVisible();
  });

  test('should create task with tags via autocomplete', async ({ page }) => {
    // Prerequisite: Create a task with 'work' tag first
    await createTask(page, 'First task', { tags: ['work'] });

    // Now create another task and use autocomplete
    await page.goto('http://localhost:3000/tasks/new');

    await page.fill('input[name="title"]', 'Second task');

    const tagInput = page.getByPlaceholder(/add tags/i);
    await tagInput.fill('wo');

    // Wait for autocomplete suggestions
    await expect(page.getByText('work').first()).toBeVisible();

    // Click on suggestion
    await page.getByText('work').first().click();

    // Verify tag was added
    await expect(page.getByText('work').nth(1)).toBeVisible();

    // Submit
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks?created=true');

    // Verify task has tag
    await expect(page.getByText('Second task')).toBeVisible();
    await expect(page.getByText('work')).toBeVisible();
  });

  test('should validate max 10 tags', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with many tags');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Add 10 tags
    for (let i = 1; i <= 10; i++) {
      await tagInput.fill(`tag${i}`);
      await tagInput.press('Enter');
    }

    // Verify input is disabled
    await expect(tagInput).toBeDisabled();

    // Try to add 11th tag (should not work)
    await expect(page.getByText(/maximum 10 tags/i)).toBeVisible();
  });

  test('should validate tag format', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with invalid tag');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Try to add tag with special characters
    await tagInput.fill('urgent!!!');
    await tagInput.press('Enter');

    // Verify error message
    await expect(page.getByText(/can only contain lowercase letters, numbers, and hyphens/i)).toBeVisible();

    // Verify tag was not added
    await expect(page.getByText('urgent!!!').first()).not.toBeVisible();
  });

  test('should prevent duplicate tags', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with duplicate tag');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Add tag
    await tagInput.fill('work');
    await tagInput.press('Enter');

    // Try to add same tag again
    await tagInput.fill('work');
    await tagInput.press('Enter');

    // Verify error message
    await expect(page.getByText(/tag already added/i)).toBeVisible();

    // Verify only one 'work' chip exists
    const workChips = page.getByText('work').filter({ hasText: /^work$/ });
    await expect(workChips).toHaveCount(1);
  });

  test('should normalize tags (lowercase and trim)', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with normalized tags');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Add tag with uppercase and whitespace
    await tagInput.fill('  URGENT  ');
    await tagInput.press('Enter');

    // Verify tag is normalized to lowercase
    await expect(page.getByText('urgent').first()).toBeVisible();

    // Submit and verify
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks?created=true');

    await expect(page.getByText('urgent')).toBeVisible();
  });

  test('should remove tag via chip close button', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with removable tags');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Add two tags
    await tagInput.fill('work');
    await tagInput.press('Enter');
    await tagInput.fill('urgent');
    await tagInput.press('Enter');

    // Click remove button on first tag
    const removeButtons = page.getByLabelText(/remove tag/i);
    await removeButtons.first().click();

    // Verify 'work' tag is removed
    await expect(page.getByText('work').first()).not.toBeVisible();

    // Verify 'urgent' tag still exists
    await expect(page.getByText('urgent').first()).toBeVisible();
  });

  test('should remove last tag via Backspace on empty input', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks/new');
    await page.fill('input[name="title"]', 'Task with backspace removal');

    const tagInput = page.getByPlaceholder(/add tags/i);

    // Add tags
    await tagInput.fill('work');
    await tagInput.press('Enter');
    await tagInput.fill('urgent');
    await tagInput.press('Enter');

    // Press Backspace on empty input
    await tagInput.press('Backspace');

    // Verify last tag ('urgent') is removed
    await expect(page.getByText('urgent').first()).not.toBeVisible();

    // Verify 'work' tag still exists
    await expect(page.getByText('work').first()).toBeVisible();
  });
});

describe('Task Tags - Edit Task (T032)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should display existing tags when editing task', async ({ page }) => {
    // Create task with tags
    await createTask(page, 'Editable task', { tags: ['work', 'urgent'] });

    // Navigate to edit page (assumes task is first in list)
    await page.click('button:has-text("Edit")');
    await page.waitForURL('**/edit');

    // Verify existing tags are displayed
    await expect(page.getByText('work').first()).toBeVisible();
    await expect(page.getByText('urgent').first()).toBeVisible();
  });

  test('should add new tags when editing task', async ({ page }) => {
    // Create task with one tag
    await createTask(page, 'Task to add tags', { tags: ['work'] });

    // Edit task
    await page.click('button:has-text("Edit")');
    await page.waitForURL('**/edit');

    // Add new tag
    const tagInput = page.getByPlaceholder(/add tags/i);
    await tagInput.fill('important');
    await tagInput.press('Enter');

    // Verify new tag appears
    await expect(page.getByText('important').first()).toBeVisible();

    // Save changes
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks');

    // Verify both tags are displayed on task card
    await expect(page.getByText('work')).toBeVisible();
    await expect(page.getByText('important')).toBeVisible();
  });

  test('should remove tags when editing task', async ({ page }) => {
    // Create task with multiple tags
    await createTask(page, 'Task to remove tags', { tags: ['work', 'urgent', 'important'] });

    // Edit task
    await page.click('button:has-text("Edit")');
    await page.waitForURL('**/edit');

    // Remove 'urgent' tag
    const removeButtons = page.getByLabelText(/remove tag/i);
    const urgentRemoveButton = page.getByLabelText('Remove tag urgent');
    await urgentRemoveButton.click();

    // Verify tag is removed
    await expect(page.getByText('urgent').first()).not.toBeVisible();

    // Save changes
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks');

    // Verify task card shows only remaining tags
    await expect(page.getByText('work')).toBeVisible();
    await expect(page.getByText('important')).toBeVisible();
    await expect(page.getByText('urgent')).not.toBeVisible();
  });

  test('should replace all tags when editing task', async ({ page }) => {
    // Create task with tags
    await createTask(page, 'Task to replace tags', { tags: ['old1', 'old2'] });

    // Edit task
    await page.click('button:has-text("Edit")');
    await page.waitForURL('**/edit');

    // Remove all existing tags
    let removeButtons = page.getByLabelText(/remove tag/i);
    await removeButtons.first().click();
    await removeButtons.first().click();

    // Add new tags
    const tagInput = page.getByPlaceholder(/add tags/i);
    await tagInput.fill('new1');
    await tagInput.press('Enter');
    await tagInput.fill('new2');
    await tagInput.press('Enter');

    // Save changes
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks');

    // Verify new tags are displayed
    await expect(page.getByText('new1')).toBeVisible();
    await expect(page.getByText('new2')).toBeVisible();

    // Verify old tags are gone
    await expect(page.getByText('old1')).not.toBeVisible();
    await expect(page.getByText('old2')).not.toBeVisible();
  });

  test('should save task with no tags', async ({ page }) => {
    // Create task with tags
    await createTask(page, 'Task to clear tags', { tags: ['work', 'urgent'] });

    // Edit task
    await page.click('button:has-text("Edit")');
    await page.waitForURL('**/edit');

    // Remove all tags
    const removeButtons = page.getByLabelText(/remove tag/i);
    await removeButtons.first().click();
    await removeButtons.first().click();

    // Verify no tags remain
    await expect(page.getByText('work').first()).not.toBeVisible();
    await expect(page.getByText('urgent').first()).not.toBeVisible();

    // Save changes
    await page.click('button[type="submit"]');
    await page.waitForURL('**/tasks');

    // Verify task card has no tags section
    const taskCard = page.locator('text="Task to clear tags"').locator('..');
    await expect(taskCard.getByText('work')).not.toBeVisible();
    await expect(taskCard.getByText('urgent')).not.toBeVisible();
  });
});
*/

export {}; // Make this a module to avoid TypeScript errors
