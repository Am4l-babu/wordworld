// Capture the real API-backed canvas for the repository's preview assets.
// Run from frontend/: node scripts/capture-readme.mjs
import {chromium} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const directory=new URL('../../.runtime/readme-frames/',import.meta.url);
const assets=new URL('../../docs/assets/',import.meta.url);
await mkdir(directory,{recursive:true});
await mkdir(assets,{recursive:true});
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:'reduce',deviceScaleFactor:1});
 await page.goto(process.env.WORDWORLD_BASE_URL||'http://127.0.0.1:5173');
 await page.getByText('spaCy NLP connected',{exact:true}).waitFor();
 const commands=[
  'Build five houses: two blue and the remaining three red.',
  'Plant trees, a total of five: two green and the remaining three purple.',
  'Put a bridge spanning the creek.',
  'Make it night with rain.',
 ];
 const frame=page.locator('.world-frame');
 await frame.screenshot({path:fileURLToPath(new URL('00.png',directory))});
 for(const [i,text] of commands.entries()){
  await page.getByLabel('Describe your imagination').fill(text);
  const response=page.waitForResponse(r=>r.url().endsWith('/api/parse'));
  await page.getByRole('button',{name:'Generate objects'}).click();
  const output=await (await response).json();
  if(output.model!=='spacy'||!output.actions.length)throw Error('Preview requires the full Python parser.');
  await page.getByRole('button',{name:'Generate objects'}).waitFor({state:'visible'});
  await page.locator('.grounded-command').filter({hasText:text}).waitFor();
  await frame.screenshot({path:fileURLToPath(new URL(`${String(i+1).padStart(2,'0')}.png`,directory))});
  if(i===1)await frame.screenshot({path:fileURLToPath(new URL('world-preview.png',assets))});
 }
 console.log('Captured five real scene states and the README poster.');
}finally{await browser.close()}
