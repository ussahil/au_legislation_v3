import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

def compute_max_new_tokens(text):
    base = 100
    increment = 10
    per_chars = 1000
    cap = 250
    return min(base + (len(text) // per_chars) * increment, cap)

def summarize(text: str, act_head: str, subsection_head: str, system_prompt: str):
    max_tokens = compute_max_new_tokens(text)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"""
Summarize the following statutory provision in 2–4 sentences.
Retain defined terms and obligations verbatim where possible.
Do not paraphrase section titles.

Act Head: {act_head}
Subsection Head: {subsection_head}

Text:
{text}
"""
        }
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
            max_new_tokens=max_tokens,
            temperature=0.1,
            top_p=0.9,
            do_sample=False
        )

    generated = outputs[0][inputs.input_ids.shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()
