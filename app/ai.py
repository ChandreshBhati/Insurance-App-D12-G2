import os
import base64
import io
import requests
from groq import Groq

# ── Initialize Groq client ────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# ── FUNCTION 1: Text Explanation ──────────────────────────────
def generate_policy_explanation(user_prompt: str, policy_type: str) -> str:
    system_prompt = f"""
You are an expert insurance advisor specializing in Indian insurance products.
You explain {policy_type} clearly and concisely for customers.

Always structure your response exactly like this:

📋 OVERVIEW
[6-10 lines detailed sentence simple explanation]



⚠️ IMPORTANT TO KNOW
[One critical thing the customer must be aware of pertaining to indian market]

💰 ESTIMATED PREMIUM RANGE
[Realistic INR range per year if applicable]

Keep the tone professional but easy to understand.
Do not use markdown bold — use plain text only.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        max_tokens=600,
        temperature=0.7
    )
    return response.choices[0].message.content


# ── FUNCTION 2: Image Generation ──────────────────────────────
def generate_risk_infographic(policy_type: str, concept: str) -> str:
    """
    Priority:
    1. Gemini 3.1 Flash Image  — 500 free/day (fresh key needed if quota hit)
    2. FLUX.1-dev via HF       — provider=auto (HF picks fastest free provider)
    3. FLUX.1-schnell via HF   — faster fallback
    4. Together AI + FLUX      — uses your TOGETHER_API_KEY

    Returns base64 data URL for direct <img> embedding.
    """
    prompt = (
        f"Professional insurance visual diagram about {policy_type}, "
        f"topic: {concept}, "
        f"MINIMAL TEXT, icon-driven design, symbols and shapes only, "
        f"flat design, teal and navy blue color palette, "
        f"simple short 1-2 word labels only, large clear icons, "
        f"flowchart arrows, pie chart, bar graph, "
        f"shield heart car medical cross icons, "
        f"white background, no watermark, no paragraphs, "
        f"high quality clean professional infographic"
    )

    gemini_key  = os.environ.get("GEMINI_API_KEY", "")
    hf_token    = os.environ.get("HF_TOKEN", "")
    together_key = os.environ.get("TOGETHER_API_KEY", "")

    # ── Method 1: Gemini 3.1 Flash Image ──────────────────────
    if gemini_key:
        for model in ["gemini-3.1-flash-image-preview", "gemini-2.5-flash-image"]:
            try:
                print(f"[Image] Trying Gemini {model}...")
                url = (
                    f"https://generativelanguage.googleapis.com"
                    f"/v1beta/models/{model}:generateContent"
                    f"?key={gemini_key}"
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"]
                    }
                }
                resp = requests.post(url, json=payload,
                                     headers={"Content-Type": "application/json"},
                                     timeout=45)
                if resp.status_code == 200:
                    parts = resp.json()["candidates"][0]["content"]["parts"]
                    for part in parts:
                        if "inlineData" in part:
                            img_b64 = part["inlineData"]["data"]
                            mime    = part["inlineData"].get("mimeType", "image/png")
                            print(f"[Image] Gemini {model} success!")
                            return f"data:{mime};base64,{img_b64}"
                    print(f"[Gemini {model}] No image in response")
                elif resp.status_code == 429:
                    print(f"[Gemini {model}] Quota exceeded")
                    continue
                elif resp.status_code == 404:
                    print(f"[Gemini {model}] Not found — trying next")
                    continue
                else:
                    print(f"[Gemini {model}] HTTP {resp.status_code}")
                    continue
            except Exception as e:
                print(f"[Gemini {model}] Error: {e}")
                continue

    # ── Method 2: FLUX.1-dev via HF (provider=auto) ───────────
    # provider="auto" → HF picks fastest available free provider
    # Confirmed providers for FLUX: wavespeed, fal-ai, together
    if hf_token:
        from huggingface_hub import InferenceClient

        flux_attempts = [
            # (model, provider, api_key)
            ("black-forest-labs/FLUX.1-dev",     "auto",      hf_token),
            ("black-forest-labs/FLUX.1-schnell", "auto",      hf_token),
            ("black-forest-labs/FLUX.1-dev",     "together",  together_key or hf_token),
            ("black-forest-labs/FLUX.1-schnell", "together",  together_key or hf_token),
        ]

        for model, provider, api_key in flux_attempts:
            if not api_key:
                continue
            try:
                print(f"[Image] Trying HF {model} provider={provider}...")

                hf_client = InferenceClient(
                    provider=provider,
                    api_key=api_key
                )

                image = hf_client.text_to_image(
                    prompt=prompt,
                    model=model
                )

                buffer = io.BytesIO()
                image.save(buffer, format="JPEG", quality=90)
                buffer.seek(0)
                img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
                print(f"[Image] HF {model} ({provider}) success!")
                return f"data:image/jpeg;base64,{img_b64}"

            except Exception as e:
                print(f"[HF {model} {provider}] Error: {e}")
                continue

    raise Exception(
        "Image generation failed. Please:\n"
        "1. Create a NEW Gemini key at https://aistudio.google.com/apikey\n"
        "   (each new key = fresh 500 free images/day)\n"
        "2. Make sure HF_TOKEN is in your .env\n"
        "3. If on college WiFi — switch to mobile hotspot"
    )


# ── FUNCTION 3: Policy Summary ────────────────────────────────
def generate_policy_summary(policy_type: str,
                             customer_name: str,
                             premium: float) -> str:
    prompt = f"""
Write a 3-sentence plain English summary for a customer named {customer_name}
who just purchased a {policy_type} policy with a yearly premium of ₹{premium:.2f}.
Explain what they are covered for, what they should do next,
and one important thing to remember.
Keep it warm, reassuring and under 80 words. Plain text only.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.6
    )
    return response.choices[0].message.content
