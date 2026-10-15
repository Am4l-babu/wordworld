import {defineConfig,devices} from '@playwright/test';

export default defineConfig({
 testDir:'./tests/browser',
 timeout:30000,
 fullyParallel:true,
 workers:2,
 reporter:'list',
 use:{baseURL:process.env.WORDWORLD_BASE_URL||'http://127.0.0.1:5173',trace:'retain-on-failure',screenshot:'only-on-failure'},
 projects:[{name:'desktop',use:{...devices['Desktop Chrome'],viewport:{width:1440,height:1100}}},{name:'mobile',use:{...devices['iPhone 13'],defaultBrowserType:'chromium'}}],
});
