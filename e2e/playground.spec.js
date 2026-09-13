const { test, expect } = require('@playwright/test');

test('executa código em português e exibe o Python canônico', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await expect(page.locator('#btn-executar')).toBeEnabled();

  await page.locator('#code-editor').fill('mostre("teste E2E")');
  await page.getByRole('button', { name: /Executar/ }).click();

  await expect(page.locator('#terminal-output')).toContainText('teste E2E', {
    timeout: 15000,
  });

  await page.getByRole('tab', { name: /Python Canônico/ }).click();
  await expect(page.locator('#canonico-output')).toContainText('print');
  await expect(page.locator('#canonico-output')).toContainText('teste E2E');
});

test('mantém syntax highlight seguro e atualizado ao inserir Tab', async ({ page }) => {
  await page.goto('/');

  const editor = page.locator('#code-editor');
  const highlight = page.locator('#syntax-highlight-code');
  await editor.fill('se verdadeiro:\nmostre("<tag>")');
  await editor.press('End');
  await editor.press('Tab');

  await expect(editor).toHaveValue('se verdadeiro:\nmostre("<tag>")    ');
  const highlightHtml = await highlight.evaluate((element) => element.innerHTML);
  expect(highlightHtml).toContain('&lt;tag&gt;');
  expect(highlightHtml).toContain('syntax-keyword');
});
