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
  'Paint the red houses yellow and make them bigger.',
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
 // Full interface in both themes, for the README and the mobile/dark QA notes.
 await page.screenshot({path:fileURLToPath(new URL('ui-light.png',assets))});
 await page.getByRole('button',{name:'Switch to dark theme'}).click().catch(()=>{});
 await page.screenshot({path:fileURLToPath(new URL('ui-dark.png',assets))});
 const phone=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,colorScheme:'dark',reducedMotion:'reduce'});
 await phone.goto(process.env.WORDWORLD_BASE_URL||'http://127.0.0.1:5173');
 await phone.getByText('spaCy NLP connected',{exact:true}).waitFor();
 await phone.getByLabel('Describe your imagination').fill('Build a castle');
 await phone.getByRole('button',{name:'Generate objects'}).click();
 await phone.locator('.focus-chip').waitFor();
 await phone.screenshot({path:fileURLToPath(new URL('mobile-dark.png',assets))});
 const sizes=await phone.evaluate(()=>['.theme-toggle','.world-menu .export-button','.top-help[aria-label="How it works"]','.zoom-controls button','.size-control button','.composer-footer button']
  .map(selector=>[selector,...[...document.querySelectorAll(selector)].map(el=>{const r=el.getBoundingClientRect();return `${Math.round(r.width)}x${Math.round(r.height)}`})]));
 console.log('Phone touch targets:',JSON.stringify(sizes));
 console.log('Captured six real scene states, the README poster and light/dark interface screenshots.');
}finally{await browser.close()}
