# Avaliação Postural v3.1 - Atualização Manus AI

Este projeto foi atualizado para incorporar critérios de análise postural mais detalhados para as vistas anterior, posterior e lateral, além de adicionar a funcionalidade de geração de áudio com narrativa para guiar os exercícios propostos aos pacientes.

## 1. Melhorias Implementadas

As seguintes melhorias foram realizadas no código-fonte:

### 1.1. Análise Postural Aprimorada (Backend)

O arquivo `backend/src/services/posture_analysis_v2.py` foi criado para substituir a lógica anterior, implementando métricas mais robustas baseadas nas três vistas (anterior, posterior e lateral).

**Novos Critérios de Análise Incorporados:**

| Vista | Pontos Observados e Métricas |
| :--- | :--- |
| **Anterior** | **Cabeça:** Inclinação/Rotação (`head_tilt_angle`). **Ombros:** Altura desigual (`shoulder_height_difference`). **Quadris:** Diferença de altura (`hip_height_difference`). **Tronco:** Rotação do tronco (`trunk_rotation_offset`). **Joelhos:** Genu valgo/varo (`left_knee_angle`, `right_knee_angle`). |
| **Posterior** | **Coluna:** Desvio lateral (`spinal_lateral_deviation`). **Assimetria:** Simetria muscular e alinhamento da coluna e membros (inferido pela diferença de altura de ombros e quadris). |
| **Lateral (Perfil)** | **Cabeça:** Projeção anterior (`head_forward_distance`). **Alinhamento:** Alinhamento vertical da linha de gravidade (`vertical_alignment_score`). |

### 1.2. Geração de Áudio para Exercícios (Backend)

O módulo `backend/src/services/audio_generator.py` foi adicionado para:
1.  **Gerar uma narrativa** de exercício personalizada com base nos fatores de risco de postura identificados.
2.  **Utilizar o serviço de Text-to-Speech (TTS) da OpenAI** (modelo `tts-1`, voz `nova`) para converter a narrativa em um arquivo de áudio MP3.
3.  **Salvar o caminho do arquivo de áudio** (`audio_exercicio_path`) no banco de dados, associado à avaliação postural.

### 1.3. Integração e Banco de Dados

*   O arquivo `backend/src/routes/posture_analysis.py` foi atualizado para:
    *   Utilizar o novo analisador (`posture_analyzer_v2`).
    *   Chamar a função de geração de áudio após a análise.
    *   Salvar o caminho do áudio no banco de dados.
*   O modelo `AvaliacaoPostural` em `backend/src/models/user.py` foi modificado para incluir o campo `audio_exercicio_path`.

## 2. Instruções de Execução (Assumindo Ambiente Python/Flask)

Para executar o projeto com as novas funcionalidades, siga as instruções originais do projeto, garantindo que as novas dependências estejam instaladas.

### 2.1. Dependências

Certifique-se de que as seguintes bibliotecas Python estão instaladas:

```bash
pip install -r requirements.txt
pip install openai # Nova dependência
```

### 2.2. Configuração da API Key

O módulo de geração de áudio requer uma chave de API da OpenAI. Certifique-se de que a variável de ambiente `OPENAI_API_KEY` esteja configurada no seu ambiente de execução.

### 2.3. Execução do Backend

1.  Navegue até o diretório `backend/src`.
2.  Execute o servidor Flask:

    ```bash
    python main.py
    ```

### 2.4. Acesso ao Arquivo de Áudio

Após a análise postural via endpoint `/api/posture/analyze`, o JSON de resposta incluirá o campo `exercise_audio_path`. O arquivo de áudio MP3 gerado será salvo no diretório `backend/src/uploads/exercise_audio` e poderá ser acessado via URL de upload configurada no `main.py` (ex: `http://localhost:5000/uploads/exercise_audio/nome_do_arquivo.mp3`).

---

**Nota:** A lógica de geração de áudio (`audio_generator.py`) utiliza o primeiro fator de risco identificado para gerar a narrativa do exercício mais relevante. O frontend deve ser atualizado para consumir o novo campo `audio_exercicio_path` e reproduzir o áudio para o paciente.
