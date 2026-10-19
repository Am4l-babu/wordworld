// Capture the typo suggester and the Test log for the README. Run from frontend/ with both servers up:
//   node scripts/capture-features.mjs
import {chromium} from '@playwright/test';
import {fileURLToPath} from 'node:url';
const assets=new URL('../../docs/assets/',import.meta.url);
const out=name=>fileURLToPath(new URL(name,assets));
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'light',reducedMotion:'reduce'});
 await page.goto(process.env.WORDWORLD_BASE_URL||'http://127.0.0.1:5173');
 await page.getByText('spaCy NLP connected',{exact:true}).waitFor();
 await page.getByLabel('Describe your imagination').fill('Paint the tres blue');
 await page.getByRole('button',{name:'Generate objects'}).click();
 await page.getByRole('button',{name:/Did you mean/}).waitFor();
 await page.getByRole('button',{name:'Not what I meant'}).last().click();
 await page.getByLabel('What did you expect?').fill('I wanted the trees blue');
 await page.getByRole('button',{name:'Save',exact:true}).click();
 await page.locator('.chat-history').screenshot({path:out('ui-typo-suggestion.png')});
 await page.getByRole('button',{name:'Share & save world'}).click();
 await page.getByRole('menuitem',{name:/Test log/}).click();
 await page.locator('.help-modal').waitFor();
 await page.locator('.help-modal').screenshot({path:out('ui-test-log.png')});
 console.log('Captured the typo suggestion and the Test log dialog.');
}finally{await browser.close()}
