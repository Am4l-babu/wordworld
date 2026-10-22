import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// WCAG 2.0/2.1/2.2 A and AA plus axe's best-practice rules, in both themes, on every state a person can reach.
const TAGS=['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice'];
const editor=page=>page.getByLabel('Describe your imagination');
const command=async page=>{await editor(page).fill('Build one bule house');await page.getByRole('button',{name:'Generate objects'}).click();await expect(page.getByRole('button',{name:/Did you mean/})).toBeVisible()};
const openMenuItem=async(page,item)=>{await page.getByRole('button',{name:'Share & save world'}).click();await page.getByRole('menuitem',{name:item}).click()};
const STATES={
 'the starting island':async()=>{},
 'after a command with a suggestion':command,
 'a selected object':async page=>{await page.locator('.world-svg').getByRole('button',{name:'Select house'}).first().click()},
 'the sentence analysis':async page=>{await command(page);await page.locator('.token-list button').first().click()},
 'the share menu':async page=>{await page.getByRole('button',{name:'Share & save world'}).click()},
 'the help dialog':async page=>{await page.getByRole('button',{name:'How it works',exact:true}).click()},
 'the share dialog':async page=>{await openMenuItem(page,/share link/i)},
 'the test log dialog':async page=>{await openMenuItem(page,/Test log/)},
 'the "Not what I meant" form':async page=>{await command(page);await page.getByRole('button',{name:'Not what I meant'}).last().click()},
};
for(const scheme of ['light','dark'])for(const [name,prepare] of Object.entries(STATES)){
 test(`no accessibility violations in the ${scheme} theme: ${name}`,async({page})=>{
  await page.emulateMedia({colorScheme:scheme});
  await page.goto('/');
  await expect(page.getByText('spaCy NLP connected')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-theme',scheme);
  await prepare(page);
  await page.waitForTimeout(250);
  const {violations}=await new AxeBuilder({page}).withTags(TAGS).analyze();
  expect(violations.map(v=>`${v.id} (${v.impact}): ${v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' | ')}`)).toEqual([]);
 });
}
test('the page has one h1 and distinctly named landmarks',async({page})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{level:1})).toHaveCount(1);
 const names=await page.getByRole('complementary').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('aria-label')));
 expect(new Set(names).size).toBe(names.length);
 expect(names.every(Boolean)).toBe(true);
});
