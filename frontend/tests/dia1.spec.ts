import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

test("centro: cifras de API, contexto entre vistas, definiciones y exportación", async({page,request})=>{
  const errors:string[]=[];page.on("pageerror",error=>errors.push(error.message));
  await page.goto("/");
  await expect(page.getByTestId("kpi-ventas")).toBeVisible();
  const global=await (await request.get("/api/v1/kpis?dias=28")).json();
  const format=(n:number)=>new Intl.NumberFormat("es-ES",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(n);
  await expect(page.getByTestId("kpi-ventas")).toContainText(format(global.metricas[0].valor));
  await page.getByLabel("Mercado global").selectOption("m01");
  const local=await (await request.get("/api/v1/kpis?dias=28&mercado=m01")).json();
  await expect(page.getByTestId("kpi-ventas")).toContainText(format(local.metricas[0].valor));
  await page.getByLabel("Definición de ventas netas").click();
  await expect(page.getByRole("dialog")).toContainText("Ventas propias sin IVA");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(page.getByLabel("Definición de ventas netas")).toBeFocused();
  await page.getByRole("button",{name:"Pedidos",exact:true}).click();
  await expect(page.getByRole("button",{name:"Pedidos",exact:true})).toHaveAttribute("aria-pressed","true");
  const download=page.waitForEvent("download");
  await page.getByRole("link",{name:"Exportar negocio"}).click();
  expect((await download).suggestedFilename()).toBe("margia-negocio-sintetico.csv");
  await page.getByRole("link",{name:"Explorar One Search",exact:true}).click();
  await expect(page).toHaveURL(/mercado=m01/);
  await expect(page.getByRole("table")).toBeVisible();
  expect(errors).toEqual([]);
});

test("búsqueda y creatividad: filtros, paginación, activos y detalle",async({page})=>{
  await page.goto("/one-search");
  await expect(page.getByRole("table")).toBeVisible();
  await page.getByLabel("Intención",{exact:true}).selectOption("Marca pura");
  await expect(page.getByText("16 registros",{exact:false})).toBeVisible();
  await page.getByLabel("Página siguiente").click();
  await expect(page.getByText("Página 2 de 2",{exact:false})).toBeVisible();
  await page.getByRole("link",{name:"Inteligencia creativa",exact:true}).click();
  await expect(page.locator(".creative-card")).toHaveCount(12);
  await page.getByLabel("Canal",{exact:true}).selectOption("meta");
  await expect(page.getByText("20 registros",{exact:false})).toBeVisible();
  await page.locator(".creative-image-button").first().click();
  await expect(page.getByRole("dialog")).toContainText("Métricas observadas");
  expect(await page.getByRole("dialog").locator("img").evaluate((el:HTMLImageElement)=>el.complete&&el.naturalWidth>0)).toBeTruthy();
  await page.getByLabel("Cerrar detalle").click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
});

test("fiabilidad, alcance pendiente y confirmación de reset",async({page,request})=>{
  await page.goto("/fiabilidad");
  await expect(page.getByRole("heading",{name:"Inventario de fuentes"})).toBeVisible();
  await expect(page.getByText("100 %",{exact:false}).first()).toBeVisible();
  await page.getByRole("link",{name:"Laboratorio",exact:true}).click();
  await expect(page.getByText("En desarrollo · Día 3")).toBeVisible();
  await page.getByRole("link",{name:"Escenarios",exact:true}).click();
  await expect(page.getByText("En desarrollo · Día 4")).toBeVisible();
  await page.getByRole("link",{name:"Configuración",exact:true}).click();
  await page.getByRole("button",{name:"Restablecer demo",exact:true}).click();
  await page.getByLabel("Confirmación requerida").fill("NO");
  await page.getByRole("button",{name:"Restablecer ahora",exact:true}).click();
  expect(await page.getByLabel("Confirmación requerida").evaluate((el:HTMLInputElement)=>el.validity.patternMismatch)).toBeTruthy();
  await page.getByRole("button",{name:"Conservar datos"}).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  const invalid=await request.post("/api/v1/demo/reset",{data:{confirmacion:"si"}});expect(invalid.status()).toBe(422);
  const crossOrigin=await request.post("/api/v1/demo/reset",{headers:{origin:"https://ejemplo.invalid"},data:{confirmacion:"RESTABLECER DEMO"}});expect(crossOrigin.status()).toBe(403);
});

test("error útil y reintento",async({page})=>{
  let broken=true;
  await page.route("**/api/v1/kpis?**",route=>broken?route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"Motor temporalmente no disponible."})}):route.continue());
  await page.goto("/");
  await expect(page.locator(".error-state")).toContainText("Motor temporalmente no disponible");
  broken=false;
  await page.getByRole("button",{name:"Reintentar",exact:true}).click();
  await expect(page.getByTestId("kpi-ventas")).toBeVisible();
});

test("capturas de pantallas reales y accesibilidad automatizada",async({page},testInfo)=>{
  test.setTimeout(240_000);
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  const sizes=[{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}];
  const routes=["/","/one-search","/medicion","/creatividad","/experimentos","/escenarios","/fiabilidad"];
  for(const size of sizes){
    await page.setViewportSize(size);
    for(const route of routes){
      await page.goto(route);
      await expect(page.locator(".loading")).toHaveCount(0);
      if(route==="/")await expect(page.locator("canvas")).toHaveCount(2);
      await page.evaluate(()=>document.fonts.ready);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
      expect(overflow,`Desbordamiento en ${route} a ${size.width}`).toBeFalsy();
      await page.screenshot({path:path.join(dir,`${route==="/"?"centro":route.slice(1)}-${size.width}.png`),fullPage:true});
      const results=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
      const report=results.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>n.target)}));
      await testInfo.attach(`accesibilidad-${route}-${size.width}`,{body:JSON.stringify(report,null,2),contentType:"application/json"});
      expect.soft(report,`Accesibilidad ${route} ${size.width}`).toEqual([]);
    }
  }
});

test("navegación móvil: apertura, teclado y contexto",async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto("/");
  await expect(page.getByTestId("kpi-ventas")).toBeVisible();
  await page.getByLabel("Abrir navegación").click();
  await expect(page.getByRole("dialog",{name:"Navegación",exact:true})).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(page.getByLabel("Abrir navegación")).toBeFocused();
  await page.getByLabel("Abrir navegación").click();
  await page.getByRole("dialog").getByRole("link",{name:"One Search",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Una búsqueda. Una visión."})).toBeVisible();
});
