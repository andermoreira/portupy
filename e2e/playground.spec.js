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

  await page.getByRole('tab', { name: /Lado a Lado/ }).click();
  await expect(page.locator('#bilingue-output')).toContainText('Português');
  await expect(page.locator('#bilingue-output')).toContainText('Python Canônico');

  await page.getByRole('tab', { name: /Python Canônico/ }).click();
  await expect(page.locator('#canonico-output')).toContainText('print');
  await expect(page.locator('#canonico-output')).toContainText('teste E2E');

  // A aba canônica também recebe realce de sintaxe (reaproveitado do editor).
  const canonicoHtml = await page
    .locator('#canonico-output')
    .evaluate((el) => el.innerHTML);
  expect(canonicoHtml).toContain('syntax-builtin'); // 'print'
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

test('executa com os assets locais mesmo sem acesso à CDN', async ({ page }) => {
  const cdnRequests = [];
  page.on('request', (request) => {
    if (request.url().includes('cdn.jsdelivr.net')) {
      cdnRequests.push(request.url());
    }
  });
  await page.route('https://cdn.jsdelivr.net/**', (route) => route.abort());

  await page.goto('/');

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await page.locator('#code-editor').fill('mostre("offline")');
  await page.getByRole('button', { name: /Executar/ }).click();
  await expect(page.locator('#terminal-output')).toContainText('offline', {
    timeout: 15000,
  });
  expect(cdnRequests).toHaveLength(0);
});

test('reabre o shell pelo Service Worker sem rede', async ({ page, context }) => {
  await page.goto('/');
  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  await context.setOffline(true);
  await page.reload();

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await page.locator('#code-editor').fill('mostre("reaberto offline")');
  await page.getByRole('button', { name: /Executar/ }).click();
  await expect(page.locator('#terminal-output')).toContainText('reaberto offline', {
    timeout: 15000,
  });
});

test('exibe diagnóstico de sintaxe e alterna abas pelo teclado', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await page.locator('#code-editor').fill('se verdadeiro\n    passe');
  await page.getByRole('button', { name: /Executar/ }).click();

  await expect(page.locator('#output-status')).toHaveText('Status: Erro (1)', {
    timeout: 15000,
  });
  await expect(page.locator('#terminal-output')).toContainText('dois pontos');

  const terminalTab = page.getByRole('tab', { name: /Terminal/ });
  await terminalTab.focus();
  await terminalTab.press('ArrowRight');
  await expect(page.getByRole('tab', { name: /Lado a Lado/ })).toHaveAttribute(
    'aria-selected',
    'true'
  );
});

test('mantém o playground utilizável em viewport estreito', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  const dimensoes = await page.evaluate(() => ({
    larguraDocumento: document.documentElement.scrollWidth,
    larguraViewport: document.documentElement.clientWidth,
  }));
  expect(dimensoes.larguraDocumento).toBeLessThanOrEqual(dimensoes.larguraViewport);
  await expect(page.locator('#select-exemplo')).toBeVisible();
  await expect(page.locator('#code-editor')).toBeVisible();
});

test('explica de forma amigável que a entrada com leia não funciona no navegador', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#status-text')).toHaveText('Python Pronto (Wasm)', {
    timeout: 120000,
  });
  await expect(page.locator('#btn-executar')).toBeEnabled();

  await page.locator('#code-editor').fill('nome = leia("Seu nome: ")\nmostre(nome)');
  await page.getByRole('button', { name: /Executar/ }).click();

  // Em vez de um EOFError cru, o playground mostra a explicação em português.
  await expect(page.locator('#terminal-output')).toContainText(
    'não funciona no playground',
    { timeout: 15000 }
  );
  await expect(page.locator('#terminal-output')).not.toContainText(
    'ainda sem tradução'
  );
  await expect(page.locator('#terminal-output')).not.toContainText(
    'EntradaIndisponivelError'
  );
});
