import streamlit as st
import torch
import tempfile
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio


# * Initialize processor and model
@st.cache_resource
def load_model():
    processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
    model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
    sampling_rate = model.config.sampling_rate  # * Ensure sample rate is set correctly
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return processor, model, sampling_rate, device


# * Streamlit UI
st.title("🗣️ Text-to-Speech with SeamlessM4T")

# * Load the model and processor
processor, model, sample_rate, device = load_model()

# * User input
text_input = st.text_area("Enter text to convert to speech", "Hello, how are you doing today?")
generate_btn = st.button("Generate Speech")

if generate_btn:
    with st.spinner("Generating speech..."):
        # * Preprocess text input
        inputs = processor(text=text_input, return_tensors="pt")

        # * Move inputs to the correct device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # * Generate speech
        with torch.no_grad():
            speech = model.generate(**inputs, tgt_lang="eng")

        # * Extract the audio waveform (first element of the tuple)
        audio_array = speech[0].cpu().numpy().squeeze()

        # * Save the audio to a temporary .wav file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            torchaudio.save(tmp_wav.name, torch.tensor(audio_array).unsqueeze(0), sample_rate)
            st.audio(tmp_wav.name, format="audio/wav")
            st.success("Speech generated!")

