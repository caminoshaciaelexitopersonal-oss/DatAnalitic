import { test, expect } from '@playwright/test';

test.describe('Deliverables Section', () => {
  const testJobId = 'test-job-e2e-123';

  test('should display the deliverables section on the job result page', async ({ page }) => {
    // Navigate to the job result page for a test job ID
    await page.goto(`/jobs/${testJobId}`);

    // Check that the main heading with the job ID is visible
    await expect(page.getByRole('heading', { name: `Job ID: ${testJobId}` })).toBeVisible();

    // Check that the "Entregables" section is rendered
    await expect(page.getByRole('heading', { name: 'Entregables' })).toBeVisible();

    // Check for the placeholder file tree text to ensure the component is there
    await expect(page.getByText('- /src/')).toBeVisible();
    await expect(page.getByText('manifest.json')).toBeVisible();

    // Check that the download button is visible and has the correct text
    const downloadButton = page.getByRole('button', { name: 'Descargar Paquete (.zip)' });
    await expect(downloadButton).toBeVisible();
    await expect(downloadButton).toBeEnabled();
  });

  test('download button should initiate a download', async ({ page }) => {
    // Mock the API endpoint to prevent an actual download during the test if needed,
    // but for this test, we'll just check that clicking it doesn't throw an error and opens a new tab.
    // Playwright can detect the new page/tab created by window.open
    const pagePromise = page.context().waitForEvent('page');

    await page.goto(`/jobs/${testJobId}`);

    // Click the download button
    const downloadButton = page.getByRole('button', { name: 'Descargar Paquete (.zip)' });
    await downloadButton.click();

    // Wait for the new page event and check its URL
    const newPage = await pagePromise;
    await newPage.waitForLoadState();

    expect(newPage.url()).toContain(`/unified/v1/mpa/delivery/job/${testJobId}/package`);

    // Close the new page
    await newPage.close();
  });
});
