import {test,expect} from '@playwright/test';

for(const [width,height] of [[320,740],[390,844],[430,932],[768,1024],[844,390]]){
 test(`responsive layout at ${width}x${height} keeps the editor, controls and dialogs usable`,async({page})=>{
  await page.setViewportSize({width,height});
  await page.goto('/');
  await expect(page.getByText('spaCy NLP connected')).toBeVisible();
  const compact=width<=735||(width<=950&&height<=500);
  const geometry=await page.evaluate(()=>{
   const rect=s=>document.querySelector(s).getBoundingClientRect().toJSON();
   return {scroll:document.documentElement.scrollWidth,width:innerWidth,composer:rect('.composer'),canvas:rect('.world-frame'),font:parseFloat(getComputedStyle(document.querySelector('textarea')).fontSize),buttons:[...document.querySelectorAll('.world-controls button,.zoom-controls button,.composer-footer button')].map(x=>({label:x.title,...x.getBoundingClientRect().toJSON()}))};
  });
  expect(geometry.scroll).toBeLessThanOrEqual(geometry.width+1);
  if(compact){
   expect(geometry.composer.y).toBeLessThan(geometry.canvas.y);
   expect(geometry.composer.y).toBeLessThan(250);
   expect(geometry.font).toBeGreaterThanOrEqual(16);
   for(const box of geometry.buttons){expect(box.height,box.label).toBeGreaterThanOrEqual(44);expect(box.width,box.label).toBeGreaterThanOrEqual(44)}
  }
  await page.getByLabel('Describe your imagination').fill('Build eight flowers: half pink and half white.');
  await page.getByRole('button',{name:'Generate objects'}).click();
  await expect(page.locator('.objects-summary').first()).toContainText('30 total');
  await page.getByRole('button',{name:'How it works',exact:true}).click();
  await expect(page.getByRole('heading',{name:'How WordWorld works'})).toBeVisible();
  const dialog=await page.locator('.help-modal').boundingBox();
  expect(dialog.x).toBeGreaterThanOrEqual(0);expect(dialog.x+dialog.width).toBeLessThanOrEqual(width+1);
  await page.getByRole('button',{name:'Close help'}).click();
  await expect(page.locator('.help-modal')).toHaveCount(0);
  await page.screenshot({path:`../.runtime/mobile-audit-v9/check-${test.info().project.name}-${width}.png`,fullPage:true});
 });
}

test('moving between desktop and phone preserves draft, saved scene and a single editor',async({page})=>{
 await page.setViewportSize({width:1440,height:1100});await page.goto('/');
 const draft='Build two houses whose roofs will be painted yellow.';
 await page.getByLabel('Describe your imagination').fill(draft);
 await page.setViewportSize({width:390,height:844});
 await expect(page.getByLabel('Describe your imagination')).toHaveCount(1);
 await expect(page.getByLabel('Describe your imagination')).toHaveValue(draft);
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.locator('.objects-summary').first()).toContainText('24 total');
 await page.getByLabel('Describe your imagination').fill('Stop the storm');
 await page.getByLabel('Describe your imagination').press('Enter');
 await expect(page.getByLabel('Describe your imagination')).toHaveValue('Stop the storm\n');
 await page.setViewportSize({width:1440,height:1100});
 await expect(page.getByLabel('Describe your imagination')).toHaveValue('Stop the storm\n');
 await expect(page.locator('.objects-summary').first()).toContainText('24 total');
});
