# YouTube ➜ MP3 / MP4

Programa simples, com janela, para baixar vídeos do YouTube como **MP3** (só o áudio), **MP4** (vídeo) ou **os dois de uma vez**.
Cole os links, escolha o formato e a pasta e clique em baixar. Feito com Python, [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) e [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## ⬇️ Baixar para Windows

### [**Clique aqui para baixar o programa (.exe)**](../../releases/latest/download/YT-MP3-Downloader.exe)

Não precisa instalar nada, nem Python, nem FFmpeg, nem usar o prompt de comando.

1. Clique no link acima. O arquivo `YT-MP3-Downloader.exe` será baixado.
2. Dê dois cliques nele para abrir.
3. Cole os links do YouTube (um por linha), escolha **Só MP3**, **Só MP4** ou **MP3 + MP4**, e clique em **Baixar**.

> Prefere ver todas as versões? Veja a página de [Releases](../../releases).

### O Windows mostrou um aviso azul. É seguro?

Ao abrir pela primeira vez, o Windows pode mostrar **"O Windows protegeu o computador"**. Isso acontece com qualquer programa novo que não tem assinatura digital paga, e este é gratuito e de código aberto.

Para abrir mesmo assim: clique em **Mais informações** e depois em **Executar assim mesmo**.

Alguns antivírus também podem marcar o arquivo por engano (falso positivo comum em programas feitos com PyInstaller). Todo o código-fonte está neste repositório, e o `.exe` é gerado automaticamente pelo GitHub a partir dele (veja `.github/workflows/build.yml`).

## Recursos

- Visual moderno (modo escuro)
- Escolha do formato: **só MP3**, **só MP4** ou **MP3 + MP4** (o MP3 é extraído do próprio vídeo, sem baixar duas vezes)
- Qualidade do vídeo MP4: 1080p, 720p, 480p ou 360p
- Vários links de uma vez, com progresso geral (“Baixando 2 de 5”) e barra do arquivo atual (Vídeo / Áudio)
- Botão **Cancelar** que interrompe com segurança
- Escolha da pasta de destino (o padrão é a pasta Downloads)
- O FFmpeg já vem dentro do `.exe`
- Uma versão nova é publicada automaticamente todo mês, com o yt-dlp atualizado

## Não funcionou?

O YouTube muda com frequência e isso pode quebrar downloads até que o yt-dlp seja atualizado. Se parar de funcionar, confira se há uma [versão mais nova](../../releases/latest) ou abra uma [issue](../../issues).

## Rodando pelo código (Linux, macOS, Windows)

Requer Python 3.10+ e o [FFmpeg](https://ffmpeg.org/download.html) instalado e no PATH.

```bash
pip install -r requirements.txt
python main.py
```

## Para quem mantém o projeto: como as versões são publicadas

O `.exe` é compilado pelo GitHub Actions (`.github/workflows/build.yml`) de três formas:

| Como | O que acontece |
| --- | --- |
| **Actions > Build Windows > Run workflow** | Teste: compila e deixa o `.exe` como *artefato* da execução. **Não** cria Release. |
| **Enviar uma tag** (`git tag v1.2.0` e `git push origin v1.2.0`) | Compila e cria a Release `v1.2.0` com o `.exe` anexado. |
| **Automático, dia 1 de cada mês** | Compila com o yt-dlp mais recente e cria a Release `vAAAA.MM.DD` (ex.: `v2026.11.01`). |

Se o repositório ficar sem nenhuma atividade por 60 dias, o GitHub pausa as execuções agendadas. Se isso acontecer, é só reativar em **Actions**.

## Aviso

Use apenas para conteúdo que você tem o direito de baixar (seus próprios vídeos, licenças livres/Creative Commons, domínio público). Respeite os Termos de Serviço do YouTube e a lei de direitos autorais do seu país. O autor não se responsabiliza pelo uso indevido da ferramenta.