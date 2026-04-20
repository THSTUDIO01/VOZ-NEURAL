import streamlit as st
import google.generativeai as genai
import os

# Configuração da Página
st.set_page_config(page_title="Gerador de Voz Neural Gemini", layout="wide")

# Interface Estilizada (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Meu Gerador de Voz Neural")

# --- BARRA LATERAL (CONFIGURAÇÕES E CANAIS) ---
with st.sidebar:
    st.header("⚙️ Definições do Canal")
    api_key = st.text_input("Insira sua API Key do Google:", type="password")
    nome_canal = st.text_input("Nome do seu Canal:", value="Meu Canal")
    
    # Lista de Vozes do Gemini
    vozes_disponiveis = ["Puck", "Charon", "Kore", "Zephyr", "Leda", "Aoede", "Autonoe", "Fenrir"]
    
    voz_selecionada = st.selectbox("Escolha a Voz do Narrador:", vozes_disponiveis)
    
    if st.button("⭐ Favoritar esta voz para este canal"):
        st.success(f"Voz {voz_selecionada} favoritada para {nome_canal}!")
        st.session_state['favorito'] = voz_selecionada

# --- ÁREA CENTRAL (CONTEÚDO) ---
texto_input = st.text_area("Cole o conteúdo para converter (Sem limite de caracteres):", height=300)

if st.button("🚀 Processar e Gerar Áudio Único"):
    if not api_key:
        st.error("Por favor, insira sua API Key na barra lateral.")
    elif not texto_input:
        st.warning("O campo de texto está vazio.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('Sua voz está sendo gerada... Isso pode demorar para textos muito longos.'):
                # Lógica para "Sem Limite": Divide o texto a cada 2000 caracteres
                pedacos = [texto_input[i:i+2000] for i in range(0, len(texto_input), 2000)]
                audio_final = bytearray()

                for p in pedacos:
                    response = model.generate_content(
                        p,
                        generation_config={
                            "response_modalities": ["AUDIO"],
                            "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": voz_selecionada}}}
                        }
                    )
                    # Adiciona o pedaço gerado ao arquivo final
                    audio_data = response.candidates[0].content.parts[0].inline_data.data
                    audio_final.extend(audio_data)

                # Nome do arquivo conforme solicitado: [Canal] + [Voz].wav
                filename = f"{nome_canal}_{voz_selecionada}.wav"
                
                st.success("✅ Áudio Unificado Pronto!")
                st.audio(audio_final, format='audio/wav')
                
                st.download_button(
                    label="📥 Descarregar Ficheiro .WAV",
                    data=bytes(audio_final),
                    file_name=filename,
                    mime="audio/wav"
                )
        except Exception as e:
            st.error(f"Erro ao gerar áudio: {e}")