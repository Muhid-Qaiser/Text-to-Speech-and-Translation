FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y bash
RUN pip install --no-cache-dir -r requirements.txt

# # Download Weights in Image
# RUN python -c "from transformers import AutoProcessor, SeamlessM4Tv2Model; \
#     processor = AutoProcessor.from_pretrained('facebook/seamless-m4t-v2-large'); \
#     model = SeamlessM4Tv2Model.from_pretrained('facebook/seamless-m4t-v2-large')"

# Use Cache in Image for weights. Download Weights in Container for first time
ENV HF_HOME="/app/.cache/huggingface"
ENV TRANSFORMERS_CACHE="${HF_HOME}" 
RUN mkdir -p "${HF_HOME}" 

COPY . .
EXPOSE 50051
EXPOSE 8501
EXPOSE 5000
CMD ["bash", "-c", "python server.py & streamlit run local_app.py"]



# docker build -t my-python-app .
# docker run -p 5000:5000 my-python-app
# docker run -p 5000:5000 --name my-running-app my-python-app
# docker stop my-running-app
# docker rm my-running-app
# docker rmi my-python-app
