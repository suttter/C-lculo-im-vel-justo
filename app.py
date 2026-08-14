import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador Imobiliário Bauru", layout="wide")
st.title("🏆 Simulador Imobiliário Master - Bauru")
st.markdown("Altere os dados no painel abaixo para ver o resultado, impostos e o gráfico mudarem em tempo real no seu celular.")

if "selic_val" not in st.session_state: st.session_state.selic_val = 14.00
if "cdi_val" not in st.session_state: st.session_state.cdi_val = 105.0
def preencher_dados_hoje():
    st.session_state.selic_val = 14.00
    st.session_state.cdi_val = 105.0

st.subheader("📍 Identificação do Imóvel")
nome_imovel = st.text_input("Nome do Condomínio, Prédio ou Rua do Imóvel", value="Apartamento Térreo - Bauru")
dinheiro_total_guardado = st.number_input("Capital total que você tem guardado hoje (R$)", value=250000, step=5000)

st.subheader("🏡 Condições de Compra")
col_compra1, col_compra2 = st.columns(2)
with col_compra1:
    v_imovel_anuncio = st.number_input("Valor de anúncio do imóvel (R$)", value=250000, step=5000)
    desconto_a_vista = st.number_input("Desconto negociado à vista (%)", value=8.0, step=0.5, min_value=0.0, max_value=100.0)
with col_compra2:
    v_condominio_inicial = st.number_input("Taxa de Condomínio mensal (R$)", value=420, step=10)
    valor_venal_exato = st.number_input("Valor Venal para cálculo de IPTU (R$)", value=130000, step=5000)

v_aluguel_mensal_inicial = st.number_input("Aluguel mensal inicial sugerido (R$)", value=1000, step=50)
st.button("📊 Preencher com os Dados de Hoje (Agosto/2026)", on_click=preencher_dados_hoje)

col_eco1, col_eco2 = st.columns(2)
with col_eco1:
    periodo_simulacao_meses = st.slider("Prazo de análise da simulação (Meses)", 1, 120, 60, 1)
    tendencia_da_selic = st.selectbox("Tendência futura da Taxa Selic", ["Queda Gradual", "Alta Gradual", "Estável"])
with col_eco2:
    taxa_selic_hoje = st.number_input("Taxa Selic atual do país (% ao ano)", step=0.25, key="selic_val") / 100
    cdi_performance = st.number_input("Rentabilidade da sua Renda Fixa (% do CDI)", step=1.0, key="cdi_val") / 100

v_imovel_venda = v_imovel_anuncio * (1 - (desconto_a_vista / 100))
custo_itbi = v_imovel_venda * 0.02  
custo_escritura_registro = v_imovel_venda * 0.018  
v_iptu_mes_inicial = (valor_venal_exato * 0.01) / 12
total_taxas_compra = custo_itbi + custo_escritura_registro
custo_total_para_adquirir = v_imovel_venda + total_taxas_compra
sobra_ou_falta_imediata = dinheiro_total_guardado - custo_total_para_adquirir

dados, saldo_banco_pos_compra, imovel_fisico, saldo_banco_alugar = [], dinheiro_total_guardado - custo_total_para_adquirir, v_imovel_venda, dinheiro_total_guardado
aluguel_vigente, condominio_vigente, iptu_vigente = v_aluguel_mensal_inicial, v_condominio_inicial, v_iptu_mes_inicial
ac_aluguel, ac_cond_aluguel, ac_iptu_aluguel, ac_cond_compra, ac_iptu_compra, ac_juros_sobra, ac_juros_aluguel = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

for mes in range(0, periodo_simulacao_meses + 1):
    if mes == 0: selic_atual = taxa_selic_hoje
    else:
        if tendencia_da_selic == "Queda Gradual": selic_atual = max(0.10, taxa_selic_hoje - (mes * 0.0011))
        elif tendencia_da_selic == "Alta Gradual": selic_atual = min(0.18, taxa_selic_hoje + (mes * 0.0008))
        else: selic_atual = taxa_selic_hoje
        if mes % 12 == 1 and mes > 1:
            aluguel_vigente *= 1.04
            condominio_vigente *= 1.04
            iptu_vigente *= 1.04
        imovel_fisico *= (1 + ((1 + 0.06)**(1/12) - 1))
        rend_mensal_cdi_liq = (((1 + (selic_atual * cdi_performance))**(1/12)) - 1) * 0.85
        if saldo_banco_pos_compra > 0: ac_juros_sobra += (saldo_banco_pos_compra * rend_mensal_cdi_liq)
        ac_juros_aluguel += (saldo_banco_alugar * rend_mensal_cdi_liq)
        ac_cond_compra += condominio_vigente
        ac_iptu_compra += iptu_vigente
        saldo_banco_pos_compra = (saldo_banco_pos_compra * (1 + rend_mensal_cdi_liq)) - (condominio_vigente + iptu_vigente)
        ac_aluguel += aluguel_vigente
        ac_cond_aluguel += condominio_vigente
        ac_iptu_aluguel += iptu_vigente
        saldo_banco_alugar = (saldo_banco_alugar * (1 + rend_mensal_cdi_liq)) - (aluguel_vigente + condominio_vigente + iptu_vigente)
    dados.append({"Mês": mes, "COMPRAR": imovel_fisico + saldo_banco_pos_compra, "ALUGAR": saldo_banco_alugar})

df = pd.DataFrame(dados)
patr_final_comprar, patr_final_alugar = dados[-1]["COMPRAR"], dados[-1]["ALUGAR"]

st.markdown("---")
st.subheader("📋 Extrato de Gastos Reais da Compra (Bauru):")
st.markdown("### 🛒 1. Custos Individuais de Aquisição:")
ext_col1, ext_col2, ext_col3 = st.columns(3)
with ext_col1: st.metric("💵 Preço do Imóvel (C/ Desconto)", f"R$ {v_imovel_venda:,.2f}")
with ext_col2: st.metric("🏛️ Imposto municipal ITBI (2%)", f"R$ {custo_itbi:,.2f}")
with ext_col3: st.metric("✍️ Custos Cartorários (Est.)", f"R$ {custo_escritura_registro:,.2f}")

st.markdown("### 🧮 2. Resumo e Soma Total:")
tot_col1, tot_col2 = st.columns(2)
with tot_col1: st.metric("📊 SOMA DAS TAXAS OCULTAS", f"R$ {total_taxas_compra:,.2f}")
with tot_col2: st.metric("💰 GASTO TOTAL DA COMPRA", f"R$ {custo_total_para_adquirir:,.2f}")

if sobra_ou_falta_imediata < 0:
    st.error(f"⚠️ ALERTA DE CAPITAL: Seu saldo de R$ {dinheiro_total_guardado:,.2f} NÃO cobre a compra! Faltam R$ {abs(sobra_ou_falta_imediata):,.2f}.")
else:
    st.success(f"✅ SALDO SUFICIENTE: Sobrarão R$ {sobra_ou_falta_imediata:,.2f} livres como reserva.")

st.markdown("---")
st.subheader("📊 Patrimônio Acumulado no Final do Prazo:")
res_col1, res_col2 = st.columns(2)
with res_col1: st.metric("🏡 Cenário Comprar Imóvel", f"R$ {patr_final_comprar:,.2f}")
with res_col2: st.metric("📈 Cenário Alugar e Investir", f"R$ {patr_final_alugar:,.2f}")

veredit_text = f"COMPRAR é mais vantajoso por R$ {patr_final_comprar - patr_final_alugar:,.2f}." if patr_final_comprar > patr_final_alugar else f"ALUGAR E INVESTIR é mais vantajoso por R$ {patr_final_alugar - patr_final_comprar:,.2f}."
if patr_final_comprar > patr_final_alugar: st.success(f"🌟 VEREDITO FINANCEIRO: {veredit_text}")
else: st.info(f"🌟 VEREDITO FINANCEIRO: {veredit_text}")

st.markdown("### 🔍 Abertura Detalhada das Contas do Período:")
tab_compra, tab_aluguel = st.columns(2)
with tab_compra:
    st.markdown("#### 🏡 Detalhamento do Cenário Comprar:")
    st.write(f"🔹 **(+) Valor do Imóvel Físico Valorizado:** R$ {imovel_fisico:,.2f}")
    st.write(f"🔹 **(+) Troco Inicial + Juros do Banco:** R$ {max(0.0, sobra_ou_falta_imediata) + ac_juros_sobra:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Condomínio:** R$ {ac_cond_compra:,.2f}")
    st.write(f"📉 **(-) Total Gasto com IPTU:** R$ {ac_iptu_compra:,.2f}")
with tab_aluguel:
    st.markdown("#### 📈 Detalhamento do Cenário Alugar:")
    st.write(f"🔹 **(+) Capital Inicial Investido:** R$ {dinheiro_total_guardado:,.2f}")
    st.write(f"🔹 **(+) Total de Juros Ganhos no Banco:** R$ {ac_juros_aluguel:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Aluguel:** R$ {ac_aluguel:,.2f}")
    st.write(f"📉 **(-) Total Gasto com Condomínio:** R$ {ac_cond_aluguel:,.2f}")
    st.write(f"📉 **(-) Total Gasto com IPTU:** R$ {ac_iptu_aluguel:,.2f}")

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

texto_relatorio = f"""📊 RELATÓRIO IMOBILIÁRIO - {nome_imovel.upper()}\nPrazo: {periodo_simulacao_meses} meses.\n\n🏡 COMPRA À VISTA:\n- Preço Imóvel: R$ {v_imovel_venda:,.2f}\n- Taxas (ITBI/Cartório): R$ {total_taxas_compra:,.2f}\n👉 Gasto Inicial Total: R$ {custo_total_para_adquirir:,.2f}\n\n📈 ALUGUEL ALTERNATIVO:\n- Aluguel Acumulado: R$ {ac_aluguel:,.2f}\n\n📊 PATRIMÔNIO FINAL:\n- Se Comprar: R$ {patr_final_comprar:,.2f}\n- Se Alugar: R$ {patr_final_alugar:,.2f}\n\n🏆 VEREDITO: {veredit_text}"""
st.markdown("---")
st.subheader("📲 Compartilhar Análise")
st.text_area("Texto do Relatório:", texto_relatorio, height=150)

texto_js = texto_relatorio.replace("\n", "\\n").replace("'", "\\'")
componentes_html = f"<script>function compartilhar_celular() {{ if (navigator.share) {{ navigator.share({{ title: 'Análise Imobiliária', text: '{texto_js}' }}).then(() => console.log('Sucesso')).catch((err) => console.log(err)); }} else {{ alert('Acesse via Chrome/Safari para compartilhar.'); }} }}</script><button onclick='compartilhar_celular()' style='width:100%; background-color:#007BFF; color:white; border:none; padding:14px; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer;'>📱 Compartilhar no WhatsApp ou Outros Apps</button>"
components.html(componentes_html, height=60)
