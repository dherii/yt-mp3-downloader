"""Baixador de MP3 do YouTube — CustomTkinter + yt-dlp.

Funciona tanto rodando direto com Python (Linux/Windows/macOS) quanto
empacotado com PyInstaller (--onefile) no Windows.
"""
from __future__ import annotations

import os
import queue
import shutil
import sys
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import DownloadCancelled


# ==========================================================
# Utilitários de caminho / ambiente
# ==========================================================
def obter_caminho_base() -> str:
    """Pasta temporária do PyInstaller (--onefile) ou diretório do script."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def caminho_recurso(*partes: str) -> str:
    """Resolve um arquivo empacotado (ex.: ffmpeg.exe, ícones) em qualquer ambiente."""
    return os.path.join(obter_caminho_base(), *partes)


def localizar_ffmpeg() -> str | None:
    """Retorna a PASTA onde está o ffmpeg, ou None se não for encontrado.

    Ordem: 1) embutido no executável (_MEIPASS) / ao lado do script; 2) PATH do sistema.
    """
    nome = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    if os.path.exists(caminho_recurso(nome)):
        return obter_caminho_base()
    no_path = shutil.which("ffmpeg")
    if no_path:
        return os.path.dirname(no_path)
    return None


def obter_pasta_downloads() -> Path:
    """Pasta 'Downloads' do usuário, de forma multiplataforma."""
    home = Path.home()
    try:
        if sys.platform == "win32":
            import winreg

            chave = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            guid_downloads = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave) as k:
                valor, _ = winreg.QueryValueEx(k, guid_downloads)
            caminho = Path(os.path.expandvars(valor))
            if caminho.is_dir():
                return caminho
        elif sys.platform.startswith("linux"):
            config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
            arquivo = config / "user-dirs.dirs"
            if arquivo.exists():
                for linha in arquivo.read_text(encoding="utf-8").splitlines():
                    if linha.startswith("XDG_DOWNLOAD_DIR"):
                        valor = linha.split("=", 1)[1].strip().strip('"')
                        caminho = Path(valor.replace("$HOME", str(home)))
                        if caminho.is_dir():
                            return caminho
    except Exception:
        pass  # cai no padrão abaixo
    return home / "Downloads"


# ==========================================================
# Infra do yt-dlp
# ==========================================================
class DownloadCancelado(DownloadCancelled):
    """Levantada no progress_hook para interromper o yt-dlp com segurança."""

    msg = "Download cancelado pelo usuário."


class LoggerSilencioso:
    """Evita que o yt-dlp escreva em stdout/stderr (que são None com --windowed)."""

    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


# ==========================================================
# Aplicação
# ==========================================================
class App(ctk.CTk):
    COR_VERDE = ("#2E7D32", "#2E7D32")
    COR_VERDE_HOVER = ("#1B5E20", "#1B5E20")
    COR_VERMELHO = ("#C62828", "#C62828")
    COR_VERMELHO_HOVER = ("#8E0000", "#8E0000")

    def __init__(self):
        super().__init__()
        self.title("Baixar MP3 do YouTube")
        self.geometry("660x580")
        self.minsize(580, 540)

        # Estado
        self.cancelar = False
        self.baixando = False
        self._texto_geral = "Pronto para baixar"
        self._ultimo_envio = 0.0
        self.fila: queue.Queue = queue.Queue()  # thread de download -> UI
        self.var_pasta = ctk.StringVar(value=str(obter_pasta_downloads()))

        self._construir_interface()
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        self.after(100, self._processar_fila)

    # ------------------------------------------------------
    # Interface
    # ------------------------------------------------------
    def _construir_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=16)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)  # a caixa de URLs cresce com a janela

        ctk.CTkLabel(
            card, text="YouTube  ➜  MP3", font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(22, 2))

        ctk.CTkLabel(
            card,
            text="Cole os links abaixo (um por linha):",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 8))

        self.entrada_urls = ctk.CTkTextbox(
            card, corner_radius=10, border_width=1, font=ctk.CTkFont(size=13)
        )
        self.entrada_urls.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.entrada_urls.focus()

        # --- Pasta de destino ---
        ctk.CTkLabel(
            card, text="Salvar em:", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 6))

        linha_pasta = ctk.CTkFrame(card, fg_color="transparent")
        linha_pasta.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 18))
        linha_pasta.grid_columnconfigure(0, weight=1)

        self.entrada_pasta = ctk.CTkEntry(
            linha_pasta, textvariable=self.var_pasta, height=36, corner_radius=8
        )
        self.entrada_pasta.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.botao_procurar = ctk.CTkButton(
            linha_pasta, text="Procurar...", width=110, height=36,
            corner_radius=8, command=self._escolher_pasta,
        )
        self.botao_procurar.grid(row=0, column=1)

        # --- Botões de ação ---
        linha_botoes = ctk.CTkFrame(card, fg_color="transparent")
        linha_botoes.grid(row=5, column=0, sticky="ew", padx=24, pady=(0, 18))
        linha_botoes.grid_columnconfigure(0, weight=3)
        linha_botoes.grid_columnconfigure(1, weight=1)

        self.botao_baixar = ctk.CTkButton(
            linha_botoes, text="📥  Baixar Áudios (MP3)", height=44, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.COR_VERDE, hover_color=self.COR_VERDE_HOVER,
            command=self._iniciar_download,
        )
        self.botao_baixar.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.botao_cancelar = ctk.CTkButton(
            linha_botoes, text="Cancelar", height=44, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.COR_VERMELHO, hover_color=self.COR_VERMELHO_HOVER,
            state="disabled", command=self._cancelar_download,
        )
        self.botao_cancelar.grid(row=0, column=1, sticky="ew")

        # --- Feedback duplo ---
        self.rotulo_status = ctk.CTkLabel(
            card, text=self._texto_geral, anchor="w", font=ctk.CTkFont(size=13, weight="bold")
        )
        self.rotulo_status.grid(row=6, column=0, sticky="ew", padx=24)

        self.rotulo_arquivo = ctk.CTkLabel(
            card, text="", anchor="w", font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
        )
        self.rotulo_arquivo.grid(row=7, column=0, sticky="ew", padx=24, pady=(2, 6))

        self.barra = ctk.CTkProgressBar(card, height=14, corner_radius=7)
        self.barra.set(0)
        self.barra.grid(row=8, column=0, sticky="ew", padx=24, pady=(0, 24))

    # ------------------------------------------------------
    # Ações da UI
    # ------------------------------------------------------
    def _escolher_pasta(self):
        escolhida = filedialog.askdirectory(
            parent=self,
            title="Escolher pasta de destino",
            initialdir=self.var_pasta.get() or None,
        )
        if escolhida:
            self.var_pasta.set(escolhida)

    def _iniciar_download(self):
        if self.baixando:
            return

        texto = self.entrada_urls.get("1.0", "end").strip()
        urls = [u.strip() for u in texto.splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("Aviso", "Por favor, cole pelo menos um link válido do YouTube.")
            return

        texto_pasta = self.var_pasta.get().strip()
        if not texto_pasta:
            messagebox.showwarning("Aviso", "Escolha a pasta onde os MP3 serão salvos.")
            return
        pasta = Path(texto_pasta).expanduser()
        try:
            pasta.mkdir(parents=True, exist_ok=True)
        except OSError as erro:
            messagebox.showerror("Erro", f"Não foi possível usar a pasta de destino:\n{erro}")
            return

        ffmpeg_dir = localizar_ffmpeg()
        if ffmpeg_dir is None:
            messagebox.showerror(
                "FFmpeg não encontrado",
                "O FFmpeg é necessário para converter o áudio em MP3.\n"
                "Instale-o e adicione ao PATH, ou coloque o ffmpeg ao lado do programa.",
            )
            return

        self.cancelar = False
        self._alternar_estado(baixando=True)
        self._definir_status_geral("Iniciando...")
        self.rotulo_arquivo.configure(text="")
        self.barra.set(0)

        threading.Thread(
            target=self._executar_download, args=(urls, pasta, ffmpeg_dir), daemon=True
        ).start()

    def _cancelar_download(self):
        self.cancelar = True
        self.botao_cancelar.configure(state="disabled", text="Cancelando...")
        self._definir_status_geral("Cancelando...")

    def _ao_fechar(self):
        if self.baixando and not messagebox.askyesno(
            "Sair", "Há downloads em andamento. Deseja cancelar e sair?"
        ):
            return
        self.cancelar = True
        self.destroy()

    def _alternar_estado(self, baixando: bool):
        self.baixando = baixando
        self.botao_baixar.configure(state="disabled" if baixando else "normal")
        self.botao_procurar.configure(state="disabled" if baixando else "normal")
        self.entrada_pasta.configure(state="disabled" if baixando else "normal")
        self.botao_cancelar.configure(
            state="normal" if baixando else "disabled", text="Cancelar"
        )

    def _definir_status_geral(self, texto: str):
        self._texto_geral = texto
        self.rotulo_status.configure(text=texto)

    @staticmethod
    def _encurtar(texto: str, limite: int = 70) -> str:
        return texto if len(texto) <= limite else texto[: limite - 1] + "…"

    # ------------------------------------------------------
    # Ponte thread -> UI (tkinter não é thread-safe: tudo passa pela fila)
    # ------------------------------------------------------
    def _processar_fila(self):
        try:
            while True:
                msg = self.fila.get_nowait()
                tipo = msg[0]
                if tipo == "geral":
                    self._definir_status_geral(msg[1])
                elif tipo == "arquivo":
                    _, fracao, titulo = msg
                    self.barra.set(fracao)
                    if titulo:
                        self.rotulo_arquivo.configure(
                            text=f"{self._encurtar(titulo)} — {fracao * 100:.0f}%"
                        )
                elif tipo == "convertendo":
                    self.rotulo_status.configure(text=f"{self._texto_geral} — Convertendo áudio...")
                elif tipo == "fim":
                    self._finalizar(*msg[1:])
                elif tipo == "fatal":
                    self._erro_fatal(msg[1])
        except queue.Empty:
            pass
        finally:
            self.after(100, self._processar_fila)

    def _finalizar(self, sucessos: int, total: int, erros: list[str], cancelado: bool, pasta: str):
        self._alternar_estado(baixando=False)
        self.barra.set(0)
        self.rotulo_arquivo.configure(text="")

        if cancelado:
            self._definir_status_geral(f"Cancelado ({sucessos} de {total} concluído(s)).")
        elif erros:
            self._definir_status_geral("Concluído com alguns erros.")
            messagebox.showwarning(
                "Aviso",
                f"Download finalizado, mas {len(erros)} link(s) falharam.\n"
                "Verifique se as URLs estão corretas ou se o vídeo é privado.",
            )
        else:
            self._definir_status_geral("Todos os downloads concluídos!")
            messagebox.showinfo(
                "Sucesso", f"{total} música(s) baixada(s) e salva(s) como MP3 em:\n{pasta}"
            )

    def _erro_fatal(self, detalhe: str):
        self._alternar_estado(baixando=False)
        self.barra.set(0)
        self._definir_status_geral("Erro fatal durante o processo.")
        messagebox.showerror("Erro", f"Ocorreu uma falha inesperada:\n{detalhe}")

    # ------------------------------------------------------
    # Download (roda em thread daemon)
    # ------------------------------------------------------
    def _hook_progresso(self, d: dict):
        # Ponto de cancelamento: o yt-dlp chama este hook a cada bloco baixado.
        if self.cancelar:
            raise DownloadCancelado()

        status = d.get("status")
        titulo = (d.get("info_dict") or {}).get("title", "")

        if status == "downloading":
            agora = time.monotonic()
            if agora - self._ultimo_envio < 0.1:  # limita a ~10 atualizações/s
                return
            self._ultimo_envio = agora
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            baixado = d.get("downloaded_bytes", 0)
            if total:
                self.fila.put(("arquivo", min(baixado / total, 1.0), titulo))
        elif status == "finished":
            self.fila.put(("arquivo", 1.0, titulo))
            self.fila.put(("convertendo",))

    def _montar_opcoes(self, pasta: Path, ffmpeg_dir: str) -> dict:
        return {
            "format": "bestaudio/best",
            "outtmpl": str(pasta / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "extractor_args": {
                "youtube": {"player_client": ["android", "ios", "web_creator"]}
            },
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "progress_hooks": [self._hook_progresso],
            "ffmpeg_location": ffmpeg_dir,
            "logger": LoggerSilencioso(),
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
        }

    def _executar_download(self, urls: list[str], pasta: Path, ffmpeg_dir: str):
        total = len(urls)
        sucessos = 0
        erros: list[str] = []
        cancelado = False

        try:
            with yt_dlp.YoutubeDL(self._montar_opcoes(pasta, ffmpeg_dir)) as ydl:
                for i, url in enumerate(urls, 1):
                    if self.cancelar:
                        cancelado = True
                        break

                    self.fila.put(("geral", f"Baixando {i} de {total}..."))
                    self.fila.put(("arquivo", 0.0, ""))
                    try:
                        ydl.download([url])
                        sucessos += 1
                    except DownloadCancelled:
                        cancelado = True
                        break
                    except Exception:
                        erros.append(url)
        except Exception as erro:
            self.fila.put(("fatal", str(erro)))
            return

        self.fila.put(("fim", sucessos, total, erros, cancelado, str(pasta)))


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # tema embutido -> exige --add-data no PyInstaller
    App().mainloop()


if __name__ == "__main__":
    main()