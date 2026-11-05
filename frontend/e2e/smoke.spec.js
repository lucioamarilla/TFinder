import { test, expect } from '@playwright/test'

test('F6 smoke: login real y feed visible', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/feed')
  await expect(page).toHaveURL(/\/feed$/)
  await expect(page.getByRole('link', { name: /Tu perfil/i })).toBeVisible()
})

test('E2E: mesas listadas tras login', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/feed')
  await page.goto('http://localhost:5173/mesas')
  await expect(page.getByText('Explorar mesas')).toBeVisible()
})

test('E2E: feed muestra composer para usuario autenticado', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/feed')
  await expect(page.getByRole('button', { name: 'Publicar' })).toBeVisible()
})
