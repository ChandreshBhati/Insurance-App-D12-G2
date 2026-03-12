import os
import base64
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
[4-5 sentence simple explanation]

✅ KEY BENEFITS
- Benefit 1
- Benefit 2
- Benefit 3
- Benefit 4

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
    Tries multiple free Hugging Face models in order.
    Returns a base64 data URL — embeds directly in <img src="...">.
    No external URL issues, no browser blocks, no expiry.

    Models tried (in order):
    1. FLUX.1-schnell  — fastest, no token needed
    2. FLUX.1-dev      — better quality, needs HF_TOKEN
    3. stable-diffusion-2 — fallback, always available
    """

    prompt = (
        f"Professional insurance infographic about {policy_type}, "
        f"concept: {concept}, flat design, teal navy white color scheme, "
        f"clean icons, modern layout, no watermark, high quality"
    )

    hf_token = os.environ.get("HF_TOKEN", "")
    headers  = {"Content-Type": "application/json"}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    # ── Models to try in order ────────────────────────────────
    models = [
        "black-forest-labs/FLUX.1-schnell",   # fastest, no token needed
        "black-forest-labs/FLUX.1-dev",        # better quality, needs token
        "stabilityai/stable-diffusion-2",      # reliable fallback
    ]

    last_error = None

    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"inputs": prompt},
                timeout=90
            )

            if response.status_code == 200:
                # Convert raw bytes → base64 data URL
                img_b64 = base64.b64encode(response.content).decode("utf-8")
                return f"data:image/jpeg;base64,{img_b64}"

            elif response.status_code == 503:
                # Model loading — skip to next
                last_error = f"{model} is loading (503). Tried next model."
                continue

            elif response.status_code == 401:
                # Token needed — skip to next
                last_error = f"{model} requires HF token (401). Tried next model."
                continue

            elif response.status_code == 410:
                # Model removed — skip to next
                last_error = f"{model} no longer available (410). Tried next model."
                continue

            else:
                last_error = f"{model} returned HTTP {response.status_code}."
                continue

        except requests.exceptions.Timeout:
            last_error = f"{model} timed out. Tried next model."
            continue

        except Exception as e:
            last_error = str(e)
            continue

    # All models failed
    raise Exception(
        f"All image models failed. Last error: {last_error}. "
        "Add HF_TOKEN to your .env for better access. "
        "Get a free token at: https://huggingface.co/settings/tokens"
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