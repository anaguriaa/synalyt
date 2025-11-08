# app.py
# Synalyt - Streamlit app com SQLite, integrações demo, limite Free e pagamento simulado
# Salve este arquivo em sua pasta do projeto e rode: streamlit run app.py

# app.py
# Synalyt - App completo com logo, login, SQLite, integrações demo, limite Free e pagamento simulado
# Rode: streamlit run app.py

# -------------------------------
# app.py - Synalyt SaaS Completo
# -------------------------------
# app.py - Synalyt completo (Streamlit) com Mercado Pago + SMTP Hotmail
# Requisitos: ver instruções no README (python-dotenv, mercadopago, streamlit, etc.)

# app.py - Synalyt (UI melhorada + envio via SMTP (Brevo/Outros) + downloads + card flutuante com X)
# Instruções: crie .env com SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, MERCADO_PAGO_* (opcional).
# Rodar: streamlit run app.py

# app.py - Synalyt completo (UI melhorada, floating card funcional, downloads, e-mail real, Mercado Pago)
# Requisitos: streamlit, pandas, matplotlib, reportlab, python-dotenv, bcrypt, mercadopago, xlsxwriter, openpyxl
# Rode: streamlit run app.py

# app_synalyt_final.py
# app_synality.py
import os
from pathlib import Path
import time
import datetime
import sqlite3
from io import BytesIO
import uuid
import secrets

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv


import streamlit as st

# CONFIG + CSS
st.set_page_config(page_title="Synality", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
:root {
  --syn-white: #FFFFFF;
  --syn-deep-blue: #0B3458;
  --syn-gold: #B8860B;
  --syn-green: #16A34A;
  --syn-muted:#64748b;
}

html, body, [class*="css"] {
  font-family: 'Poppins', sans-serif !important;
  background: var(--syn-white) !important;
  color: var(--syn-deep-blue) !important;
}

/* HEADER */
.header-container {
  display:flex;
  align-items:center;
  gap:18px;
  padding:18px 6px;
  justify-content:center;
  background: transparent;
}
.header-logo {
  width:160px;
  height:auto;
}
.header-title {
  font-size:32px;
  font-weight:700;
  color: var(--syn-deep-blue);
}
.header-sub {
  color: #475569;
  font-size:14px;
}

</style>
""", unsafe_allow_html=True)


col1, col2 = st.columns([1, 4])

with col1:
    st.image("synalityfoto.png", use_column_width=True)

with col2:
    st.markdown("""
        <div class='header-title'>Synality</div>
        <div class='header-sub'>Arquitetura em nuvem • Análise de dados • Automação empresarial</div>
    """, unsafe_allow_html=True)




# -------------------------
# Carregar .env
load_dotenv()

# SMTP / Gmail (coloque no .env)
SMTP_EMAIL = os.getenv("OUTLOOK_EMAIL")      # use seu gmail ou outlook aqui
SMTP_PASSWORD = os.getenv("OUTLOOK_PASSWORD")  # app password do Gmail / senha do SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# -------------------------
# Paths e diretórios
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

LOGO_PATH = os.path.join(BASE_DIR, "synalityfoto.png")
DB_PATH = os.path.join(BASE_DIR, "synality.db")
SAMPLE_CSV = os.path.join(BASE_DIR, "invoices.csv")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# -------------------------
st.set_page_config(page_title="Synality", page_icon="📊", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

:root {
  --syn-white: #FFFFFF;
  --syn-deep-blue: #0B3458; /* azul profundo */
  --syn-gold: #D4AF37;      /* dourado real */
  --syn-gold-soft: #F5E6A4; /* dourado claro */
  --syn-green: #16A34A;     /* botão verde */
  --syn-muted:#64748b;
}

/* Fundo geral + fonte */
html, body, [class*="css"] { 
  font-family: 'Poppins', sans-serif; 
  background: var(--syn-white) !important; 
  color: var(--syn-deep-blue); 
}

/* HEADER */
.header-container {
  display:flex;
  align-items:center;
  gap:18px;
  padding:18px 6px;
  justify-content:center;
}
.header-logo {
  width:160px;
  height:auto;
  border-radius:8px;
  box-shadow: 0 8px 20px rgba(2,6,23,0.06);
}
.header-title {
  font-size:28px;
  font-weight:700;
  color: var(--syn-deep-blue);
  margin:0;
}
.header-sub {
  color: #475569;
  font-size:14px;
  margin-top:4px;
}

/* ✅ CARD DOURADO PREMIUM */
#synalyt_pro_card {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 320px;
  background: linear-gradient(135deg, var(--syn-gold), var(--syn-gold-soft));
  border-left: 5px solid var(--syn-gold);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  padding: 16px;
  border-radius: 14px;
  z-index: 9999;
}

#synalyt_pro_card h4{
    margin:0;
    font-size:18px;
    color: var(--syn-deep-blue);
    font-weight: 700;
}

#synalyt_pro_card p{
    margin:8px 0 14px 0;
    font-size:14px;
    color:#222;
}

/* ✅ BOTÃO ASSINAR */
.syn-btn {
    display:inline-block; 
    padding:10px 14px; 
    border-radius:8px; 
    background: var(--syn-green); 
    color:white !important; 
    text-decoration:none; 
    font-weight:700; 
    cursor:pointer;
}

/* BOTÃO FECHAR */
.syn-close{
    position:absolute; 
    right:8px; 
    top:6px; 
    background:transparent; 
    border:none; 
    font-weight:700; 
    cursor:pointer; 
    color:#222; 
    font-size:20px;
}

/* BOTÕES DO STREAMLIT */
.stButton>button { 
    border-radius:10px; 
    background: var(--syn-green); 
    color:white !important;
    font-weight:600;
}
.stButton>button:hover { 
    background:#0f7f39; 
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# DB connection (simple)
@st.cache_resource
def get_conn(path):
    return sqlite3.connect(path, check_same_thread=False)

conn = get_conn(DB_PATH)
c = conn.cursor()

# Criação de tabelas (inclui password_resets)
c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha BLOB NOT NULL,
    plano TEXT DEFAULT 'free',
    mp_preference_id TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS relatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    arquivo_pdf TEXT,
    arquivo_xlsx TEXT,
    arquivo_csv TEXT,
    data TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    year_month TEXT,
    sent_count INTEGER DEFAULT 0,
    UNIQUE(usuario, year_month)
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL
)
''')
conn.commit()

# -------------------------
# Helpers auth
def hash_password(pwd: str) -> bytes:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())

def check_password(pwd: str, hashed):
    if isinstance(hashed, memoryview):
        hashed = hashed.tobytes()
    return bcrypt.checkpw(pwd.encode(), hashed)

def criar_usuario(email: str, password: str):
    try:
        h = hash_password(password)
        c.execute("INSERT INTO usuarios (email, senha, plano) VALUES (?, ?, ?)", (email, h, "free"))
        conn.commit()
        return True, "Cadastro realizado com sucesso."
    except sqlite3.IntegrityError:
        return False, "E-mail já cadastrado."
    except Exception as e:
        return False, str(e)

def autenticar(email: str, password: str):
    row = c.execute("SELECT senha, plano FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return False, "Usuário não encontrado."
    senha_hash, plano = row
    try:
        if check_password(password, senha_hash):
            return True, plano
        return False, "Senha incorreta."
    except Exception as e:
        return False, str(e)

# -------------------------
# Password reset helpers
RESET_TOKEN_TTL_SECONDS = 3600  # 1 hora

def create_password_reset_token(email: str):
    # verifica se usuário existe
    row = c.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return False, "E-mail não cadastrado."
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.datetime.utcnow() + datetime.timedelta(seconds=RESET_TOKEN_TTL_SECONDS)).isoformat()
    try:
        c.execute("INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)", (email, token, expires_at))
        conn.commit()
        return True, token
    except sqlite3.IntegrityError:
        # raro: token collision, gerar outro
        return create_password_reset_token(email)
    except Exception as e:
        return False, str(e)

def verify_reset_token(token: str):
    row = c.execute("SELECT email, expires_at FROM password_resets WHERE token = ?", (token,)).fetchone()
    if not row:
        return False, "Token inválido."
    email, expires_at = row
    expires = datetime.datetime.fromisoformat(expires_at)
    if datetime.datetime.utcnow() > expires:
        # remover token expirado
        c.execute("DELETE FROM password_resets WHERE token = ?", (token,))
        conn.commit()
        return False, "Token expirado."
    return True, email

def consume_reset_token_and_set_password(token: str, new_password: str):
    ok, res = verify_reset_token(token)
    if not ok:
        return False, res
    email = res
    h = hash_password(new_password)
    c.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (h, email))
    c.execute("DELETE FROM password_resets WHERE token = ?", (token,))
    conn.commit()
    return True, "Senha atualizada com sucesso."

# -------------------------
# Helpers email limit (Free = 5 / mês)
FREE_EMAIL_LIMIT = 5

def ym_str(dt=None):
    if dt is None:
        dt = datetime.date.today()
    return dt.strftime("%Y-%m")

def get_sent_count(usuario, year_month):
    row = c.execute("SELECT sent_count FROM email_logs WHERE usuario = ? AND year_month = ?", (usuario, year_month)).fetchone()
    return row[0] if row else 0

def increment_sent_count(usuario, year_month):
    row = c.execute("SELECT id, sent_count FROM email_logs WHERE usuario = ? AND year_month = ?", (usuario, year_month)).fetchone()
    if row:
        _id, cnt = row
        c.execute("UPDATE email_logs SET sent_count = ? WHERE id = ?", (cnt+1, _id))
    else:
        c.execute("INSERT INTO email_logs (usuario, year_month, sent_count) VALUES (?, ?, ?)", (usuario, year_month, 1))
    conn.commit()

# -------------------------
# Arquivos: gerar PDF/Excel/CSV e salvar em exports
def gerar_pdf_buffer(usuario: str, df: pd.DataFrame, titulo="Relatório Synality"):
    buf = BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    # logo no PDF (tenta)
    try:
        if os.path.exists(LOGO_PATH):
            pdf.drawImage(LOGO_PATH, 40, 750, width=140, height=60)
    except Exception:
        pass
    pdf.setTitle(titulo)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, 780, titulo)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 740, f"Usuário: {usuario}")
    pdf.drawString(50, 725, f"Data: {datetime.date.today().isoformat()}")
    # detectar coluna de valor
    value_col = None
    for cand in ["value","Value","valor","Valor","gross_amount","transaction_amount","amount"]:
        if cand in df.columns:
            value_col = cand
            break
    if value_col:
        total = pd.to_numeric(df[value_col], errors="coerce").sum()
        pdf.drawString(50, 705, f"Faturamento total (estimado): R$ {total:,.2f}")
    y = 680
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, y, "Amostra de transações:")
    y -= 14
    for _, row in df.head(12).iterrows():
        line = " | ".join([str(v) for v in row.values[:6]])
        pdf.drawString(50, y, line[:130])
        y -= 12
        if y < 60:
            break
    pdf.save()
    buf.seek(0)
    return buf

def df_to_excel_bytes(df: pd.DataFrame):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Relatorio")
    buf.seek(0)
    return buf

def df_to_csv_bytes(df: pd.DataFrame):
    return df.to_csv(index=False).encode("utf-8")

def save_exports(base_name: str, pdf_buf: BytesIO, xlsx_buf: BytesIO, csv_bytes: bytes):
    ts = int(time.time())
    pdf_path = os.path.join(EXPORTS_DIR, f"{base_name}_{ts}.pdf")
    xlsx_path = os.path.join(EXPORTS_DIR, f"{base_name}_{ts}.xlsx")
    csv_path = os.path.join(EXPORTS_DIR, f"{base_name}_{ts}.csv")
    with open(pdf_path, "wb") as f: f.write(pdf_buf.getvalue())
    with open(xlsx_path, "wb") as f: f.write(xlsx_buf.getvalue())
    with open(csv_path, "wb") as f: f.write(csv_bytes)
    return pdf_path, xlsx_path, csv_path

def registrar_relatorio(usuario, pdf_path, xlsx_path, csv_path):
    c.execute("INSERT INTO relatorios (usuario, arquivo_pdf, arquivo_xlsx, arquivo_csv, data) VALUES (?, ?, ?, ?, ?)",
              (usuario, pdf_path, xlsx_path, csv_path, datetime.datetime.now().isoformat()))
    conn.commit()

# -------------------------
# Envio de e-mail (Gmail - STARTTLS)
def enviar_email_com_anexos(to_email: str, subject: str, body: str, attachments: list):
    """
    attachments: list of tuples (filename, bytes_data, mime_type)
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise ValueError("SMTP_EMAIL / SMTP_PASSWORD não configurados no .env (use App Password do Gmail).")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Synality", SMTP_EMAIL))
    msg["To"] = to_email
    msg.set_content(body)
    for fname, data, mime in attachments:
        maintype, subtype = mime.split("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fname)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
    server.ehlo()
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

def enviar_email_simples(to_email: str, subject: str, body: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise ValueError("SMTP_EMAIL / SMTP_PASSWORD não configurados no .env (use App Password do Gmail).")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Synality", SMTP_EMAIL))
    msg["To"] = to_email
    msg.set_content(body)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
    server.ehlo()
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

# -------------------------
# Sessão
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
    st.session_state["plano"] = None
    st.session_state["last_pref_id"] = None

# -------------------------
# Floating Pro card (uma vez) - botão verde com texto ASSINAR (preto)
floating_html = """
<div id="synalyt_pro_card">
  <button type="button" class="syn-close" id="syn_close_btn">✕</button>
  <h4>💎 Synality Pro</h4>
  <p>Relatórios ilimitados • Integração SAP • Envio automático por e-mail • Prioridade</p>
  <a class="syn-btn" id="syn_cta_btn" href="#pro_section">ASSINAR</a>
</div>
<script>
(function(){
  function closeCard(e){
    try{ if(e && typeof e.preventDefault === 'function') e.preventDefault(); if(e && typeof e.stopPropagation === 'function') e.stopPropagation(); }catch(err){}
    var card = document.getElementById('synalyt_pro_card');
    if(card) { card.style.display = 'none'; try{ localStorage.setItem('synalyt_closed', Date.now().toString()); }catch(e){} }
    return false;
  }
  var btn = document.getElementById('syn_close_btn');
  if(btn){ btn.addEventListener('click', closeCard, false); btn.addEventListener('touchend', closeCard, false); }
  var cta = document.getElementById('syn_cta_btn');
  if(cta){ cta.addEventListener('click', function(e){ try{ e.preventDefault(); e.stopPropagation(); }catch(err){} window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }); return false; }, false); }
  try{
    var closed = localStorage.getItem('synalyt_closed');
    if(!closed){}
    else{
      var elapsed = Date.now() - parseInt(closed,10);
      if(elapsed >= 20000){ localStorage.removeItem('synalyt_closed'); var card = document.getElementById('synalyt_pro_card'); if(card) card.style.display = 'block'; }
      else {
        var remaining = 20000 - elapsed; var card = document.getElementById('synalyt_pro_card'); if(card) card.style.display = 'none';
        setTimeout(function(){ try{ localStorage.removeItem('synalyt_closed'); }catch(e){} var card2 = document.getElementById('synalyt_pro_card'); if(card2) card2.style.display = 'block'; }, remaining);
      }
    }
  }catch(e){}
})();
</script>
"""
st.markdown(floating_html, unsafe_allow_html=True)

# -------------------------
# Header (único, centralizado, logo maior)
col1, col2, col3 = st.columns([1,2,1])
with col1:
    st.write("")
with col2:
    header_html = "<div class='header-container'>"
    header_html += "<div class='header-text'>"
    header_html += "<div class='header-title'>📊 Synality — Relatórios Inteligentes</div>"
    header_html += "<div class='header-sub'>Automatize análise, exporte e envie relatórios em segundos</div>"
    header_html += "</div></div>"
    st.markdown(header_html, unsafe_allow_html=True)
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
with col3:
    st.write("")

st.markdown("---")

# -------------------------
# Reset token handling (if user clicked link in email)
query_params = st.experimental_get_query_params()
if "reset_token" in query_params:
    token = query_params.get("reset_token")[0]
    st.header("🔒 Redefinir senha")
    ok, res = verify_reset_token(token)
    if not ok:
        st.error(res)
        if st.button("Voltar para login"):
            st.experimental_set_query_params()
            st.rerun()
    else:
        senha_nova = st.text_input("Senha nova", type="password", key="reset_new_pwd")
        senha_nova2 = st.text_input("Confirmar senha nova", type="password", key="reset_new_pwd2")
        if st.button("Atualizar senha"):
            if not senha_nova or senha_nova != senha_nova2:
                st.error("Senhas não conferem.")
            else:
                ok2, res2 = consume_reset_token_and_set_password(token, senha_nova)
                if ok2:
                    st.success(res2)
                    # limpa query params para evitar reuso no UI
                    st.experimental_set_query_params()
                    if st.button("Ir para login"):
                        st.rerun()
                else:
                    st.error(res2)
    st.stop()

# -------------------------
# Auth UI
if not st.session_state["usuario"]:
    left, right = st.columns(2)
    with left:
        st.header("🔐 Entrar")
        email = st.text_input("E-mail", key="login_email")
        pwd = st.text_input("Senha", type="password", key="login_pwd")
        if st.button("Entrar"):
            ok, res = autenticar(email, pwd)
            if ok:
                st.session_state["usuario"] = email
                st.session_state["plano"] = res or "free"
                st.success("Login efetuado ✅")
                st.rerun()
            else:
                st.error(res)
        st.write("") 
        # link e fluxo de "Esqueci a senha"
        st.markdown("### Esqueceu a senha?")
        forgot_email = st.text_input("Informe seu e-mail para receber o link de recuperação", key="forgot_email")
        if st.button("Enviar link de recuperação"):
            if not forgot_email:
                st.error("Informe um e-mail.")
            else:
                ok, res = create_password_reset_token(forgot_email)
                if not ok:
                    st.error(res)
                else:
                    token = res
                    # contrói link - tenta pegar URL atual (Streamlit Cloud ou local)
                    try:
                        base_url = st.runtime.scriptrunner.script_run_ctx.get("server").server_address  # fallback (may be None)
                    except Exception:
                        base_url = None
                    # Melhor alternativa: usar request url a partir de window.location não disponível; vamos construir link relativo
                    reset_link = f"{st.get_url()}?reset_token={token}" if hasattr(st, "get_url") else f"?reset_token={token}"
                    # Envia e-mail com instruções
                    body = f"Olá,\n\nVocê solicitou redefinir sua senha do Synality. Clique no link abaixo para criar uma nova senha (válido por 1 hora):\n\n{reset_link}\n\nSe você não solicitou, ignore este e-mail.\n\nEquipe Synality"
                    try:
                        enviar_email_simples(forgot_email, "Recuperação de senha Synality", body)
                        st.success("Link de recuperação enviado por e-mail (verifique caixa de spam).")
                    except Exception as e:
                        st.error("Erro ao enviar e-mail: " + str(e))

    with right:
        st.header("🆕 Criar conta")
        new_email = st.text_input("E-mail (novo)", key="reg_email")
        new_pwd = st.text_input("Senha (nova)", type="password", key="reg_pwd")
        if st.button("Cadastrar"):
            ok, msg = criar_usuario(new_email, new_pwd)
            if ok:
                st.success(msg + " — Agora faça login.")
            else:
                st.error(msg)
    st.stop()

# -------------------------
# Sidebar
st.sidebar.markdown("## Navegação")
st.sidebar.write(f"**Usuário:** {st.session_state['usuario']}")
st.sidebar.write(f"**Plano:** {st.session_state['plano'].upper() if st.session_state['plano'] else 'FREE'}")
if st.sidebar.button("Sair"):
    st.session_state["usuario"] = None
    st.session_state["plano"] = None
    st.rerun()

page = st.sidebar.radio("Menu", ["Dashboard", "Integrações", "Pro (benefícios)", "Relatórios", "Conta"])

# -------------------------
# Dashboard
if page == "Dashboard":
    st.subheader("📊 Painel")
    st.markdown("Faça upload do CSV/XLSX (colunas: issue_date / value) ou use o CSV de exemplo.")

    uploaded = st.file_uploader("Carregar arquivo", type=["csv", "xlsx"])
    df = None

    if uploaded:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded, engine="openpyxl")

            st.success(f"Arquivo {uploaded.name} carregado")
            st.dataframe(df.head(8), use_container_width=True)

        except Exception as e:
            st.error("Erro lendo arquivo: " + str(e))

    if st.button("Usar CSV de exemplo"):
        if os.path.exists(SAMPLE_CSV):
            df = pd.read_csv(SAMPLE_CSV)
            st.success("Arquivo de exemplo carregado")
            st.dataframe(df.head(8), use_container_width=True)
        else:
            st.warning("Coloque invoices.csv na pasta do app para usar exemplo.")

    # Se não tem df carregado, para aqui
    if df is None:
        st.stop()

    # detectar colunas
    possible_value_cols = [c for c in df.columns if c.lower() in ("value", "valor", "gross_amount", "amount", "transaction_amount")]
    value_col = possible_value_cols[0] if possible_value_cols else st.selectbox("Coluna de valores", options=[None] + list(df.columns))

    possible_date_cols = [c for c in df.columns if c.lower() in ("issue_date", "date", "data", "created_at")]
    date_col = possible_date_cols[0] if possible_date_cols else st.selectbox("Coluna de data", options=[None] + list(df.columns))

    # Métricas
    faturamento_total = pd.to_numeric(df[value_col], errors="coerce").sum() if value_col else 0
    qtd = df.shape[0]

    st.metric("Faturamento total (estimado)", f"R$ {faturamento_total:,.2f}")
    st.metric("Registros", f"{qtd}")

    # gráfico
    if date_col and value_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            serie = df.groupby(df[date_col].dt.to_period("M"))[value_col].sum()

            fig, ax = plt.subplots(figsize=(8, 3))
            serie.index = serie.index.astype(str)
            serie.plot(kind="bar", ax=ax)
            ax.set_title("Evolução Mensal")
            ax.set_xlabel("")
            st.pyplot(fig)
        except:
            pass

    # ---- Gerar relatórios ----
    pdf_buf = gerar_pdf_buffer(st.session_state["usuario"], df, titulo="Relatório Synality")
    xlsx_buf = df_to_excel_bytes(df)
    csv_bytes = df_to_csv_bytes(df)

    # salvar
    base_name = f"{st.session_state['usuario']}_relatorio"
    pdf_path, xlsx_path, csv_path = save_exports(base_name, pdf_buf, xlsx_buf, csv_bytes)
    registrar_relatorio(st.session_state["usuario"], pdf_path, xlsx_path, csv_path)

    st.success("Relatório gerado e salvo em exports/ ✅")

    # —— Auto send (Free = 5/mês)
    send_to = st.text_input("Enviar para (e-mail)", value=st.session_state["usuario"])
    year_month = ym_str()

    can_auto_send = True
    if st.session_state.get("plano") != "pro":
        if get_sent_count(st.session_state["usuario"], year_month) >= FREE_EMAIL_LIMIT:
            can_auto_send = False

    if can_auto_send:
        try:
            attachments = [
                (os.path.basename(pdf_path), open(pdf_path, "rb").read(), "application/pdf"),
                (os.path.basename(xlsx_path), open(xlsx_path, "rb").read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                (os.path.basename(csv_path), open(csv_path, "rb").read(), "text/csv")
            ]

            enviar_email_com_anexos(
                send_to,
                "Relatório Synality — automático",
                "Segue em anexo seu relatório Synality.",
                attachments
            )

            if st.session_state.get("plano") != "pro":
                increment_sent_count(st.session_state["usuario"], year_month)

            st.success("Relatório enviado automaticamente por e-mail ✅")

        except Exception as e:
            st.error("Erro no envio automático: " + str(e))

    else:
        st.warning(f"Limite de envios atingido ({FREE_EMAIL_LIMIT}/mês). Faça upgrade para PRO.")

    # Downloads
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ Baixar PDF", data=open(pdf_path, "rb"), file_name=os.path.basename(pdf_path))
    with c2:
        st.download_button("⬇️ Baixar Excel", data=open(xlsx_path, "rb"), file_name=os.path.basename(xlsx_path))
    with c3:
        st.download_button("⬇️ Baixar CSV", data=open(csv_path, "rb"), file_name=os.path.basename(csv_path))

    # Envio manual
    if st.button("Enviar por e-mail agora (manual)"):
        ym = ym_str()
        can_send = True
        if st.session_state.get("plano") != "pro":
            if get_sent_count(st.session_state["usuario"], ym) >= FREE_EMAIL_LIMIT:
                can_send = False

        if not can_send:
            st.warning("Limite de envios atingido. Atualize para Pro.")
        else:
            try:
                attachments = [
                    (os.path.basename(pdf_path), open(pdf_path, "rb").read(), "application/pdf"),
                    (os.path.basename(xlsx_path), open(xlsx_path, "rb").read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                    (os.path.basename(csv_path), open(csv_path, "rb").read(), "text/csv")
                ]

                enviar_email_com_anexos(send_to, "Relatório Synality", "Segue em anexo seu relatório Synality.", attachments)

                if st.session_state.get("plano") != "pro":
                    increment_sent_count(st.session_state["usuario"], ym)

                st.success("E-mail enviado ✅")
            except Exception as e:
                st.error("Erro ao enviar e-mail: " + str(e))

# -------------------------
# Pro (benefícios) + checkout (simples)
elif page == "Pro (benefícios)":
    st.header("Synality Pro — Benefícios")
    st.markdown("""
    **Por que assinar Pro?**
    - Relatórios ilimitados (PDF/Excel/CSV)
    - Integração SAP e importadores
    - Envio automático/agendado por e-mail
    - Onboarding e suporte prioritário
    - Área premium com tutoriais
    """)
    st.markdown("### Planos")
    st.table(pd.DataFrame({
        "Recurso":["Relatórios","Integração SAP","Envio e-mail","Suporte","Preço"],
        "Free":["5/mês","-","Automático limitado","Comunidade","Grátis"],
        "Pro":["Ilimitado","Sim","Automático ilimitado","Prioritário","R$49,90/mês"]
    }))

    st.markdown("### Assinar Pro (simulado)")
    if st.button("Criar checkout (simulado)"):
        st.info("Simulação: página de checkout abriria aqui. Integração real com Mercado Pago exige credenciais e teste.")

# -------------------------
# Relatórios (histórico)
elif page == "Relatórios":
    st.header("Histórico de Relatórios")
    rows = c.execute("SELECT arquivo_pdf, arquivo_xlsx, arquivo_csv, data FROM relatorios WHERE usuario = ? ORDER BY id DESC", (st.session_state["usuario"],)).fetchall()
    if not rows:
        st.info("Nenhum relatório gerado ainda.")
    else:
        dfh = pd.DataFrame(rows, columns=["arquivo_pdf","arquivo_xlsx","arquivo_csv","data"])
        st.dataframe(dfh, use_container_width=True)
        for pdf_p, xlsx_p, csv_p, dt in rows:
            colA, colB, colC = st.columns([6,1,1])
            colA.write(f"📄 {os.path.basename(pdf_p)} — {dt}")
            if colB.button("🔽 Baixar PDF", key=f"dl_pdf_{pdf_p}"):
                with open(pdf_p, "rb") as f:
                    st.download_button("⬇️ Download PDF", data=f, file_name=os.path.basename(pdf_p), mime="application/pdf")
            if colC.button("🔽 Baixar XLSX", key=f"dl_xlsx_{xlsx_p}"):
                with open(xlsx_p, "rb") as f:
                    st.download_button("⬇️ Download XLSX", data=f, file_name=os.path.basename(xlsx_p), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------------
# Conta & Configurações
elif page == "Conta":
    st.header("Conta & Configurações")
    st.write(f"Usuário: **{st.session_state['usuario']}**")
    st.write(f"Plano: **{st.session_state['plano'].upper() if st.session_state['plano'] else 'FREE'}**")
    st.markdown("---")
    st.subheader("SMTP (env)")
    st.write("Servidor:", SMTP_SERVER)
    st.write("Porta:", SMTP_PORT)
    st.write("Usuário:", SMTP_EMAIL if SMTP_EMAIL else "não configurado")
    st.markdown("**Dica:** Se usar Gmail, ative 2FA e gere uma App Password para usar em `OUTLOOK_PASSWORD` (campo OUTLOOK_PASSWORD no .env).")
    if st.button("Cancelar assinatura (simulado)"):
        c.execute("UPDATE usuarios SET plano = ? WHERE email = ?", ("free", st.session_state["usuario"]))
        conn.commit()
        st.session_state["plano"] = "free"
        st.success("Plano FREE restaurado.")

# -------------------------
# Mantém o floating card no final também
st.markdown(floating_html, unsafe_allow_html=True)
