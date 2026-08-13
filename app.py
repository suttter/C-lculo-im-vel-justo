import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador Imobiliário Bauru", layout="wide")

st.title("🏆 Simulador Imobiliário Master - Bauru")
st.markdown("Altere os dados no painel abaixo para ver o resultado, impostos e o gráfico mudarem em tempo real no seu celular.")

# --- 🚀 GERENCIAMENTO DE ESTADO PARA OS CAMPOS ---
if "selic_val" not in st.session_state:
    st.session_state.selic_val = 14.00
if "cdi_val" not in st.session_state:
    st.session_state.cdi_val = 105.0

def preencher_dados_hoje():
    st.session_state.selic_val = 14.00
    st.session_state.cdi_val = 105.0

# --- 📱 PAINEL INTERATIVO DE ENTRADA DE DADOS ---
st.subheader("📍 Identificação do Imóvel")
nome_imovel = st.text_input("Nome do Condomínio, Prédio ou Rua do Imóvel", value="Apartamento Térreo - Bauru")

st.subheader("💰 Seu Capital Inicial")
dinheiro_total_guardado = st.number_input("Capital total que você tem guardado hoje (R$)", value=250000, step=5000)

st.subheader("🏡 Condições de Compra do Imóvel")
col_compra1, col_compra2 = st.columns(2)
with col_compra1:
    v_imovel_anuncio = st.number_input("Valor de anúncio do imóvel (R$)", value=250000, step=5000)
    desconto_a_vista = st.number_input("Desconto negociado à vista (%)", value=8.0, step=0.5, min_value=0.0, max_value=100.0)
with col_compra2:
    v_condominio_inicial = st.number_input("Taxa de Condomínio mensal (R$)", value=420, step=10)
    valor_venal_exato = st.number_input("Valor Venal para cálculo de IPTU (R$)", value=130000, step=5000)

st.subheader("📈 Condições de Aluguel")
v_aluguel_mensal_inicial = st.number_input("Aluguel mensal inicial sugerido (R$)", value=1000, step=50)

st.subheader("🔮 Cenário Econômico do Brasil")
st.button("📊 Preencher Automaticamente com os Dados de Hoje (Agosto/2026)", on_click=preencher_dados_hoje)

col_eco1, col_eco2 = st.columns(2)
with col_eco1:
    periodo_simulacao_meses = st.slider("Prazo de análise da simulação (Meses)", 1, 120, 60, 1)
    tendencia_da_selic = st.selectbox("Tendência futura da Taxa Selic", ["Queda Gradual", "Alta Gradual", "Estável"])
with col_eco2:
    taxa_selic_hoje = st.number_input("Taxa Selic atual do país (% ao ano)", step=0.25, key="selic_val") / 100
    cdi_performance = st.number_input("Rentabilidade da sua Renda Fixa (% do CDI)", step=1.0, key="cdi_val") / 100

val_imovel_ano = 0.06 
inflacao_ano = 0.04   

# --- 🧮 PROCESSAMENTO MATEMÁTICO ---
v_imovel_venda = v_imovel_anuncio * (1 - (desconto_a_vista / 100))
custo_itbi = v_imovel_venda * 0.02  
custo_escritura_registro = v_imovel_venda * 0.018  
v_iptu_ano = valor_venal_exato * 0.01  
v_iptu_mes_inicial = v_iptu_ano / 12

total_taxas_compra = custo_itbi + custo_escritura_registro
custo_total_para_adquirir = v_imovel_venda + total_taxas_compra
sobra_ou_falta_imediata = dinheiro_total_guardado - custo_total_para_adquirir

val_mensal_imovel = (1 + val_imovel_ano)**(1/12) - 1
inflacao_mensal = (1 + inflacao_ano)**(1/12) - 1

dados = []
saldo_banco_pos_compra = dinheiro_total_guardado - custo_total_para_adquirir
imovel_fisico = v_imovel_venda
saldo_banco_alugar = dinheiro_total_guardado

aluguel_vigente = v_aluguel_mensal_inicial
condominio_vigente = v_condominio_inicial
iptu_vigente = v_iptu_mes_inicial

# Variáveis acumuladoras dos fatores internos da simulação de tempo
acumulado_aluguel = 0.0
acumulado_condominio_alugar = 0.0
acumulado_iptu_alugar = 0.0

acumulado_condominio_comprar = 0.0
acumulado_iptu_comprar = 0.0
acumulado_manutencao = 0.0
acumulado_rendimento_sobra = 0.0
acumulado_rendimento_alugar = 0.0

for mes in range(0, periodo_simulacao_meses + 1):
    if mes == 0:
        selic_atual = taxa_selic_hoje
    else:
        if tendencia_da_selic == "Queda Gradual":
            selic_atual = max(0.10, taxa_selic_hoje - (mes * 0.0011))
        elif tendencia_da_selic == "Alta Gradual":
            selic_atual = min(0.18, taxa_selic_hoje + (mes * 0.0008))
        else:
            selic_atual = taxa_selic_hoje
            
        if mes % 12 == 1 and mes > 1:
            aluguel_vigente *= (1 + inflacao_ano)
            condominio_vigente *= (1 + inflacao_ano)
            iptu_vigente *= (1 + inflacao_ano)
            
        imovel_fisico *= (1 + val_mensal_imovel)
        custo_manutencao_mes = (imovel_fisico * 0.005) / 12
        
        rend_mensal_cdi_liq = (((1 + (selic_atual * cdi_performance))**(1/12)) - 1) * 0.85
        
        if saldo_banco_pos_compra > 0:
            acumulado_rendimento_sobra += (saldo_banco_pos_compra * rend_mensal_cdi_liq)
        acumulado_rendimento_alugar += (saldo_banco_alugar * rend_mensal_cdi_liq)

        acumulado_condominio_comprar += condominio_vigente
        acumulado_iptu_comprar += iptu_vigente
        acumulado_manutencao += custo_manutencao_mes
        custo_comprar_mes = condominio_vigente + iptu_vigente + custo_manutencao_mes
        saldo_banco_pos_compra = (saldo_banco_pos_compra * (1 + rend_mensal_cdi_liq)) - custo_comprar_mes
        
        acumulado_aluguel += aluguel_vigente
        acumulado_condominio_alugar += condominio_vigente
        acumulado_iptu_alugar += iptu_vigente
        custo_alugar_mes = aluguel_vigente + condominio_vigente + iptu_vigente
        saldo_banco_alugar = (saldo_banco_alugar * (1 + rend_mensal_cdi_liq)) - custo_alugar_mes

    patrimonio_comprar_total = imovel_fisico + saldo_banco_pos_compra
    dados.append({"Mês": mes, "COMPRAR": patrimonio_comprar_total, "ALUGAR": saldo_banco_alugar})

df = pd.DataFrame(dados)
patr_final_comprar = dados[-1]["COMPRAR"]
patr_final_alugar = dados[-1]["ALUGAR"]

# --- 🖥️ EXIBIÇÃO DO EXTRATO DETALHADO ---
st.markdown("---")
st.subheader("📋 Extrato de Gastos Reais da Compra (Bauru):")

st.markdown("### 🛒 1. Custos Individuais de Aquisição:")
ext_col1, ext_col2, ext_col3 = st.columns(3)
with ext_col1: st.metric("💵 Preço do Imóvel (C/ Desconto)", f"R$ {v_imovel_venda:,.2f}")
with ext_col2: st.metric("🏛️ Imposto municipal ITBI (2%)", f"R$ {custo_itbi:,.2f}")
with ext_col3: st.metric("✍️ Custos Cartorários (Est.)", f"R$ {custo_escritura_registro:,.2f}")

st.markdown("---")

st.markdown("### 🧮 2. Resumo e Soma Total:")
tot_col1, tot_col2 = st.columns(2)
with tot_col1: st.metric("📊 SOMA DAS TAXAS OCULTAS", f"R$ {total_taxas_compra:,.2f}")
with tot_col2: st.metric("💰 GASTO TOTAL DA COMPRA", f"R$ {custo_total_para_adquirir:,.2f}")

if sobra_ou_falta_imediata < 0:
    st.error(f"⚠️ ALERTA DE CAPITAL: Seu saldo de R$ {dinheiro_total_guardado:,.2f} NÃO cobre o gasto total necessário! Faltam R$ {abs(sobra_ou_falta_imediata):,.2f} para conseguir escriturar à vista.")
else:
    st.success(f"✅ SALDO SUFICIENTE: Seu capital cobre o gasto total! Após a compra e o pagamento das taxas, te sobrarão R$ {sobra_ou_falta_imediata:,.2f} livres como reserva de emergência imediata.")

# --- 📊 EXIBIÇÃO DO VEREDITO ---
st.markdown("---")
st.subheader("📊 Patrimônio Acumulado no Final do Prazo:")
res_col1, res_col2 = st.columns(2)
with res_col1: st.metric("🏡 Cenário Comprar Imóvel", f"R$ {patr_final_comprar:,.2f}")
with res_col2: st.metric("📈 Cenário Alugar e Investir", f"R$ {patr_final_alugar:,.2f}")

veredit_text = ""
if patr_final_comprar > patr_final_alugar:
    veredit_text = f"COMPRAR o imóvel físico é mais vantajoso por R$ {patr_final_comprar - patr_final_alugar:,.2f}."
    st.success(f"🌟 VEREDITO FINANCEIRO: {veredit_text}")
else:
    veredit_text = f"ALUGAR E INVESTIR o capital é mais vantajoso por R$ {patr_final_alugar - patr_final_comprar:,.2f}."
    st.info(f"🌟 VEREDITO FINANCEIRO: {veredit_text}")

st.markdown("### 🔍 Abertura Detalhada das Contas do Período:")
tab_compra, tab_aluguel = st.columns(2)

with tab_compra:
    st.markdown("#### 🏡 Detalhamento do Cenário Comprar:")
    st.write(f"🔹 **(+) Valor do Imóvel Físico Atualizado (Valorização):** R$ {imovel_fisico:,.2f}")
    st.write(f"🔹 **(+) Troco Inicial + Rendimento do Banco:** R$ {max(0.0, dinheiro_total_guardado - custo_total_para_adquirir) + acumulado_rendimento_sobra:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Condomínio:** R$ {acumulado_condominio_comprar:,.2f}")
    st.write(f"📉 **(-) Total Gasto com IPTU:** R$ {acumulado_iptu_comprar:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Manutenção Física:** R$ {acumulado_manutencao:,.2f}")
    st.markdown(f"👉 **PATRIMÔNIO LÍQUIDO FINAL:** **R$ {patr_final_comprar:,.2f}**")

with tab_aluguel:
    st.markdown("#### 📈 Detalhamento do Cenário Alugar:")
    st.write(f"🔹 **(+) Capital Inicial Investido:** R$ {dinheiro_total_guardado:,.2f}")
    st.write(f"🔹 **(+) Total de Juros Ganhos no Banco:** R$ {acumulado_rendimento_alugar:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Aluguel:** R$ {acumulado_aluguel:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Condomínio:** R$ {acumulado_condominio_alugar:,.2f}")
    st.write(f"📉 **(-) Total Gasto com IPTU:** R$ {acumulado_iptu_alugar:,.2f}")
    st.markdown(f"👉 **PATRIMÔNIO LÍQUIDO FINAL:** **R$ {patr_final_alugar:,.2f}**")

# --- 📈 GRÁFICO INTERATIVO ---
plt.close('all')
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Mês"], df["COMPRAR"], label="Se Comprar", color="green", linewidth=2.5)
ax.plot(df["Mês"], df["ALUGAR"], label="Se Alugar", color="blue", linewidth=2.5)
ax.set_xlabel("Meses")
ax.set_ylabel("Patrimônio Líquido (R$)")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
st.pyplot(fig)

# --- 📝 TEXTO DO PARECER CONCISO ---
texto_relatorio = f"""📊 RELATÓRIO IMOBILIÁRIO - {nome_imovel.upper()}
Prazo: {periodo_simulacao_meses} meses.

🏡 COMPRA À VISTA:
- Preço do Imóvel: R$ {v_imovel_venda:,.2f}
- Soma de Taxas (ITBI + Cartórios): R$ {total_taxas_compra:,.2f}
👉 GASTO TOTAL REAL DA COMPRA: R$ {custo_total_para_adquirir:,.2f}

📈 ALUGUEL ALTERNATIVO:
- Aluguel acumulado gasto no prazo: R$ {acumulado_aluguel:,.2f}
Taxas acumuladas pagas no aluguel (Condomínio/IPTU): R$ {acumulado_condominio_alugar + acumulado_iptu_alugar:,.2f}📊 PATRIMÔNIO FINAL:Se Comprar: R$ {patr_final_comprar:,.2f}Se Alugar: R$ {patr_final_alugar:,.2f}🏆 VEREDITO: {veredit_text}"""st.markdown("---")st.subheader("📲 Compartilhar Análise")st.text_area("Pré-visualização do texto:", texto_relatorio, height=180)texto_js = texto_relatorio.replace("\n", "\n").replace("'", "\'")componentes_html = f"""function compartilhar_celular() {{if (navigator.share) {{navigator.share({{title: 'Análise Imobiliária',text: '{texto_js}'}}).then(() => {{console.log('Compartilhado com sucesso!');}}).catch((error) => {{console.log('Erro ao compartilhar:', error);}});}} else {{alert('Seu navegador não suporta compartilhamento nativo. Use o botão de cópia acima.');}}}}📱 Compartilhar com WhatsApp ou Outros Apps"""components.html(componentes_html, height=60)
