# login_b4you_playwright.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import pyautogui
import time
import sys
import os, glob  # <-- adicionado
 
# ----- CONFIG -----
URL = "https://painel.b4youlog.com/autenticacao/index?ReturnUrl=%2Fhome%2Fmenu"
LOGIN = "Diego_pharmaesthetics"     # substitua
SENHA  = "B4you10&@"    # substitua
WAIT_NETWORK_TIMEOUT = 15000  # ms
SLOW_MO_MS = 100             # ver as ações (100ms entre ações)
 
# Pasta de origem dos arquivos para upload (compartilhada)
BASE_DIR = r"O:\Logística\17- Colaboradores - Pastas\6 - Caetano\TESTE"
# -------------------
 
def run():
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False, slow_mo=SLOW_MO_MS)  # headful para você ver
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
 
            # Navega para a página de login
            page.goto(URL, wait_until="domcontentloaded")
            # garante que os inputs existam
            page.wait_for_selector('input[name="login"]', timeout=5000)
            page.wait_for_selector('input[name="senha"]', timeout=5000)
 
            # Preenche login e senha
            page.fill('input[name="login"]', LOGIN)
            page.fill('input[name="senha"]', SENHA)
 
            # Opcional: mover o mouse do sistema para "mostrar" atividade (pode ser útil visualmente)
            try:
                pyautogui.moveTo(600, 300, duration=0.3)
            except Exception:
                pass
 
            # Clica no botão "Logar"
            try:
                page.click("button[type='submit'].btn.btn-primary", timeout=3000)
            except PWTimeoutError:
                page.click("button:has-text('Logar')")
 
            # Aguarda a navegação/requests ficarem quiescentes (networkidle)
            try:
                page.wait_for_load_state("networkidle", timeout=WAIT_NETWORK_TIMEOUT)
            except PWTimeoutError:
                print("Aviso: espera por networkidle estourou o timeout.", file=sys.stderr)
           
            # Abre o dropdown "Pedidos"
            page.click("a.nav-link.dropdown-toggle:has-text('Pedidos')")
            # Clica na opção "Novo - a partir do XML"
            page.click("a.dropdown-item.text-primary[href='/nfeToPedido']")
 
            # Aguarda carregamento da nova página
            try:
                page.wait_for_load_state("networkidle", timeout=WAIT_NETWORK_TIMEOUT)
            except PWTimeoutError:
                print("Aviso: espera por networkidle após navegação estourou o timeout.", file=sys.stderr)
 
            # ------------------ [NOVO] Upload dos arquivos ------------------
            # Localiza arquivo XML (aceita .xml e também .xlm caso exista)
            xml_candidates = glob.glob(os.path.join(BASE_DIR, "*.xml"))
            xml_file = max(xml_candidates, key=os.path.getmtime) if xml_candidates else None
 
            # Localiza PDFs e distribui por nome
            pdfs = glob.glob(os.path.join(BASE_DIR, "*.pdf"))
            # Usa ocorrência no nome do arquivo para mapear destinos
            nf_pdf  = next((f for f in pdfs if "NF"  in os.path.basename(f).upper()), None)
            etq_pdf = next((f for f in pdfs if "ETQ" in os.path.basename(f).upper()), None)
            out_pdfs = [f for f in pdfs if "OUT" in os.path.basename(f).upper()]
 
            # page.fill('input[name="numeroDoPedido"]', f"{nf_pdf}")
 
            # Preenche os inputs (cada um é aguardado antes)
            if xml_file:
                page.wait_for_selector("#xml-file", timeout=5000)
                page.set_input_files("#xml-file", xml_file)
 
            if nf_pdf:
                page.wait_for_selector("#arquivoNfe", timeout=5000)
                page.set_input_files("#arquivoNfe", nf_pdf)
 
            if etq_pdf:
                page.wait_for_selector("#label-file", timeout=5000)
                page.set_input_files("#label-file", etq_pdf)
 
            if out_pdfs:
                page.wait_for_selector("#other-docs", timeout=5000)
                page.set_input_files("#other-docs", out_pdfs)  # multiple
            # ---------------- [FIM NOVO BLOCO] ------------------------------
 
            # Aguarda mais 10 segundos para você checar visualmente
            print("Página de 'Novo - a partir do XML' carregada e arquivos anexados — aguardando 10 segundos...")
            time.sleep(10)
 
            # Fecha
            context.close()
            browser.close()
            try:
                pyautogui.alert(text="Script finalizado e navegador fechado.", title="Playwright", button="OK")
            except Exception:
                pass
 
    except Exception as e:
        print("Erro durante o processo:", e, file=sys.stderr)
        raise
 
if __name__ == "__main__":
    run()