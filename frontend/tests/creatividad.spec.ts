import {expect,test} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {mkdir} from "node:fs/promises";
import path from "node:path";

const percentage=(v:number)=>new Intl.NumberFormat("es-ES",{style:"percent",minimumFractionDigits:2,maximumFractionDigits:2}).format(v);
const number=(v:number)=>new Intl.NumberFormat("es-ES",{maximumFractionDigits:0}).format(v);

test("creatividad: contexto → tres composiciones → selección persistente y método",async({page,request})=>{
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  const original=await (await request.get("/api/v1/contexto")).json();
  const model=await (await request.get("/api/v1/creativos/pretest")).json();
  await page.goto("/creatividad");
  await page.getByRole("link",{name:"Preparar pretest",exact:true}).click();
  await expect(page.getByTestId("variante-pretest")).toHaveCount(3);
  await expect.poll(()=>page.getByTestId("variante-pretest").locator("img").evaluateAll(imgs=>imgs.every(el=>(el as HTMLImageElement).complete&&(el as HTMLImageElement).naturalWidth>0))).toBeTruthy();
  await page.getByLabel("Objetivo del brief (obligatorio)",{exact:true}).fill(`QA creatividad ${Date.now()}`);
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page).toHaveURL(/evaluacion=pretest-/);
  const id=new URL(page.url()).searchParams.get("evaluacion")!;
  const evaluation=await (await request.get("/api/v1/creativos/evaluaciones/"+id)).json();
  await expect(page.getByTestId("ctr-pretest")).toHaveText(percentage(evaluation.referencia.ctr));
  await expect(page.getByTestId("clics-pretest")).toHaveText(number(evaluation.referencia.clics_esperados));
  await expect(page.getByText("Sin ganador predictivo",{exact:true})).toBeVisible();
  expect(evaluation.ganador).toBeNull();
  expect(new Set(evaluation.variantes.map((v:{ctr_referencia:number})=>v.ctr_referencia)).size).toBe(1);
  await page.getByRole("button",{name:"Guardar propuesta 2",exact:true}).click();
  await expect(page.getByTestId("seleccion-creativa")).toContainText("Hipótesis creativa guardada");
  await expect(page).toHaveURL(/seleccion=sel-creativa-/);
  const selection=new URL(page.url()).searchParams.get("seleccion")!;
  const s=await (await request.get("/api/v1/creativos/selecciones/"+selection)).json();
  expect(s.pretest_id).toBe(id);expect(s.multiplicador_demanda).toBe(1);expect(s.efecto_identificado).toBeFalsy();
  await page.reload();
  await expect(page.getByTestId("seleccion-creativa")).toContainText(selection);
  await page.getByRole("button",{name:"Método y validación",exact:true}).click();
  await expect(page.getByRole("dialog")).toContainText("Las campañas y composiciones no cruzan la frontera");
  await expect(page.getByRole("region",{name:"Validación del modelo creativo",exact:true})).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button",{name:"Método y validación",exact:true})).toBeFocused();
  expect((await (await request.get("/api/v1/creativos/pretest")).json()).modelo.id).toBe(model.modelo.id);
  expect((await (await request.get("/api/v1/contexto")).json()).checksum).toBe(original.checksum);
  expect(errors).toEqual([]);
});

test("creatividad: filtros, estado vacío y contexto global sin reentrenar",async({page,request})=>{
  const original=await (await request.get("/api/v1/creativos/pretest")).json();
  await page.goto("/creatividad");
  await page.getByLabel("Canal",{exact:true}).selectOption("meta");
  await page.getByLabel("Categoría",{exact:true}).selectOption("hogar");
  await page.getByLabel("Audiencia",{exact:true}).selectOption("Cohorte 01");
  await expect(page.locator(".creative-card")).toHaveCount(4);
  await page.getByLabel("Ordenar biblioteca",{exact:true}).selectOption("ctr");
  await page.getByLabel("Objetivo de campaña",{exact:true}).selectOption("Captación");
  await expect(page.getByText("No hay activos observados para estos filtros.",{exact:true})).toBeVisible();
  await page.getByLabel("Objetivo de campaña",{exact:true}).selectOption("");
  await expect(page.locator(".creative-card")).toHaveCount(4);
  await page.getByRole("link",{name:"Preparar pretest",exact:true}).click();
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page).toHaveURL(/evaluacion=pretest-/);
  const id=new URL(page.url()).searchParams.get("evaluacion")!;
  await page.getByLabel("Periodo global").selectOption("90");
  await expect(page).toHaveURL(new RegExp(`dias=90.*evaluacion=${id}`));
  await expect(page.getByTestId("ctr-pretest")).toBeVisible();
  expect((await (await request.get("/api/v1/creativos/pretest")).json()).modelo.id).toBe(original.modelo.id);
});

test("creatividad: error recuperable, parámetros conservados y validación nativa",async({page})=>{
  let broken=true;
  await page.route("**/api/v1/creativos/evaluar",r=>broken?r.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"No se ha podido guardar el pretest."})}):r.continue());
  await page.goto("/creatividad?vista=pretest");
  await page.getByLabel("Impresiones de referencia",{exact:true}).fill("20000");
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("No se ha podido guardar");
  await expect(page.locator(".form-error")).toBeFocused();
  await expect(page.getByLabel("Impresiones de referencia",{exact:true})).toHaveValue("20000");
  broken=false;
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page.getByTestId("clics-pretest")).toBeVisible();
  await page.getByLabel("Frecuencia prevista",{exact:true}).fill("0");
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  expect(await page.getByLabel("Frecuencia prevista",{exact:true}).evaluate((el:HTMLInputElement)=>el.validity.rangeUnderflow)).toBeTruthy();
  await page.getByLabel("Frecuencia prevista",{exact:true}).fill("9");
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page.getByText("Frecuencia fuera del rango de entrenamiento:",{exact:false})).toBeVisible();
});

test("creatividad: revisión visual de pretest en cuatro tamaños y activos de tres perfiles",async({page})=>{
  test.setTimeout(150_000);
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  await page.goto("/creatividad?vista=pretest");
  await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
  await expect(page.getByTestId("ctr-pretest")).toBeVisible();
  for(const size of [{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}]){
    await page.setViewportSize(size);await page.evaluate(()=>document.fonts.ready);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.screenshot({path:path.join(dir,`creatividad-pretest-${size.width}.png`),fullPage:true});
    const result=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }
  await page.setViewportSize({width:1440,height:900});
  for(const profile of ["moda","belleza"]){
    await page.getByLabel("Perfil de partida",{exact:true}).selectOption(profile);
    await page.getByRole("button",{name:"Evaluar tres composiciones",exact:true}).click();
    await expect(page.getByTestId("variante-pretest").first()).toContainText(profile);
    await expect.poll(()=>page.getByTestId("variante-pretest").locator("img").evaluateAll(imgs=>imgs.every(el=>(el as HTMLImageElement).complete&&(el as HTMLImageElement).naturalWidth>0))).toBeTruthy();
    await page.locator(".creative-comparison").screenshot({path:path.join(dir,`creatividad-${profile}.png`)});
  }
});
