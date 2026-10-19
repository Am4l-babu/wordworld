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

test('language edits recolor, resize and move existing objects, and "it" follows the last command',async({page})=>{
 const houses=scene(page).getByRole('button',{name:'Select house',exact:true});
 await editor(page).fill('Paint the houses blue');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(houses.locator('path[fill="#74a6ea"]')).toHaveCount(2);
 await expect(count(page)).toContainText('22 total');
 await editor(page).fill('Build a castle');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.locator('.focus-chip')).toContainText('1 castle');
 const castle=scene(page).getByRole('button',{name:'Select castle',exact:true});
 const before=await castle.getAttribute('transform');
 await editor(page).fill('make it bigger');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(castle).not.toHaveAttribute('transform',before);
 await expect(page.locator('.reference-resolutions')).toContainText('it → 1 castle (from before)');
 await editor(page).fill('move it next to the lake');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByRole('group',{name:'Placement guide: near',exact:true})).toBeVisible();
 await expect(count(page)).toContainText('23 total');
 await scene(page).getByRole('button',{name:'Select rock',exact:true}).click();
 await expect(page.locator('.focus-chip')).toContainText('1 rock');
 await editor(page).fill('remove it');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(scene(page).getByRole('button',{name:'Select rock',exact:true})).toHaveCount(0);
 await expect(scene(page).getByRole('button',{name:'Select castle',exact:true})).toHaveCount(1);
});

test('the analysis compares the rules with a dependency-parse baseline',async({page})=>{
 await editor(page).fill('Build two red houses next to the lake');
 await page.getByRole('button',{name:'Generate objects'}).click();
 const compare=page.getByLabel('Extractor comparison');
 await expect(compare).toContainText('Same actions');
 await expect(compare).toContainText(/Across \d+ labelled commands/);
 await editor(page).fill('Build five houses: two blue and the remaining three red.');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(compare).toContainText('Different actions');
 await expect(compare.locator('.compare-column').first()).toContainText('+ 2 blue houses');
});

test('a two-finger pinch zooms the island',async({page})=>{
 const svg=scene(page),box=await svg.boundingBox();
 const cx=box.x+box.width/2,cy=box.y+box.height/2;
 const touch=(type,id,x,y)=>svg.dispatchEvent(type,{pointerId:id,pointerType:'touch',isPrimary:id===1,clientX:x,clientY:y,bubbles:true});
 await touch('pointerdown',1,cx-40,cy);
 await touch('pointerdown',2,cx+40,cy);
 for(const spread of [60,90,120])await touch('pointermove',2,cx+spread,cy);
 await touch('pointerup',2,cx+120,cy);
 await touch('pointerup',1,cx-40,cy);
 await expect(page.locator('.zoom-controls')).not.toContainText('100%');
 await expect(count(page)).toContainText('22 total');
});

test('a place filter edits and removes only the objects in that place',async({page})=>{
 const trees=scene(page).getByRole('button',{name:'Select tree',exact:true});
 await expect(trees).toHaveCount(9);
 await editor(page).fill('Paint the trees near the lake red');
 await page.getByRole('button',{name:'Generate objects'}).click();
 const red=trees.filter({has:page.locator('circle[fill="#ed786f"]')});
 await expect(red).not.toHaveCount(0);
 expect(await red.count()).toBeLessThan(9);
 await expect(page.locator('.actions-chips').first()).toContainText('near lake');
 const painted=await red.count();
 await editor(page).fill('Remove the trees near the lake');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(trees).toHaveCount(9-painted);
 await expect(red).toHaveCount(0);
 await editor(page).fill('Remove the rocks near the mountain');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByLabel('Creation journal')).toContainText('There is no mountain to measure from');
});

test('server errors with an explanation are shown, not mistaken for an offline API',async({page})=>{
 await page.route('**/api/parse',route=>route.fulfill({status:500,contentType:'application/json',body:JSON.stringify({detail:'The language engine hit an unexpected problem with that command. Try rephrasing it.'})}));
 await editor(page).fill('Add a tree');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByLabel('Creation journal')).toContainText('unexpected problem with that command');
 await expect(page.getByText('spaCy NLP connected')).toBeVisible();
 await expect(count(page)).toContainText('22 total');
 await page.unroute('**/api/parse');
 await page.route('**/api/parse',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:[{loc:['body','text'],msg:'String should have at most 1400 characters',type:'string_too_long'}]})}));
 await editor(page).fill('Add another tree');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByLabel('Creation journal')).toContainText('String should have at most 1400 characters');
 await expect(count(page)).toContainText('22 total');
});

test('a typo that blocks every action offers a corrected sentence that is only applied on request',async({page})=>{
 await editor(page).fill('Plant a tre next to the lak');
 await page.getByRole('button',{name:'Generate objects'}).click();
 const hint=page.getByRole('button',{name:/Did you mean/});
 await expect(hint).toContainText('Plant a tree next to the lake');
 await expect(count(page)).toContainText('22 total');
 await hint.click();
 await expect(editor(page)).toHaveValue('Plant a tree next to the lake');
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(count(page)).toContainText('23 total');
 await editor(page).fill('Hello there friend');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByLabel('Creation journal')).toContainText('No scene changes were applied');
 await expect(page.getByRole('button',{name:/Did you mean/})).toHaveCount(1);
});

test('a typo that only costs part of a command warns and offers an explicit undo, never a double build',async({page})=>{
 await editor(page).fill('Build one bule house');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(count(page)).toContainText('23 total');
 await expect(page.getByText('Part of that wasn’t understood')).toBeVisible();
 const hint=page.getByRole('button',{name:/Did you mean/});
 await expect(hint).toContainText('Build one blue house');
 await hint.click();
 await expect(editor(page)).toHaveValue('Build one blue house');
 await expect(count(page)).toContainText('23 total');
 await page.getByRole('button',{name:'Undo that step'}).click();
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(count(page)).toContainText('23 total');
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true}).locator('path[fill="#74a6ea"]')).toHaveCount(1);
});
