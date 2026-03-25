from __future__ import annotations

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import keyboard
import pyperclip

from audio_recorder import AudioRecorder
from config import APP_DIR, load_settings, save_settings
from history_store import HistoryStore
from language_service import LanguageService
from startup_manager import set_startup


class ChatHelperApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = load_settings()
        self.history_store = HistoryStore(limit=self.settings["history_limit"])
        self.recorder = AudioRecorder(sample_rate=self.settings["sample_rate"])

        self.current_chinese = ""
        self.current_english = ""
        self.last_audio_path: Path | None = None
        self.hotkey_handler = None

        self.root.title("Chinese to English Chat Helper")
        self.root.geometry("620x520")
        self.root.attributes("-topmost", self.settings["always_on_top"])
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_ui()
        self._register_hotkey()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Chinese to English Chat Helper", font=("Segoe UI", 13, "bold")).pack(anchor="w")

        top_btns = ttk.Frame(frame)
        top_btns.pack(fill="x", pady=8)

        self.start_btn = ttk.Button(top_btns, text="开始说话", command=self.start_recording)
        self.start_btn.pack(side="left", padx=2)
        self.stop_btn = ttk.Button(top_btns, text="停止录音", command=self.stop_recording, state="disabled")
        self.stop_btn.pack(side="left", padx=2)
        ttk.Button(top_btns, text="重新识别", command=self.retry_recognition).pack(side="left", padx=2)
        ttk.Button(top_btns, text="重新翻译", command=self.retry_translation).pack(side="left", padx=2)

        ttk.Label(frame, text="中文识别结果").pack(anchor="w")
        self.cn_text = tk.Text(frame, height=7, wrap="word")
        self.cn_text.pack(fill="x")

        ttk.Label(frame, text="英文翻译结果").pack(anchor="w", pady=(8, 0))
        self.en_text = tk.Text(frame, height=8, wrap="word")
        self.en_text.pack(fill="x")

        action_btns = ttk.Frame(frame)
        action_btns.pack(fill="x", pady=8)
        ttk.Button(action_btns, text="一键复制英文", command=self.copy_english).pack(side="left", padx=2)
        ttk.Button(action_btns, text="复制中英双语", command=self.copy_bilingual).pack(side="left", padx=2)
        ttk.Button(action_btns, text="清空", command=self.clear_texts).pack(side="left", padx=2)
        ttk.Button(action_btns, text="历史记录", command=self.open_history_window).pack(side="left", padx=2)
        ttk.Button(action_btns, text="设置", command=self.open_settings_window).pack(side="left", padx=2)

        self.status_var = tk.StringVar(value="就绪。按快捷键可呼出窗口。")
        ttk.Label(frame, textvariable=self.status_var, foreground="#0A5").pack(anchor="w", pady=(5, 0))

    def _register_hotkey(self) -> None:
        hotkey = self.settings["hotkey"]
        try:
            keyboard.unhook_all_hotkeys()
            self.hotkey_handler = keyboard.add_hotkey(hotkey, self.show_window)
            self.status_var.set(f"已注册全局快捷键: {hotkey}")
        except Exception as exc:
            self.status_var.set(f"快捷键注册失败: {exc}")

    def show_window(self) -> None:
        self.root.after(0, self._show_window_safe)

    def _show_window_safe(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def set_status(self, text: str) -> None:
        self.root.after(0, lambda: self.status_var.set(text))

    def start_recording(self) -> None:
        try:
            self.recorder.start()
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.set_status("录音中...请开始说中文。")
        except Exception as exc:
            messagebox.showerror("麦克风错误", f"无法开始录音：{exc}")

    def stop_recording(self) -> None:
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.set_status("处理中，请稍候...")

        def worker() -> None:
            try:
                audio_path = APP_DIR / "last_record.wav"
                self.last_audio_path = self.recorder.stop_and_save(audio_path)
                self._recognize_and_translate(self.last_audio_path)
            except Exception as exc:
                self.set_status(f"失败：{exc}")
                messagebox.showerror("处理失败", str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _make_service(self) -> LanguageService:
        key = self.settings.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")
        return LanguageService(
            api_key=key,
            transcribe_model=self.settings["openai_transcribe_model"],
            translate_model=self.settings["openai_translate_model"],
        )

    def _recognize_and_translate(self, audio_path: Path) -> None:
        service = self._make_service()
        chinese = service.transcribe_chinese(audio_path)
        english = service.translate_to_english(chinese, self.settings["translation_style"])
        self.current_chinese = chinese
        self.current_english = english
        self.root.after(0, lambda: self._update_texts(chinese, english))
        self.history_store.limit = int(self.settings["history_limit"])
        self.history_store.add(chinese, english)
        if self.settings.get("auto_copy_english"):
            pyperclip.copy(english)
            self.set_status("完成，英文已自动复制。")
        else:
            self.set_status("完成。")

    def _update_texts(self, chinese: str, english: str) -> None:
        self.cn_text.delete("1.0", "end")
        self.cn_text.insert("1.0", chinese)
        self.en_text.delete("1.0", "end")
        self.en_text.insert("1.0", english)

    def retry_recognition(self) -> None:
        if not self.last_audio_path or not self.last_audio_path.exists():
            messagebox.showinfo("提示", "没有可重试的录音。请先录音一次。")
            return

        self.set_status("重新识别中...")

        def worker() -> None:
            try:
                service = self._make_service()
                chinese = service.transcribe_chinese(self.last_audio_path)  # type: ignore[arg-type]
                self.current_chinese = chinese
                self.root.after(0, lambda: self._update_texts(chinese, self.current_english))
                self.set_status("重新识别完成。")
            except Exception as exc:
                self.set_status(f"重新识别失败：{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def retry_translation(self) -> None:
        chinese = self.cn_text.get("1.0", "end").strip()
        if not chinese:
            messagebox.showinfo("提示", "没有中文内容可翻译。")
            return

        self.set_status("重新翻译中...")

        def worker() -> None:
            try:
                service = self._make_service()
                english = service.translate_to_english(chinese, self.settings["translation_style"])
                self.current_chinese = chinese
                self.current_english = english
                self.root.after(0, lambda: self._update_texts(chinese, english))
                self.history_store.add(chinese, english)
                self.set_status("重新翻译完成。")
            except Exception as exc:
                self.set_status(f"重新翻译失败：{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def copy_english(self) -> None:
        english = self.en_text.get("1.0", "end").strip()
        if not english:
            messagebox.showinfo("提示", "英文内容为空。")
            return
        pyperclip.copy(english)
        self.set_status("英文已复制。")

    def copy_bilingual(self) -> None:
        chinese = self.cn_text.get("1.0", "end").strip()
        english = self.en_text.get("1.0", "end").strip()
        if not chinese and not english:
            messagebox.showinfo("提示", "没有内容可复制。")
            return
        pyperclip.copy(f"中文：{chinese}\nEnglish: {english}")
        self.set_status("中英内容已复制。")

    def clear_texts(self) -> None:
        self.cn_text.delete("1.0", "end")
        self.en_text.delete("1.0", "end")
        self.current_chinese = ""
        self.current_english = ""
        self.set_status("已清空。")

    def open_history_window(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("历史记录")
        win.geometry("700x420")
        txt = tk.Text(win, wrap="word")
        txt.pack(fill="both", expand=True)
        records = self.history_store.load()
        if not records:
            txt.insert("1.0", "暂无历史记录。")
            return

        lines = []
        for i, item in enumerate(records, start=1):
            lines.append(
                f"#{i}  {item.get('time', '')}\n"
                f"中文: {item.get('chinese', '')}\n"
                f"English: {item.get('english', '')}\n"
                f"{'-'*66}\n"
            )
        txt.insert("1.0", "\n".join(lines))

    def open_settings_window(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("设置")
        win.geometry("500x420")

        labels = ttk.Frame(win, padding=10)
        labels.pack(fill="both", expand=True)

        hotkey_var = tk.StringVar(value=self.settings["hotkey"])
        style_var = tk.StringVar(value=self.settings["translation_style"])
        top_var = tk.BooleanVar(value=self.settings["always_on_top"])
        auto_copy_var = tk.BooleanVar(value=self.settings["auto_copy_english"])
        startup_var = tk.BooleanVar(value=self.settings.get("startup_launch", False))
        history_var = tk.IntVar(value=self.settings["history_limit"])
        key_var = tk.StringVar(value=self.settings.get("openai_api_key", ""))

        ttk.Label(labels, text="全局快捷键 (如 ctrl+shift+space)").pack(anchor="w")
        ttk.Entry(labels, textvariable=hotkey_var).pack(fill="x", pady=(0, 8))

        ttk.Label(labels, text="翻译风格").pack(anchor="w")
        ttk.Combobox(labels, textvariable=style_var, values=["concise", "business", "polite"], state="readonly").pack(fill="x", pady=(0, 8))

        ttk.Checkbutton(labels, text="窗口置顶", variable=top_var).pack(anchor="w")
        ttk.Checkbutton(labels, text="翻译后自动复制英文", variable=auto_copy_var).pack(anchor="w")
        ttk.Checkbutton(labels, text="开机自动启动", variable=startup_var).pack(anchor="w", pady=(0, 8))

        ttk.Label(labels, text="历史记录条数 (5-200)").pack(anchor="w")
        ttk.Entry(labels, textvariable=history_var).pack(fill="x", pady=(0, 8))

        ttk.Label(labels, text="OpenAI API Key").pack(anchor="w")
        ttk.Entry(labels, textvariable=key_var, show="*").pack(fill="x", pady=(0, 12))

        def save() -> None:
            self.settings["hotkey"] = hotkey_var.get().strip()
            self.settings["translation_style"] = style_var.get().strip()
            self.settings["always_on_top"] = bool(top_var.get())
            self.settings["auto_copy_english"] = bool(auto_copy_var.get())
            self.settings["startup_launch"] = bool(startup_var.get())
            self.settings["history_limit"] = max(5, min(200, int(history_var.get())))
            self.settings["openai_api_key"] = key_var.get().strip()

            save_settings(self.settings)
            self.history_store.limit = self.settings["history_limit"]
            self.root.attributes("-topmost", self.settings["always_on_top"])
            self._register_hotkey()
            try:
                set_startup(self.settings["startup_launch"])
            except Exception as exc:
                messagebox.showwarning("提示", f"设置开机自启失败：{exc}")
            self.set_status("设置已保存。")
            win.destroy()

        ttk.Button(labels, text="保存设置", command=save).pack(anchor="e")

    def on_close(self) -> None:
        keyboard.unhook_all_hotkeys()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = ChatHelperApp(root)
    # 初始为可见；如需托盘模式可在后续版本扩展。
    root.mainloop()


if __name__ == "__main__":
    main()
