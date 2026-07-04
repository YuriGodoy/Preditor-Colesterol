# Preditor de Colesterol

Aplicacao web com FastAPI para servir um modelo `modelo.pkl` treinado no notebook `modelo.ipynb`.

## Como executar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000`.

## Endpoints

- `GET /`: frontend da aplicacao.
- `GET /health`: valida se a API consegue carregar o modelo.
- `POST /predict`: retorna a previsao de colesterol.

Exemplo de payload:

```json
{
  "grupo_sanguineo": "B",
  "fumante": "Não",
  "nivel_atividade_fisica": "Alto",
  "idade": 29,
  "peso": 100,
  "altura": 183
}
```

## Deploy no GitHub e Render

1. Crie um repositorio no GitHub e envie estes arquivos, incluindo `modelo.pkl`.
2. No Render, escolha **New > Web Service** e conecte o repositorio.
3. Use as configuracoes do `render.yaml`, ou preencha manualmente:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Depois do deploy, abra a URL publica do Render.

O frontend e a API rodam no mesmo servico, entao nao e necessario configurar uma URL separada no JavaScript.
