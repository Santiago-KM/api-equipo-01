# Práctica 1: Liberación y despliegue continuo con Cloudflare Workers

Equipo: 01. Worker: `api-equipo-01`. Versión inicial: `1.0.0`.

## Integrantes y datos pendientes

- Integrantes: Santiago Castillo, Ivan Alejandro, Jose Carlos y Rosa Elena.
- GitHub: USUARIO (pendiente de proporcionar).
- workers.dev: equipochido-idgs10a.

URLs de los despliegues manuales confirmados por la salida de Wrangler proporcionada por el equipo:

- Staging: https://api-equipo-01-staging.equipochido-idgs10a.workers.dev
- Producción: https://api-equipo-01.equipochido-idgs10a.workers.dev

El subdominio real ya está configurado en el pipeline y en el PDF. Falta confirmar el usuario de GitHub y configurar secretos y environments antes del primer push.

## Ejecución local

Usar Node 22 (`.nvmrc`). En esta carpeta también se preparó un ejecutable local de Node 22, ignorado por Git:

```powershell
$env:PATH = "$PWD\.tools\node22\node_modules\node\bin;$env:PATH"
node --version
npm ci
npm test
```

`/health` devuelve estado, ambiente y versión; `/error` lanza el error simulado; las demás rutas devuelven el saludo.

## Primeros despliegues: realizar personalmente

```powershell
npx wrangler login
npx wrangler deploy --env staging
npx wrangler deploy
```

Elegir el subdominio workers.dev cuando Cloudflare lo solicite y conservar las URLs reales. Si la cuenta requiere activarlo desde el panel, hacerlo en Workers & Pages. Abrir `/health` en ambos ambientes y verificar `version: "1.0.0"` y sus ambientes respectivos.

En Cloudflare: perfil > API Tokens > Create Token > plantilla **Edit Cloudflare Workers**. Seleccionar la cuenta que contiene los Workers y crear el token. Obtener el Account ID desde el panel de esa misma cuenta. Introducir ambos valores directamente en GitHub; no guardarlos en archivos ni en commits.

## GitHub: comandos exactos para PowerShell

`gh` no estaba disponible en el PATH al preparar el proyecto. Instalar GitHub CLI y abrir una terminal nueva:

```powershell
winget install --id GitHub.cli -e
gh auth login
gh auth status
Set-Location 'C:\Users\scast\Desktop\Gestion'
$githubUser = gh api user --jq .login
gh repo create "$githubUser/api-equipo-01" --public --source . --remote origin
gh api --method PUT "repos/$githubUser/api-equipo-01/environments/staging"
$reviewerId = gh api user --jq .id
$productionRules = @{ reviewers = @(@{ type = 'User'; id = [long]$reviewerId }); prevent_self_review = $false; can_admins_bypass = $false } | ConvertTo-Json -Depth 5
$productionRules | gh api --method PUT "repos/$githubUser/api-equipo-01/environments/production" --input -
gh secret set CLOUDFLARE_API_TOKEN --repo "$githubUser/api-equipo-01"
gh secret set CLOUDFLARE_ACCOUNT_ID --repo "$githubUser/api-equipo-01"
gh secret list --repo "$githubUser/api-equipo-01"
gh api "repos/$githubUser/api-equipo-01/environments/production"
```

Los comandos `gh secret set` solicitan cada valor de forma interactiva. Verificar que production incluya `required_reviewers`. Si falta esa opción, confirmar que el repositorio sea público y que la respuesta de la API no haya sido un error. Se permite aprobar al propio usuario iniciador; el revisor configurado debe ser tu usuario real.

**Detenerse aquí y confirmar a Codex que los dos secretos están configurados. No ejecutar el primer push antes de esa confirmación.** Una vez confirmados los secretos, reemplazados los datos pendientes y verificada la regla de aprobación:

```powershell
git add README.md .github/workflows/cd.yml entregable/Practica1.pdf
git diff --cached
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) { git commit -m "Configura datos reales del equipo y despliegue" }
git push -u origin main
```

Si el repositorio ya existe, comprobarlo con `gh repo view "$githubUser/api-equipo-01"` y agregar el remoto con `git remote add origin "https://github.com/$githubUser/api-equipo-01.git"` únicamente si `origin` todavía no existe.

## Pipeline

Cada push a `main` ejecuta `pruebas` en Ubuntu con Node 22: checkout, `npm ci` y `npm test`. Si pasa, `staging` instala dependencias y despliega con Wrangler usando los secretos de GitHub; comprueba `/health` con curl y reintentos. Después `produccion` espera la aprobación del environment `production`, despliega y ejecuta su smoke test.

La aprobación depende de configurar **Required reviewers** en GitHub; el YAML por sí solo no impone esa regla. Cuando Actions muestre producción pendiente, abrir **Review deployments**, seleccionar `production` y aprobar. Capturar esa pantalla antes de aprobar y el pipeline completo cuando termine en verde.

## Versión 1.1.0 y rollback

Solo después de confirmar que el pipeline v1.0.0 está en verde, Codex cambiará `VERSION` en `src/index.js` a `1.1.0`, probará, hará commit y push. Aprobar otra vez producción cuando GitHub lo solicite. Abrir el `/health` real de producción y capturar `version: "1.1.0"` antes de revertir.

Ejecutar personalmente desde esta carpeta:

```powershell
npx wrangler rollback
# Revisar que el destino corresponde a 1.0.0 y confirmar el rollback.
# Abrir https://api-equipo-01.equipochido-idgs10a.workers.dev/health y capturar version 1.0.0.
npx wrangler deployments list
```

El rollback sin `--env` afecta producción. Para staging, si se necesitara: `npx wrangler rollback --env staging`. El rollback remoto no modifica el código del repositorio; otro push con VERSION 1.1.0 volvería a desplegar esa versión.

## Evidencia y diagnóstico

Verificación local realizada: Node v22.23.5, Wrangler 4.166.0, `npm ci` correcto y 2/2 pruebas aprobadas. La compilación `wrangler deploy --dry-run` pasó para producción y staging con sus respectivos valores de AMBIENTE; no publicó ningún Worker. El PDF fue renderizado e inspeccionado: tres páginas y cuatro marcadores para capturas.

`entregable/Practica1.pdf` contiene tres páginas con espacios explícitos para las cuatro capturas requeridas. Es una plantilla de evidencia: no acredita despliegues ni resultados remotos todavía. `entregable/generar_pdf.py` permite regenerarla y completar integrantes y subdominio mediante argumentos `--integrantes` y `--subdominio`.

- `npm ci` falla: comprobar que `package-lock.json` esté versionado y coincida con package.json.
- Autenticación falla: revisar nombres y alcance de `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID`.
- Falta Required reviewers: verificar visibilidad pública del repositorio y respuesta de GitHub.
- Smoke test falla: comprobar URL real, subdominio y que el despliegue haya terminado.
- Error 1027: límite diario gratuito; se reinicia a medianoche UTC.

Referencias: [ambientes de Wrangler](https://developers.cloudflare.com/workers/wrangler/environments/), [environments de GitHub](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), [aprobación de despliegues](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments).
