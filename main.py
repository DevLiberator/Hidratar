
import json
import sys
import time
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from plyer import notification


APP_NAME = "Hidra"
APP_TITLE = "Já se HIDRATOU hoje?"
DEFAULT_MESSAGE = "Hora de beber água. 💧"
DEFAULT_INTERVAL = 45
DEFAULT_DURATION = 8


def get_config_path():
    """Guarda as configurações na pasta do usuário."""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local" / "Hidra"
    else:
        base = Path.home() / ".config" / "hidra"

    base.mkdir(parents=True, exist_ok=True)
    return base / "config.json"


CONFIG_PATH = get_config_path()


def load_config():
    defaults = {
        "interval_minutes": DEFAULT_INTERVAL,
        "duration_hours": DEFAULT_DURATION,
        "message": DEFAULT_MESSAGE,
    }

    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            defaults.update({
                key: saved[key]
                for key in defaults
                if key in saved
            })
    except (OSError, ValueError, TypeError):
        pass

    return defaults


def save_config(config):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = CONFIG_PATH.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)

        temporary.replace(CONFIG_PATH)
    except OSError as error:
        print(f"Não foi possível salvar as configurações: {error}")


class HidraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hidra - Lembrete de Água")
        self.root.geometry("480x550")
        self.root.minsize(420, 500)

        self.config = load_config()

        self.interval_var = tk.StringVar(
            value=str(self.config["interval_minutes"])
        )
        self.duration_var = tk.StringVar(
            value=str(self.config["duration_hours"])
        )
        self.message_var = tk.StringVar(
            value=self.config["message"]
        )
        self.status_var = tk.StringVar(value="Pronto para começar")
        self.next_var = tk.StringVar(value="Próximo lembrete: --:--")
        self.remaining_var = tk.StringVar(value="Tempo restante: 08:00:00")

        self.running = False
        self.paused = False
        self.elapsed = 0.0
        self.last_tick = None
        self.last_reminder = 0.0
        self.last_error = None
        self.after_id = None

        self._build_ui()
        self._update_display()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text="💧 HIDRA",
            font=("TkDefaultFont", 24, "bold")
        ).pack(pady=(0, 3))

        ttk.Label(
            outer,
            text="Lembretes para manter sua hidratação",
            font=("TkDefaultFont", 10)
        ).pack(pady=(0, 18))

        settings = ttk.LabelFrame(
            outer, text=" Configurações ", padding=12
        )
        settings.pack(fill="x", pady=(0, 12))

        ttk.Label(
            settings, text="Intervalo entre lembretes (minutos):"
        ).grid(row=0, column=0, sticky="w", pady=6)

        ttk.Spinbox(
            settings, from_=1, to=1440,
            textvariable=self.interval_var, width=8
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        ttk.Label(
            settings, text="Duração total (horas):"
        ).grid(row=1, column=0, sticky="w", pady=6)

        ttk.Spinbox(
            settings, from_=1, to=24,
            textvariable=self.duration_var, width=8
        ).grid(row=1, column=1, sticky="e", padx=(8, 0))

        ttk.Label(
            settings, text="Mensagem da notificação:"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 4))

        ttk.Entry(
            settings, textvariable=self.message_var
        ).grid(row=3, column=0, columnspan=2, sticky="ew")

        settings.columnconfigure(0, weight=1)

        timers = ttk.LabelFrame(
            outer, text=" Temporizadores ", padding=12
        )
        timers.pack(fill="x", pady=(0, 12))

        ttk.Label(
            timers, textvariable=self.remaining_var,
            font=("TkDefaultFont", 12, "bold")
        ).pack(anchor="w", pady=4)

        ttk.Label(
            timers, textvariable=self.next_var
        ).pack(anchor="w", pady=4)

        ttk.Label(
            outer, textvariable=self.status_var,
            wraplength=410, justify="center"
        ).pack(fill="x", pady=(2, 12))

        buttons = ttk.Frame(outer)
        buttons.pack(fill="x")

        self.start_button = ttk.Button(
            buttons, text="▶ Iniciar", command=self.start
        )
        self.start_button.pack(
            side="left", fill="x", expand=True, padx=(0, 4)
        )

        self.pause_button = ttk.Button(
            buttons, text="⏸ Pausar", command=self.pause,
            state="disabled"
        )
        self.pause_button.pack(
            side="left", fill="x", expand=True, padx=4
        )

        self.stop_button = ttk.Button(
            buttons, text="■ Encerrar", command=self.stop,
            state="disabled"
        )
        self.stop_button.pack(
            side="left", fill="x", expand=True, padx=(4, 0)
        )

        ttk.Label(
            outer, text="As preferências são salvas neste computador.",
            font=("TkDefaultFont", 8)
        ).pack(pady=(14, 0))

    def _read_settings(self):
        try:
            interval = int(self.interval_var.get())
            duration = int(self.duration_var.get())
        except ValueError:
            messagebox.showerror(
                "Configuração inválida",
                "Informe números inteiros para intervalo e duração.",
                parent=self.root
            )
            return None

        if not 1 <= interval <= 1440:
            messagebox.showerror(
                "Intervalo inválido",
                "O intervalo deve ser entre 1 e 1440 minutos.",
                parent=self.root
            )
            return None

        if not 1 <= duration <= 24:
            messagebox.showerror(
                "Duração inválida",
                "A duração deve ser entre 1 e 24 horas.",
                parent=self.root
            )
            return None

        message = self.message_var.get().strip() or DEFAULT_MESSAGE

        self.config = {
            "interval_minutes": interval,
            "duration_hours": duration,
            "message": message,
        }
        save_config(self.config)
        return interval, duration, message

    def start(self):
        if self.running:
            return

        settings = self._read_settings()
        if settings is None:
            return

        interval, duration, message = settings

        self.interval_seconds = interval * 60
        self.duration_seconds = duration * 3600
        self.notification_message = message

        self.elapsed = 0.0
        self.last_reminder = 0.0
        self.last_tick = time.monotonic()
        self.running = True
        self.paused = False
        self.last_error = None

        self.status_var.set("Hidra está ativo. Beba água regularmente.")
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="⏸ Pausar")
        self.stop_button.configure(state="normal")

        self._schedule_tick()

    def pause(self):
        if not self.running:
            return

        if not self.paused:
            self._advance_clock()
            self.paused = True
            self.pause_button.configure(text="▶ Retomar")
            self.status_var.set("Temporizador pausado.")
        else:
            self.paused = False
            self.last_tick = time.monotonic()
            self.pause_button.configure(text="⏸ Pausar")
            self.status_var.set("Hidra está ativo.")

        self._update_display()

    def stop(self, finished=False):
        self.running = False
        self.paused = False
        self.last_tick = None

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="⏸ Pausar")
        self.stop_button.configure(state="disabled")

        if finished:
            self.elapsed = self.duration_seconds
            self.status_var.set("⏳ Tempo concluído. Até a próxima!")
        else:
            self.elapsed = 0.0
            self.status_var.set("Temporizador encerrado.")

        self._update_display()

    def _advance_clock(self):
        if self.running and not self.paused and self.last_tick is not None:
            now = time.monotonic()
            self.elapsed += max(0.0, now - self.last_tick)
            self.last_tick = now

    def _schedule_tick(self):
        if self.running and self.after_id is None:
            self.after_id = self.root.after(250, self._tick)

    def _tick(self):
        self.after_id = None

        if not self.running:
            return

        if not self.paused:
            self._advance_clock()

            if self.elapsed >= self.duration_seconds:
                self.stop(finished=True)
                return

            if self.elapsed - self.last_reminder >= self.interval_seconds:
                self.last_reminder = self.elapsed
                self._notify()

        self._update_display()
        self._schedule_tick()

    def _notify(self):
        try:
            notification.notify(
                title=APP_TITLE,
                message=self.notification_message,
                app_name=APP_NAME,
                timeout=10
            )
            self.last_error = None
        except Exception as error:
            self.last_error = str(error)
            self.status_var.set(
                "Não foi possível mostrar a notificação. "
                "Verifique o suporte a notificações do sistema."
            )

    @staticmethod
    def _format_time(seconds):
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"

    def _update_display(self):
        if not self.running:
            duration = self.config.get(
                "duration_hours", DEFAULT_DURATION
            ) * 3600
            self.remaining_var.set(
                f"Tempo restante: {self._format_time(duration)}"
            )
            self.next_var.set("Próximo lembrete: --:--")
            return

        remaining = max(0, self.duration_seconds - self.elapsed)
        self.remaining_var.set(
            f"Tempo restante: {self._format_time(remaining)}"
        )

        if self.paused:
            self.next_var.set("Próximo lembrete: pausado")
        else:
            until_next = self.interval_seconds - (
                self.elapsed - self.last_reminder
            )
            self.next_var.set(
                "Próximo lembrete: "
                + self._format_time(max(0, until_next))
            )

    def close(self):
        if self.running:
            should_close = messagebox.askyesno(
                "Fechar Hidra",
                "Deseja encerrar os lembretes e sair?",
                parent=self.root
            )
            if not should_close:
                return

        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    HidraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()