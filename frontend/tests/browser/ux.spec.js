import {test,expect} from '@playwright/test';

const count=page=>page.locator('.objects-summary').first();
const scene=page=>page.locator('.world-svg');
const editor=page=>page.getByLabel('Describe your imagination');
test.beforeEach(async({page})=>{await page.goto('/');await expect(page.getByText('spaCy NLP connected')).toBeVisible()});

test('edits made while a command is pending are kept when its result arrives',async({page})=>{
 await page.route('**/api/parse',async route=>{await new Promise(r=>setTimeout(r,700));await route.continue()});
 await editor(page).fill('Add a castle');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await scene(page).getByRole('button',{name:'Select rock',exact:true}).click();
 await page.getByRole('button',{name:'Delete',exact:true}).click();
 await expect(scene(page).getByRole('button',{name:'Select castle',exact:true})).toHaveCount(1);
 await expect(scene(page).getByRole('button',{name:'Select rock',exact:true})).toHaveCount(0);
 await expect(count(page)).toContainText('22 total');
});

test('keyboard shortcuts delete, undo, redo and the toast offers undo',async({page})=>{
 const rock=scene(page).getByRole('button',{name:'Select rock',exact:true});
 await rock.focus();await rock.press('Enter');
 await page.keyboard.press('Delete');
 await expect(count(page)).toContainText('21 total');
 await page.getByRole('button',{name:'Undo last change'}).click();
 await expect(count(page)).toContainText('22 total');
 await page.locator('body').click({position:{x:2,y:2}});
 await page.keyboard.press('ControlOrMeta+Shift+Z');
 await expect(count(page)).toContainText('21 total');
 await page.keyboard.press('ControlOrMeta+Z');
 await expect(count(page)).toContainText('22 total');
 await page.keyboard.press('/');
 await expect(editor(page)).toBeFocused();
});

test('singular removal, command recall and journal reuse',async({page})=>{
 await editor(page).fill('Remove the house');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true})).toHaveCount(1);
 await editor(page).focus();
 await page.keyboard.press('ArrowUp');
 await expect(editor(page)).toHaveValue('Remove the house');
 await page.keyboard.press('ArrowDown');
 await expect(editor(page)).toHaveValue('');
 await page.getByRole('button',{name:'Edit again: Remove the house'}).click();
 await expect(editor(page)).toHaveValue('Remove the house');
});

test('import restores an exported scene and rejects other files',async({page})=>{
 const file={name:'scene.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({items:[{id:'a',type:'castle',x:500,y:330},{id:'b',type:'tree',x:600,y:330,color:'purple'}],settings:{time:'night',weather:'snow'}}))};
 await page.locator('input[type=file]').setInputFiles(file);
 await expect(count(page)).toContainText('2 total');
 await expect(scene(page)).toHaveClass(/night/);
 await page.locator('input[type=file]').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"hello":1}')});
 await expect(page.getByText('That file is not a WordWorld scene export.')).toBeVisible();
 await expect(count(page)).toContainText('2 total');
});

test('empty world offers a starter and help closes with Escape',async({page})=>{
 await page.getByRole('button',{name:'Clear the world'}).click();
 await expect(count(page)).toContainText('0 total');
 await page.getByRole('button',{name:'Restore starter village'}).click();
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:'How it works',exact:true}).click();
 await expect(page.getByRole('dialog')).toBeVisible();
 await page.keyboard.press('Escape');
 await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('theme toggle switches to dark and survives a reload',async({page})=>{
 const panel=()=>page.evaluate(()=>getComputedStyle(document.querySelector('.left-panel')).backgroundColor);
 const start=await page.evaluate(()=>document.documentElement.dataset.theme),original=await panel();
 const next=start==='dark'?'light':'dark';
 await page.getByRole('button',{name:`Switch to ${next} theme`}).click();
 await expect(page.locator('html')).toHaveAttribute('data-theme',next);
 await page.reload();
 await expect(page.locator('html')).toHaveAttribute('data-theme',next);
 expect(await panel()).not.toBe(original);
});

test('a share link opens a copy of the island and undo restores your own',async({page})=>{
 await page.getByRole('button',{name:'Share or save world'}).click();
 await page.getByRole('menuitem',{name:/Copy share link/}).click();
 const link=await page.getByLabel('Share link').inputValue();
 expect(link).toContain('?world=');
 await page.getByRole('button',{name:'Close share dialog'}).click();
 await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('button',{name:'Clear the world'}).click();
 await expect(count(page)).toContainText('0 total');
 await page.goto(link);
 await expect(count(page)).toContainText('22 total');
 await expect(page.getByText('Opened a shared island')).toBeVisible();
 expect(page.url()).not.toContain('world=');
 await page.getByRole('button',{name:'Undo last change'}).click();
 await expect(count(page)).toContainText('0 total');
});

test('zoomed-in islands pan by dragging empty space and reset restores the view',async({page})=>{
 for(let i=0;i<5;i++)await page.getByRole('button',{name:'Zoom in'}).click();
 await expect(page.locator('.zoom-controls')).toContainText('150%');
 const before=await scene(page).getAttribute('viewBox');
 const box=await scene(page).boundingBox();
 await page.mouse.move(box.x+box.width*.5,box.y+12);
 await page.mouse.down();
 await page.mouse.move(box.x+box.width*.5+80,box.y+60,{steps:6});
 await page.mouse.up();
 const after=await scene(page).getAttribute('viewBox');
 expect(after).not.toBe(before);
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:/reset view/}).click();
 await expect(scene(page)).toHaveAttribute('viewBox','0 0.5 1000 645');
});

test('sentence structure explains dependencies alongside grounding roles',async({page})=>{
 await editor(page).fill('Put a bridge between two houses');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.locator('.dep-arcs')).toBeVisible();
 await expect(page.locator('.dep-arc')).not.toHaveCount(0);
 await page.locator('.token-list').getByRole('button',{name:'bridge NOUN',exact:true}).click();
 await expect(page.locator('.token-meaning')).toHaveText('“bridge” is a noun acting as the direct object of “Put”.');
 await expect(page.locator('.token-details')).toContainText('Object');
 await page.locator('.token-details').getByRole('button',{name:'Put'}).click();
 await expect(page.locator('.token-meaning')).toContainText('root of the sentence');
});
