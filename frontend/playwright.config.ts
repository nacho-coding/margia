import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir:"./tests", fullyParallel:false, workers:1,
  timeout:45_000, expect:{timeout:12_000}, retries:0,
  reporter:[["list"],["json",{outputFile:"../artifacts/qa/playwright.json"}]],
  use:{baseURL:"http://127.0.0.1:3000",viewport:{width:1440,height:900},locale:"es-ES",timezoneId:"Europe/Madrid",trace:"retain-on-failure",screenshot:"only-on-failure"},
});
