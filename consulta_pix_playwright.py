
import asyncio
from playwright.async_api import async_playwright
from fpdf import FPDF

async def main():
    # Lê os CNPJs do arquivo
    with open("lista_cnpjs.txt", "r") as f:
        cnpjs = [linha.strip() for linha in f.readlines()]

    resultados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.mercadopago.com.br/money-out/transfer/pix-methods#from=dashboard&flow_detail=new_transfer")
        input("🔐 Faça login no Mercado Pago e pressione Enter para continuar...")

        for cnpj in cnpjs:
            await page.goto("https://www.mercadopago.com.br/money-out/transfer/pix-methods#from=dashboard&flow_detail=new_transfer")
            await page.wait_for_timeout(3000)

            try:
                # Abre o seletor de chave
                await page.locator(".dropdown").click()
                await page.get_by_text("CNPJ").click()

                campo = page.locator("input[placeholder='00.000.000/0000-00']")
                await campo.fill(cnpj)
                await page.get_by_role("button", name="Buscar conta").click()

                await page.wait_for_timeout(4000)

                try:
                    banco = await page.locator("div:has-text('Banco') + div").text_content()
                    nome_banco = banco.strip() if banco else "Banco não identificado"
                except:
                    nome_banco = "Banco não identificado"
            except Exception as e:
                nome_banco = f"Erro: {str(e)}"

            resultados.append(f"{cnpj} - {nome_banco}")
            print(f"{cnpj} - {nome_banco}")

        await browser.close()

    # Geração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Consulta de CNPJs - Chave Pix", ln=True, align="C")
    pdf.ln(10)

    for linha in resultados:
        pdf.cell(200, 10, txt=linha, ln=True)

    pdf.output("resultados_pix_consulta.pdf")
    print("\n✅ Consulta finalizada com sucesso!")
    print("📄 PDF gerado: resultados_pix_consulta.pdf")

if __name__ == "__main__":
    asyncio.run(main())
