import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

test("MMM: cifras de API, descomposición, soporte y metodología accesibles", async({page,request})=>{
  const errors:string[]=[];
  page.on("pageerror", error=>errors.push(error.message));
  const data=await (await request.get("/api/v1/modelos/mmm?dias=28")).json();
  await page.goto("/medicion");
  await expect(page.getByTestId("modelo-nacional")).toBeVisible();
  const percent=new Intl.NumberFormat("es-ES",{style:"percent",minimumFractionDigits:2,maximumFractionDigits:2});
  await expect(page.getByTestId("wape-mmm")).toHaveText(percent.format(data.modelo.diagnostico.holdout.wape));
  await expect(page.locator("canvas")).toHaveCount(2);
  await page.getByRole("button",{name:"Descomposición",exact:true}).click();
  await expect(page.getByRole("button",{name:"Descomposición",exact:true})).toHaveAttribute("aria-pressed","true");
  await page.getByText("Ver datos de las semanas",{exact:true}).click();
  const weeks=page.getByRole("region",{name:"Semanas del modelo",exact:true});
  await expect(weeks.getByRole("row")).toHaveCount(5);
  await expect(weeks).toContainText(new Intl.NumberFormat("es-ES").format(data.serie[0].observado));
  await page.getByLabel("Canal del modelo").selectOption("tv");
  await expect(page.getByRole("img",{name:/Curva semanal de TV/})).toBeVisible();
  await page.getByText("Ver datos de la curva y marginal",{exact:true}).click();
  const curve=page.getByRole("region",{name:"Datos de la curva",exact:true});
  await expect(curve).toContainText("Extrapolación");
  await expect(curve).toContainText("Observado en train");
  const dir=path.resolve("../artifacts/qa");
  await mkdir(dir,{recursive:true});
  await page.screenshot({path:path.join(dir,"mmm-descomposicion.png"),fullPage:true});
  await page.getByRole("button",{name:"Metodología del MMM",exact:true}).click();
  await expect(page.getByRole("dialog")).toContainText(data.modelo.id);
  await expect(page.getByRole("dialog")).toContainText("La buena predicción conjunta no garantiza un reparto estable.");
  await page.screenshot({path:path.join(dir,"mmm-metodologia.png"),fullPage:true});
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button",{name:"Metodología del MMM",exact:true})).toBeFocused();
  expect(errors).toEqual([]);
});

test("MMM: periodo visual no reentrena y mercado no fabrica un modelo local",async({page,request})=>{
  const before=await (await request.get("/api/v1/modelos")).json();
  await page.goto("/medicion");
  await expect(page.getByTestId("modelo-nacional")).toBeVisible();
  await page.getByLabel("Periodo global").selectOption("365");
  await expect(page.getByText("52 semanas completas del periodo",{exact:false})).toBeVisible();
  await page.getByLabel("Mercado global").selectOption("m01");
  await expect(page.getByText("El MMM es nacional y no se desagrega por mercado.",{exact:false})).toBeVisible();
  await expect(page.getByTestId("modelo-nacional")).toHaveCount(0);
  await expect(page.getByTestId("wape-mmm")).toHaveCount(0);
  const local=await (await request.get("/api/v1/medios?dias=365&mercado=m01")).json();
  const euros=new Intl.NumberFormat("es-ES",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  await expect(page.getByRole("region",{name:"Tabla de medios",exact:true})).toContainText(euros.format(local.filas[0].inversion));
  await page.getByRole("link",{name:"Explorar One Search",exact:true}).click();
  await expect(page).toHaveURL(/mercado=m01/);
  const after=await (await request.get("/api/v1/modelos")).json();
  expect(after.filas[0]).toEqual(before.filas[0]);
});

test("MMM: error de modelo permite reintentar y conserva la atribución",async({page})=>{
  let broken=true;
  await page.route("**/api/v1/modelos/mmm?**",route=>broken?route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"El modelo aún no está preparado."})}):route.continue());
  await page.goto("/medicion");
  await expect(page.locator(".error-state")).toContainText("El modelo aún no está preparado.");
  await expect(page.getByRole("region",{name:"Tabla de medios",exact:true})).toBeVisible();
  broken=false;
  await page.getByRole("button",{name:"Reintentar",exact:true}).click();
  await expect(page.getByTestId("modelo-nacional")).toBeVisible();
});
