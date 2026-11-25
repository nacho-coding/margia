import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const money=(v:number)=>new Intl.NumberFormat("es-ES",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(v);

test("radar → hipótesis Search → recorte, costes, no actuar y guardado",async({page,request})=>{
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  const radar=await (await request.get("/api/v1/oportunidades")).json();
  await page.goto("/");
  await expect(page.getByTestId("impacto-radar")).toHaveText(money(radar.filas[0].impacto));
  await page.getByRole("link",{name:"Explorar One Search",exact:true}).click();
  await expect(page).toHaveURL(new RegExp(radar.filas[0].id));
  await expect(page.getByRole("heading",{name:"¿Qué cambia al reducir SEM marca?",exact:true})).toBeFocused();
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toHaveText(money(radar.filas[0].impacto));
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByRole("status").filter({hasText:"resultado reproducible reutilizado"})).toBeVisible();
  await page.getByLabel("Cuota de plataforma del periodo (€)",{exact:true}).fill("100000");
  await expect(page.getByText("Parámetros modificados.",{exact:false})).toBeVisible();
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByText("Mantener; el beneficio o el riesgo",{exact:false})).toBeVisible();
  await expect(page.getByTestId("delta-search")).toContainText("-");
  await page.getByLabel("La cuota ya se paga en ambas opciones",{exact:true}).check();
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toHaveText(money(radar.filas[0].impacto));
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("0");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toHaveText(money(0));
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("100");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByText("Recorte fuera del soporte experimental",{exact:false})).toBeVisible();
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("101");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  expect(await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).evaluate((el:HTMLInputElement)=>el.validity.rangeOverflow)).toBeTruthy();
  expect(errors).toEqual([]);
});

test("Search: históricos consultables, teclado, contexto y mercado como hipótesis",async({page})=>{
  await page.goto("/one-search");
  await page.getByRole("button",{name:"Revisar evidencia de marca",exact:true}).click();
  await expect(page.getByRole("dialog")).toContainText("La tasa de recuperación SEO/directo no está identificada");
  await page.locator(".historical-button").first().click();
  await expect(page.getByRole("region",{name:"Observaciones del experimento",exact:true}).getByRole("row")).toHaveCount(49);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button",{name:"Revisar evidencia de marca",exact:true})).toBeFocused();
  await page.getByLabel("Mercado global").selectOption("m01");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByText("Estimación agrupada nacional aplicada",{exact:false})).toBeVisible();
});

test("Search: error de cálculo conserva formulario y permite reintento",async({page})=>{
  let broken=true;
  await page.route("**/api/v1/busqueda/simular?**",r=>broken?r.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"No se ha podido guardar la evaluación."})}):r.continue());
  await page.goto("/one-search");
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("25");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("No se ha podido guardar");
  await expect(page.locator(".form-error")).toBeFocused();
  await expect(page.getByLabel("Recorte de SEM marca (%)",{exact:true})).toHaveValue("25");
  broken=false;
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toBeVisible();
});

test("Search: revisión visual de resultado en cuatro tamaños y escenario negativo",async({page})=>{
  test.setTimeout(150_000);
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  await page.goto("/one-search");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toBeVisible();
  await expect(page.locator("canvas")).toHaveCount(2);
  for(const size of [{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}]){
    await page.setViewportSize(size);
    await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>resolve())));
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.locator("#simulador").screenshot({path:path.join(dir,`search-evaluacion-${size.width}.png`)});
    const axe=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }
  await page.setViewportSize({width:1440,height:900});
  await page.getByLabel("Cuota de plataforma del periodo (€)",{exact:true}).fill("100000");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  await expect(page.getByTestId("delta-search")).toContainText("-");
  await page.locator("#simulador").screenshot({path:path.join(dir,"search-negativo.png")});
});
