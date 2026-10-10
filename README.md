# 🎵 BaixarMusicas GUI (YouTube para MP3)

Um aplicativo moderno, rápido e simples para baixar áudios do YouTube no formato MP3. Desenvolvido em Python, utilizando a biblioteca **CustomTkinter** para oferecer uma interface gráfica moderna e fluida em Dark Mode, e o poderoso **yt-dlp** para o processamento dos vídeos.

## ✨ Funcionalidades

- **Interface Moderna:** Design responsivo com suporte a Dark Mode.
- **Processamento em Segundo Plano:** A interface permanece responsiva durante os downloads, graças ao uso de multithreading.
- **Controle Total:** Escolha a pasta de destino para salvar suas músicas.
- **Feedback em Tempo Real:** Barras de progresso para acompanhar o andamento geral dos downloads e o progresso individual de cada arquivo.
- **Cancelamento Seguro:** Cancele downloads em andamento sem comprometer o funcionamento do aplicativo.
- **Executável Standalone:** Versão para Windows empacotada em um único arquivo `.exe`, sem necessidade de instalar o Python.

---

## 📥 Como baixar e usar (Para usuários)

O aplicativo é compilado automaticamente para Windows por meio do GitHub Actions. Para baixar a versão mais recente:

1. Acesse a aba [**Actions**](../../actions) deste repositório.
2. Selecione a execução mais recente concluída com sucesso, identificada pelo ícone verde (✅).
3. Role a página até a seção **Artifacts**.
4. Clique em `BaixarMusicas-Windows` para baixar o arquivo `.zip`.
5. Extraia o conteúdo do arquivo baixado.
6. Execute o arquivo `BaixarMusicas.exe`.

> **Aviso:** O GitHub exige que você esteja autenticado em uma conta para baixar arquivos da seção Artifacts. Esses arquivos também podem expirar de acordo com as configurações de retenção do workflow.

---

## 💻 Como executar localmente (Para desenvolvedores)

Se você utiliza Linux ou macOS, deseja executar o projeto diretamente pelo código-fonte ou pretende contribuir com o desenvolvimento, siga os passos abaixo.

### 1. Clone o repositório

Substitua `SEU_USUARIO` e `SEU_REPOSITORIO` pelos dados reais do repositório.

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Crie e ative um ambiente virtual

É recomendável utilizar um ambiente virtual para isolar as dependências do projeto.

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

Se o projeto possuir um arquivo `requirements.txt`, execute:

```bash
pip install -r requirements.txt
```

Caso o arquivo não esteja disponível, instale as dependências básicas manualmente:

```bash
pip install customtkinter yt-dlp pyinstaller
```

**Observação:** O FFmpeg também pode ser necessário para converter os áudios para MP3. Verifique se ele está instalado e disponível no PATH do sistema.

### 4. Execute o aplicativo

Com as dependências instaladas e o ambiente virtual ativado, execute:

```bash
python main.py
```

---

## 🛠️ Tecnologias utilizadas

- **Python 3.11+:** Linguagem de programação principal.
- **CustomTkinter:** Biblioteca utilizada para a construção da interface gráfica.
- **yt-dlp:** Ferramenta responsável pelo processamento e download de conteúdo compatível.
- **FFmpeg:** Ferramenta utilizada na conversão e no processamento de áudio.
- **PyInstaller:** Ferramenta para empacotamento do aplicativo em um executável.
- **GitHub Actions:** Automação do processo de compilação e disponibilização dos artefatos.

---

## ☕ Contribuições

Feito com ☕ e código!

Sinta-se à vontade para abrir uma [Issue](../../issues) para relatar problemas ou sugerir melhorias, ou enviar um Pull Request com suas contribuições.

**Importante:** Utilize o aplicativo apenas para baixar conteúdos que você possui autorização para baixar, respeitando os direitos autorais e os termos de serviço das plataformas envolvidas.
