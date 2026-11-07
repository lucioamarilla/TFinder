import { test, expect } from '@playwright/test'

test('F6 smoke: login real y mesas visible', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/mesas')
  await expect(page).toHaveURL(/\/mesas$/)
  await expect(page.getByRole('link', { name: /Tu perfil/i })).toBeVisible()
  await expect(page.getByText('Explorar mesas')).toBeVisible()
})

test('E2E: mesas listadas tras login', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/mesas')
  await expect(page.getByText('Explorar mesas')).toBeVisible()
})

test('E2E: mesas muestra listado para usuario autenticado', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.getByLabel('Email').fill('gm@tfinder.dev')
  await page.getByLabel('Contraseña').fill('DemoTFinder123!')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await page.waitForURL('**/mesas')
  await expect(page.getByRole('link', { name: 'Publicá tu campaña' })).toBeVisible()
})