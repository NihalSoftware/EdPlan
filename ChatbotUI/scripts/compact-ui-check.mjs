import { createRequire } from 'node:module';
import { mkdir, readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const reference = process.argv.includes('--reference');
const base = reference ? 'https://www.studentspace.ai' : (process.env.UI_BASE_URL || 'http://localhost:5173');
await mkdir('artifacts/compact-ui', { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_EXECUTABLE });
try {
  for (const width of reference ? [1335, 390] : [375, 390, 768, 1280, 1335, 1920]) {
    const context = await browser.newContext({ viewport: { width, height: 862 } });
    if (!reference) {
      // Browser-only responses from existing catalog content; no database writes.
      const source = JSON.parse((await readFile('public/assets/programdetail.json', 'utf8')).replace(/^\uFEFF/, ''));
      const university = source.universities.find(item => item.university === 'Northern New Mexico College');
      const program = university.programs.find(item => item.program === 'Barbering');
      await context.route('**/api/**', async route => {
        const pathname = new URL(route.request().url()).pathname;
        let data = [];
        if (pathname.endsWith('/programs')) data = [{ ...program, program_id: 'compact-ui-program', university_name: university.university }];
        if (pathname.endsWith('/courses')) data = program.courses.map(course => ({ ...course,
          course_code: course.courseCode, course_name: course.name,
          is_elective: course.courseCode.startsWith('ELEC'), default_plan_eligible: !course.courseCode.startsWith('ELEC'),
        }));
        await route.fulfill({ contentType: 'application/json', body: JSON.stringify({ data }) });
      });
      await context.addInitScript(() => {
        localStorage.setItem('University', JSON.stringify('Northern New Mexico College'));
        localStorage.setItem('Programname', JSON.stringify('Barbering'));
        localStorage.setItem('ProgramDegree', JSON.stringify('Associate of Applied Science'));
      });
    }
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`${base}/educationplan`);
    await page.waitForTimeout(1600);
    if (!reference) {
      await page.getByRole('combobox', { name: 'Program', exact: true }).selectOption('Barbering');
      await page.getByRole('combobox', { name: 'Select semester', exact: true }).locator('option').nth(3).waitFor({ state: 'attached' });
      await page.getByRole('button', { name: /Add Semester/ }).click();
      await page.getByRole('button', { name: /Add Semester/ }).click();
      const labels = await page.getByRole('combobox', { name: 'Select semester', exact: true }).locator('option').allTextContents();
      assert.ok(labels.includes('Sem 5: Fall') && labels.includes('Sem 6: Spring'));
      const catalogToggle = page.getByRole('button', { name: /Program course list/ });
      await catalogToggle.click();
      await catalogToggle.click();
      await page.getByRole('button', { name: 'Add course to semester 6: Spring', exact: true }).click();
      assert.equal(await catalogToggle.getAttribute('aria-expanded'), 'true');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (width === 1335) await page.screenshot({ path: 'artifacts/compact-ui/planner-open-1335.png', fullPage: true });
      await page.locator('#program-course-list-content button').first().click();
      await page.getByText('8 courses', { exact: true }).waitFor();
      await catalogToggle.click();
      assert.equal(await page.getByRole('button', { name: 'Save Your Plan', exact: true }).count(), 1);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    }
    await page.screenshot({ path: `artifacts/compact-ui/${reference ? 'reference' : 'planner'}-${width}.png`, fullPage: true });
    if (reference) console.log(JSON.stringify(await page.evaluate(() => ({ width: innerWidth,
      headings: [...document.querySelectorAll('h1,h2')].map(node => node.textContent),
      controls: [...document.querySelectorAll('select,button')].filter(node => node.getBoundingClientRect().width > 0).map(node => ({
        text: node.textContent.trim().slice(0, 80), x: node.getBoundingClientRect().x, y: node.getBoundingClientRect().y,
        height: node.getBoundingClientRect().height, background: getComputedStyle(node).backgroundColor,
      })).slice(-20),
    }))));
    if (!reference) {
      await page.getByRole('button', { name: 'Save Your Plan', exact: true }).click();
      assert.ok(await page.evaluate(() => JSON.parse(localStorage.getItem('LocalSavedPlans') || '[]').length > 0));
      await page.goto(`${base}/career`);
      await page.locator('#career-program').waitFor();
      const panelHeight = await page.locator('.career-filter-panel').evaluate(node => node.getBoundingClientRect().height);
      if (width >= 768) assert.ok(panelHeight < 120, `Filter panel should be compact; got ${panelHeight}px`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({ path: `artifacts/compact-ui/career-${width}.png`, fullPage: true });
      assert.deepEqual(errors, []);
      console.log(`PASS ${width}px: planner, semester labels, catalog disclosure, course addition, local save, compact filters, no page overflow/errors`);
    }
    await context.close();
  }
} finally { await browser.close(); }
