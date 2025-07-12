
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)
resultados = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    cnpjs = request.json['cnpjs'].splitlines()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    output = loop.run_until_complete(processar_consultas(cnpjs))
    return output

@app.route('/gerar_pdf')
def gerar_pdf():
    global resultados
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Consulta de CNPJs - PIX", ln=True, align="C")
    pdf.ln(10)

    for linha in resultados:
        pdf.cell(200, 10, txt=linha, ln=True)

    pdf.output("resultados_pix.pdf")
    return send_file("resultados_pix.pdf", as_attachment=True)

async def processar_consultas(cnpjs):
    global resultados
    resultados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.mercadopago.com.br/money-out/transfer/pix-methods#from=dashboard&flow_detail=new_transfer")
        input("🔐 Faça login no Mercado Pago e pressione ENTER aqui no terminal para continuar...")

        for cnpj in cnpjs:
            await page.goto("https://www.mercadopago.com.br/money-out/transfer/pix-methods#from=dashboard&flow_detail=new_transfer")
            await page.wait_for_timeout(3000)

            try:
                await page.locator(".dropdown").click()
                await page.get_by_text("CNPJ").click()
                campo = page.locator("input[placeholder='00.000.000/0000-00']")
                await campo.fill(cnpj.strip())
                await page.get_by_role("button", name="Buscar conta").click()
                await page.wait_for_timeout(3000)

                try:
                    banco = await page.locator("div:has-text('Banco') + div").text_content()
                    nome_banco = banco.strip() if banco else "Banco não identificado"
                except:
                    nome_banco = "Banco não identificado"
            except Exception as e:
                nome_banco = f"Erro: {str(e)}"

            resultados.append(f"{cnpj.strip()} - {nome_banco}")
            print(f"{cnpj.strip()} - {nome_banco}")

        await browser.close()

    return "\n".join(resultados)

if __name__ == '__main__':
    app.run(debug=True)
