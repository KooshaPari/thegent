import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

/**
 * This is a template for generating web demos.
 * It uses Playwright to record a video and then converts it to a GIF.
 */
test('generate web demo', async ({ page }, testInfo) => {
  // 1. Setup video recording (Playwright does this automatically if configured)
  // We can also use a custom recording strategy if needed.
  
  await page.goto('https://vitepress.dev/');
  
  // 2. Perform actions
  await page.click('text=Get Started');
  await expect(page).toHaveURL(/.*guide/);
  
  await page.waitForTimeout(1000);
  
  // 3. After the test, Playwright saves the video.
  // We can convert it to GIF in a global teardown or a script.
});
