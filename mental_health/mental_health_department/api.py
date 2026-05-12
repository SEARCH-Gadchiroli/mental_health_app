# Copyright (c) 2026, SEARCH Gadchiroli and contributors
# For license information, please see license.txt
"""
Server-side APIs for the MH Chatbot module.

All methods are whitelisted and called via frappe.call() from client scripts.
OpenAI API key is stored in MH Settings and never exposed to the browser.
"""

import frappe
import json
import math
import urllib.request
import urllib.error


# ──────────────────────────────────────────────────────────────────────────────
# Helper: get OpenAI API key from MH Settings (Admin-only DocType)
# ──────────────────────────────────────────────────────────────────────────────

def _get_api_key():
    # Use .get_password() to decrypt the value correctly
    api_key = frappe.get_doc("MH Settings").get_password("openai_api_key")
    if not api_key:
        frappe.throw(
            "OpenAI API key is not configured. Please set it in MH Settings.",
            title="Missing Configuration"
        )
    return api_key


def _get_model(field, default):
    val = frappe.db.get_single_value("MH Settings", field)
    return val or default


# ──────────────────────────────────────────────────────────────────────────────
# Helper: call OpenAI REST API (no external library needed)
# ──────────────────────────────────────────────────────────────────────────────

def _openai_post(endpoint, payload, api_key):
    url = f"https://api.openai.com/v1/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        frappe.throw(f"OpenAI API error ({e.code}): {body}", title="API Error")


# ──────────────────────────────────────────────────────────────────────────────
# Core: translate text to English via OpenAI
# ──────────────────────────────────────────────────────────────────────────────

def _translate_to_english(text, api_key, model):
    # Skip translation if the text is already English (no Devanagari characters)
    if not any('\u0900' <= char <= '\u097f' for char in text):
        return text.strip()

    result = _openai_post("chat/completions", {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional medical translator. "
                    "Translate the given text to English. Keep medical terms accurate."
                )
            },
            {"role": "user", "content": text}
        ]
    }, api_key)
    return result["choices"][0]["message"]["content"].strip()


# ──────────────────────────────────────────────────────────────────────────────
# Core: get text embedding from OpenAI
# ──────────────────────────────────────────────────────────────────────────────

def _get_embedding(text, api_key, model):
    result = _openai_post("embeddings", {
        "model": model,
        "input": text
    }, api_key)
    return result["data"][0]["embedding"]


# ──────────────────────────────────────────────────────────────────────────────
# Core: cosine similarity between two vectors
# ──────────────────────────────────────────────────────────────────────────────

def _cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC API: Calculate similarity scores for a consultation record
# Called from the `similarity_score` client script via frappe.call()
# ──────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def calculate_similarity_scores(docname):
    """
    Translates AI and Doctor outputs to English, generates embeddings,
    and returns cosine similarity scores (0–100) for:
      - Pharmacotherapy (ai_pharmacotherapy_output vs doctor_pharmacotherapy_output)
      - Diagnosis       (ai_diagnosis_output vs doctor_diagnosis_output)

    Returns a dict:
      {
        "pharmacotherapy_score": float | None,
        "diagnosis_score": float | None
      }
    """
    doc = frappe.get_doc("MH_Chatbot_Consultation_Glific", docname)

    api_key = _get_api_key()
    translation_model = _get_model("translation_model", "gpt-4o-mini")
    embedding_model = _get_model("embedding_model", "text-embedding-3-small")

    result = {}

    # ── Pharmacotherapy ───────────────────────────────────────────────────────
    if doc.ai_pharmacotherapy_output and doc.doctor_pharmacotherapy_output:
        ai_en = _translate_to_english(doc.ai_pharmacotherapy_output, api_key, translation_model)
        doc_en = _translate_to_english(doc.doctor_pharmacotherapy_output, api_key, translation_model)
        emb1 = _get_embedding(ai_en, api_key, embedding_model)
        emb2 = _get_embedding(doc_en, api_key, embedding_model)
        sim = _cosine_similarity(emb1, emb2)
        result["pharmacotherapy_score"] = round(max(0.0, sim) * 100, 2)
    else:
        result["pharmacotherapy_score"] = None

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    if doc.ai_diagnosis_output and doc.doctor_diagnosis_output:
        ai_en2 = _translate_to_english(doc.ai_diagnosis_output, api_key, translation_model)
        doc_en2 = _translate_to_english(doc.doctor_diagnosis_output, api_key, translation_model)
        emb3 = _get_embedding(ai_en2, api_key, embedding_model)
        emb4 = _get_embedding(doc_en2, api_key, embedding_model)
        sim2 = _cosine_similarity(emb3, emb4)
        result["diagnosis_score"] = round(max(0.0, sim2) * 100, 2)
    else:
        result["diagnosis_score"] = None

    return result


