from __future__ import annotations

from pathlib import Path

from openai import OpenAI

STYLE_PROMPTS = {
    "concise": "Use concise, natural business English. Keep the meaning accurate.",
    "business": "Use friendly, professional foreign-trade chat English for machinery parts and manufacturing communication.",
    "polite": "Use polite and professional English, suitable for customer communication, without over-expanding details.",
}

DOMAIN_HINT = (
    "You translate Chinese to English for industrial trade chats about CNC machining, screws, barrels, "
    "injection molding machines, extruders, spare parts, dimensions, materials, drawings, quotations, "
    "lead time, shipment, packaging, and payment terms. Keep technical terms accurate."
)


class LanguageService:
    def __init__(self, api_key: str, transcribe_model: str, translate_model: str) -> None:
        if not api_key.strip():
            raise ValueError("请先在设置中填写 OpenAI API Key。")
        self.client = OpenAI(api_key=api_key)
        self.transcribe_model = transcribe_model
        self.translate_model = translate_model

    def transcribe_chinese(self, audio_path: Path) -> str:
        with open(audio_path, "rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                model=self.transcribe_model,
                file=audio_file,
                language="zh",
            )
        text = (result.text or "").strip()
        if not text:
            raise RuntimeError("识别结果为空，请重试并说得更清楚一些。")
        return text

    def translate_to_english(self, chinese_text: str, style: str = "business") -> str:
        style_prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["business"])
        prompt = (
            f"{DOMAIN_HINT}\n"
            f"Style instruction: {style_prompt}\n"
            "Rules:\n"
            "1) Keep original meaning.\n"
            "2) Do not invent information.\n"
            "3) Keep dimensions, quantity, material specs exact.\n"
            "4) Output only final English text."
        )
        response = self.client.responses.create(
            model=self.translate_model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": chinese_text},
            ],
            temperature=0.2,
        )
        text = (response.output_text or "").strip()
        if not text:
            raise RuntimeError("翻译结果为空，请重试。")
        return text
