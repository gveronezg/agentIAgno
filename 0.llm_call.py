from agno.models.groq import Groq # utilizando os modelos da groq principalmente por serem gratuitos
from agno.models.message import Message

from dotenv import load_dotenv
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

model = Groq(id="llama-3.3-70b-versatile")  # Inicializa o modelo Groq com o modelo LLaMA 3.3 70B Versatile

msg = Message(
    role="user",
    content=[{"type": "text", "text": "Olá, meu nome é Gabriel!"}]
)  # Cria uma mensagem de usuário

response = model.invoke([msg])  # Invoca o modelo com a mensagem criada

response.choices[0].message.content # Acessa o conteúdo da resposta do modelo