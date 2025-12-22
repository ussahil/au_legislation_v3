import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re



MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()

# -----------------------------
# Helpers
# -----------------------------

def normalize_heading(h: str) -> str:
    """
    Remove leading section numbers and excess whitespace.
    """
    return re.sub(r"^\s*\d+[A-Z]*\s*", "", h).strip()

def format_headings(title: str, items: list[str], max_items: int = 20) -> str:
    """
    Normalize and cap headings to avoid prompt bloat.
    """
    cleaned = [normalize_heading(h) for h in items if h.strip()]
    cleaned = cleaned[:max_items]
    lines = [f"- {h}" for h in cleaned]
    return f"{title}:\n" + "\n".join(lines)


def summarize(
    jurisdiction: str,
    act: str,
    act_headings: list[str],
    # subsection_headings: list[str],
    system_prompt: str,
    max_new_tokens: int = 300,
):
    """
    Generate an Act-level retrieval summary.
    """

    act_headings_txt = format_headings("Act-level topics", act_headings or [])
    # subsection_headings_txt = format_headings("Subordinate topics", subsection_headings or [])

    user_content = f"""
Jurisdiction: {jurisdiction}
Act name: {act}

{act_headings_txt}


INSTRUCTIONS:
- Write a high-level semantic summary of what this Act governs.
- Describe regulatory scope, administering bodies, and types of powers or obligations.
- Do NOT restate headings.
- Do NOT quote section numbers.
- Do NOT include procedural detail.
- Use neutral statutory language.
- Limit to 4-6 sentences.
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_content.strip()}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            # temperature=0.0,
            # top_p=1.0,
            eos_token_id=tokenizer.eos_token_id
        )

    generated = outputs[0][inputs.input_ids.shape[-1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True).strip()

    return text