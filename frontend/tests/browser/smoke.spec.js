import {test,expect} from '@playwright/test';

const scene=page=>page.locator('.world-svg');
const count=page=>page.locator('.objects-summary').first();
async function submit(page,text){
 await page.getByLabel('Describe your imagination').fill(text);
 const response=page.waitForResponse(r=>r.url().endsWith('/api/parse'));
 await page.getByRole('button',{name:'Generate objects'}).click();
 await response;
 await expect(page.getByRole('button',{name:'Generate objects'})).toBeDisabled();
}
test.beforeEach(async({page})=>{await page.goto('/');await expect(page.getByText('spaCy NLP connected')).toBeVisible()});

test('typed between command flows through the API into midpoint placement and explanation',async({page})=>{
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await submit(page,'Put a bridge between two houses');
 await expect(count(page)).toContainText('23 total');
 await expect(page.getByRole('group',{name:'Placement guide: between',exact:true})).toBeVisible();
 await expect(page.locator('.grounded-command .span-landmark')).toHaveText('houses');
 await page.locator('.token-list').getByRole('button',{name:'bridge NOUN',exact:true}).click();
 await expect(page.locator('.token-details')).toContainText('dobj → Put');
 const positions=await scene(page).locator('.scene-object').evaluateAll(nodes=>nodes.map(n=>({type:n.getAttribute('aria-label'),transform:n.getAttribute('transform'),selected:n.getAttribute('aria-pressed')})));
 const coord=transform=>transform.match(/translate\(([^ ]+) ([^)]+)\)/).slice(1).map(Number);
 const houses=positions.filter(o=>o.type==='Select house').map(o=>coord(o.transform));
 const bridge=coord(positions.find(o=>o.type==='Select bridge'&&o.selected==='true').transform);
 expect(bridge).toEqual([(houses[0][0]+houses[1][0])/2,(houses[0][1]+houses[1][1])/2]);
 await page.locator('.main-panel').screenshot({path:`../.runtime/wordworld-${test.info().project.name}.png`});
 await page.getByRole('button',{name:'Hide guides',exact:true}).click();
 await expect(page.locator('.placement-guide')).toHaveCount(0);
 await page.getByRole('button',{name:'Undo',exact:true}).click();
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:'Redo',exact:true}).click();
 await expect(count(page)).toContainText('23 total');
 expect(errors).toEqual([]);
});

test('dragging moves an object and creates a single undo step',async({page})=>{
 await submit(page,'Clear the world then add a tree');
 const tree=scene(page).getByRole('button',{name:'Select tree',exact:true});
 await tree.scrollIntoViewIfNeeded();
 const original=await tree.getAttribute('transform');
 const box=await tree.locator('circle').first().boundingBox();
 await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
 await page.mouse.down();
 await page.mouse.move(box.x+box.width/2+30,box.y+box.height/2+20,{steps:5});
 await page.mouse.up();
 await expect(tree).not.toHaveAttribute('transform',original);
 const moved=await tree.getAttribute('transform');
 await page.getByRole('button',{name:'Undo',exact:true}).click();
 await expect(tree).toHaveAttribute('transform',original);
 await page.getByRole('button',{name:'Redo',exact:true}).click();
 await expect(tree).toHaveAttribute('transform',moved);
});

test('mixed intent, weather negation and missing landmarks are visible',async({page})=>{
 await submit(page,'Clear the world then build two red houses');
 await expect(count(page)).toContainText('2 total');
 await submit(page,'Remove one house and add two blue flowers');
 await expect(count(page)).toContainText('3 total');
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true})).toHaveCount(1);
 await expect(scene(page).getByRole('button',{name:'Select flower',exact:true})).toHaveCount(2);
 await submit(page,'Make it night with rain');
 await expect(scene(page)).toHaveClass(/night/);
 await expect(page.locator('.rain')).toBeVisible();
 await submit(page,'No rain');
 await expect(page.locator('.rain')).toHaveCount(0);
 await submit(page,'Put a bridge between two houses');
 await expect(page.getByLabel('Parser notices')).toContainText('two distinct landmarks');
 await expect(page.locator('.placement-guide')).toHaveCount(0);
});

test('selection, recolor, keyboard movement, duplicate, delete, zoom and autosave',async({page})=>{
 const house=scene(page).getByRole('button',{name:'Select house',exact:true}).first();
 await house.press('Enter');
 await expect(house).toHaveAttribute('aria-pressed','true');
 const original=await house.getAttribute('transform');
 await house.press('ArrowRight');
 await expect(house).not.toHaveAttribute('transform',original);
 await page.getByRole('button',{name:'blue',exact:true}).click();
 await expect(house.locator('path[fill="#74a6ea"]')).toHaveCount(1);
 await page.getByRole('button',{name:'Duplicate',exact:true}).click();
 await expect(count(page)).toContainText('23 total');
 await page.getByRole('button',{name:'Delete',exact:true}).click();
 await expect(count(page)).toContainText('22 total');
 await page.getByRole('button',{name:'Zoom in',exact:true}).click();
 await expect(page.locator('.zoom-controls')).toContainText('110%');
 await page.reload();
 await expect(count(page)).toContainText('22 total');
 await expect(house).not.toHaveAttribute('transform',original);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});

test('API validation failures do not run the preview parser',async({page})=>{
 await page.route('**/api/parse',route=>route.fulfill({status:400,contentType:'application/json',body:JSON.stringify({detail:'Rejected test instruction'})}));
 await submit(page,'Add two houses');
 await expect(page.getByText('Rejected test instruction',{exact:true})).toBeVisible();
 await expect(count(page)).toContainText('22 total');
 await expect(page.getByText('spaCy NLP connected')).toBeVisible();
});

test('unavailable backend leaves unsupported preview commands unchanged',async({page})=>{
 await page.route('**/api/parse',route=>route.abort());
 await page.getByLabel('Describe your imagination').fill('Put a bridge between two houses');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await expect(page.getByText('Browser preview mode')).toBeVisible();
 await expect(count(page)).toContainText('22 total');
 await expect(page.getByLabel('Parser notices')).toContainText('Python API is unavailable');
});

test('negation, protected mentions, quantities and initial locations reach the scene correctly',async({page})=>{
 await submit(page,'Don’t add any bridges.');
 await expect(count(page)).toContainText('22 total');
 await submit(page,'Keep the houses and remove the flowers.');
 await expect(count(page)).toContainText('16 total');
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true})).toHaveCount(2);
 await submit(page,'Behind the lake, plant a pair of purple trees.');
 await expect(count(page)).toContainText('18 total');
 await expect(scene(page).getByRole('button',{name:'Select lake',exact:true})).toHaveCount(1);
 await expect(page.getByRole('group',{name:'Placement guide: above',exact:true})).toBeVisible();
 await expect(page.locator('.grounded-command .span-spatial_relation')).toHaveText('Behind');
 await expect(page.locator('.grounded-command .span-quantity')).toHaveText('a pair');
 await page.locator('.main-panel').screenshot({path:`../.runtime/parser-fixes-${test.info().project.name}.png`});
});

test('spanning, coordinated colors and request-local pronouns create only intended objects',async({page})=>{
 await submit(page,'Put a bridge spanning the creek.');
 await expect(count(page)).toContainText('23 total');
 await expect(scene(page).getByRole('button',{name:'Select river',exact:true})).toHaveCount(1);
 await expect(page.getByRole('group',{name:'Placement guide: across',exact:true})).toBeVisible();
 await submit(page,'Build a house, then remove it.');
 await expect(count(page)).toContainText('23 total');
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true})).toHaveCount(2);
 await submit(page,'Build one red and one blue house; put a tree between them.');
 await expect(count(page)).toContainText('26 total');
 await expect(scene(page).getByRole('button',{name:'Select house',exact:true})).toHaveCount(4);
 await expect(page.getByRole('group',{name:'Placement guide: between',exact:true})).toBeVisible();
 await expect(page.locator('.reference-resolutions')).toContainText('them → 1 house + 1 house');
 await expect(page.locator('.grounded-command .span-color')).toHaveText(['red','blue']);
 await page.locator('.main-panel').screenshot({path:`../.runtime/reference-fixes-${test.info().project.name}.png`});
});

test('post-noun colors, appositive counts and colorless coordination reach visible objects',async({page})=>{
 await submit(page,'Build cottages, three of them, with blue roofs.');
 await expect(count(page)).toContainText('25 total');
 const houses=scene(page).getByRole('button',{name:'Select house',exact:true});
 await expect(houses).toHaveCount(5);
 await expect(houses.locator('path[fill="#74a6ea"]')).toHaveCount(3);
 await expect(page.locator('.grounded-command .span-quantity')).toHaveText('three');
 await expect(page.locator('.grounded-command .span-color')).toHaveText('blue');
 await submit(page,'Plant two small and three large trees whose leaves are purple.');
 await expect(count(page)).toContainText('30 total');
 await expect(scene(page).getByRole('button',{name:'Select tree',exact:true})).toHaveCount(14);
 await expect(scene(page).getByRole('button',{name:'Select tree',exact:true}).locator('circle[fill="#a78bd8"]')).toHaveCount(15);
 await expect(page.locator('.grounded-command .span-quantity')).toHaveText(['two','three']);
 await submit(page,'Build houses, two of them, with orange roofs; remove them.');
 await expect(count(page)).toContainText('30 total');
 await expect(houses).toHaveCount(5);
 await expect(page.locator('.reference-resolutions')).toContainText('them → 2 house');
 await page.getByRole('button',{name:'Undo',exact:true}).click();
 await expect(count(page)).toContainText('30 total');
 await page.getByRole('button',{name:'Redo',exact:true}).click();
 await expect(count(page)).toContainText('30 total');
 await page.locator('.main-panel').screenshot({path:`../.runtime/postnoun-fixes-${test.info().project.name}.png`});
});

test('exact quantities, roof clauses, ones and coordinated relatives execute with scoped references',async({page})=>{
 await submit(page,'Plant flowers, exactly five in all.');
 await expect(count(page)).toContainText('27 total');
 await expect(scene(page).getByRole('button',{name:'Select flower',exact:true})).toHaveCount(11);
 await submit(page,'Build a house with a roof painted purple and two large ones with roofs that are blue.');
 await expect(count(page)).toContainText('30 total');
 const houses=scene(page).getByRole('button',{name:'Select house',exact:true});
 await expect(houses).toHaveCount(5);
 await expect(houses.locator('path[fill="#a78bd8"]')).toHaveCount(1);
 await expect(houses.locator('path[fill="#74a6ea"]')).toHaveCount(2);
 await expect(page.locator('.grounded-command .span-object')).toHaveText(['house','ones']);
 await submit(page,'Plant one tree that is yellow and one that is pink; put a flower between them.');
 await expect(count(page)).toContainText('33 total');
 const trees=scene(page).getByRole('button',{name:'Select tree',exact:true});
 await expect(trees).toHaveCount(11);
 await expect(trees.locator('circle[fill="#f5bc59"]')).toHaveCount(3);
 await expect(trees.locator('circle[fill="#eaa2bc"]')).toHaveCount(3);
 await expect(page.getByRole('group',{name:'Placement guide: between',exact:true})).toBeVisible();
 await expect(page.locator('.reference-resolutions')).toContainText('them → 1 tree + 1 tree');
 await expect(page.locator('.grounded-command .span-color')).toHaveText(['yellow','pink']);
 await submit(page,'Build one house with a roof that is orange and two large ones; remove them.');
 await expect(count(page)).toContainText('33 total');
 await expect(houses).toHaveCount(5);
 await expect(page.locator('.reference-resolutions')).toContainText('them → 1 house + 2 house');
 await page.locator('.main-panel').screenshot({path:`../.runtime/ellipsis-fixes-${test.info().project.name}.png`});
});

test('counted partitions create no default object and passive roofs, totals and omitted predicates render',async({page})=>{
 await submit(page,'Plant trees, two that are green and three yellow.');
 await expect(count(page)).toContainText('27 total');
 const trees=scene(page).getByRole('button',{name:'Select tree',exact:true});
 await expect(trees).toHaveCount(14);
 await expect(trees.locator('circle[fill="#80bea1"]')).toHaveCount(6);
 await expect(trees.locator('circle[fill="#f5bc59"]')).toHaveCount(9);
 await submit(page,'Build two houses, one whose roof has been painted blue and one with a purple roof.');
 await expect(count(page)).toContainText('29 total');
 const houses=scene(page).getByRole('button',{name:'Select house',exact:true});
 await expect(houses).toHaveCount(4);
 await expect(houses.locator('path[fill="#74a6ea"]')).toHaveCount(1);
 await expect(houses.locator('path[fill="#a78bd8"]')).toHaveCount(1);
 await expect(page.locator('.grounded-command .span-color')).toHaveText(['blue','purple']);
 await submit(page,'Add flowers, five total.');
 await expect(count(page)).toContainText('34 total');
 await expect(scene(page).getByRole('button',{name:'Select flower',exact:true})).toHaveCount(11);
 await submit(page,'Build houses, one blue and one green; put a flower between them; remove two of them.');
 await expect(count(page)).toContainText('37 total');
 await expect(houses).toHaveCount(6);
 await expect(page.getByRole('group',{name:'Placement guide: between',exact:true})).toBeVisible();
 await expect(page.locator('.reference-resolutions')).toContainText('them → 1 house + 1 house');
 await page.getByRole('button',{name:'Undo',exact:true}).click();
 await expect(count(page)).toContainText('34 total');
 await page.getByRole('button',{name:'Redo',exact:true}).click();
 await expect(count(page)).toContainText('37 total');
 await page.locator('.main-panel').screenshot({path:`../.runtime/partition-fixes-${test.info().project.name}.png`});
});
