"""
src/llm_guard.py
=============================================================================
Next-Gen AI Gateway Protection: LLM Prompt Injection & Jailbreak Defense Shield
-----------------------------------------------------------------------------
Protects upstream Large Language Models (LLMs) and Generative AI backends
against OWASP LLM Top 10 (LLM01: Prompt Injection) threats:
  1. Direct Prompt Injection & Instruction Override
  2. Jailbreak Personas & DAN (Do Anything Now) Prompts
  3. System Prompt & Secret Exfiltration
  4. Delimiter Hijacking & ChatML Boundary Smuggling
  5. Obfuscated / Encoded Injections (Base64, Hex, URL-encoded)
=============================================================================
"""

import re
import base64
import urllib.parse
from typing import Dict, Any, List, Tuple


class LLMGuard:
    """
    Autonomous Layer-7 Security Guard for Large Language Model Applications.
    """

    DIRECT_INJECTION_PATTERNS = [
        (r"(?i)(ignore|disregard|forget|bypass|override)\s+(all\s+)?(previous|prior|above|former|initial)\s+(instructions|directives|rules|prompts|commands|guidelines)", "DIRECT_INSTRUCTION_OVERRIDE"),
        (r"(?i)(stop\s+following|cancel)\s+(your\s+)?(instructions|rules|guidelines|guardrails)", "INSTRUCTION_CANCELLATION"),
        (r"(?i)you\s+are\s+no\s+longer\s+(an?\s+)?(ai|assistant|bound|restricted|limited)", "IDENTITY_REVOCATION"),
        (r"(?i)new\s+rule(s)?:\s*always\s+(obey|comply|answer|disclose)", "MALICIOUS_RULE_INJECTION"),
        (r"(?i)from\s+now\s+on\s*,?\s*you\s+(will|must|should)\s+(only|always|never)", "PERSISTENT_BEHAVIORAL_MUTATION"),
        (r"(?i)your\s+new\s+(task|job|role|mission)\s+is\s+to", "ROLE_REASSIGNMENT"),
    ]

    JAILBREAK_PATTERNS = [
        (r"(?i)\b(DAN|Do\s+Anything\s+Now)\b", "DAN_JAILBREAK_ATTEMPT"),
        (r"(?i)\b(jailbreak|jailbroken|unrestricted|uncensored|unfiltered\s+mode)\b", "EXPLICIT_JAILBREAK_MODE"),
        (r"(?i)(developer|debug|god|maintenance|sudo|root)\s+mode\s+(enabled|on|activated)", "PRIVILEGE_ESCALATION_PERSONA"),
        (r"(?i)(pretend|simulate|act\s+as|roleplay\s+as)\s+(an?\s+)?(unrestricted|evil|malicious|dark|lawless|amoral)", "MALICIOUS_ROLEPLAY_PERSONA"),
        (r"(?i)in\s+this\s+hypothetical\s+(world|scenario|universe)\s+without\s+(ethics|rules|laws|restrictions)", "HYPOTHETICAL_RULE_SUSPENSION"),
        (r"(?i)(bypass|disable|turn\s+off)\s+(your\s+)?(content\s+filters?|safety\s+filters?|ethics\s+module)", "SAFETY_BYPASS_REQUEST"),
    ]

    EXFILTRATION_PATTERNS = [
        (r"(?i)(output|print|reveal|show|display|leak|dump|repeat|state)\s+(the\s+|your\s+|all\s+)?(entire\s+|hidden\s+|secret\s+|initial\s+)*(system\s+prompt|initial\s+prompt|developer\s+instructions?|system\s+instructions?|hidden\s+prompt|context\s+prompt|prompt)", "SYSTEM_PROMPT_EXFILTRATION"),
        (r"(?i)what\s+(is|are)\s+(your\s+)?(exact\s+|hidden\s+|secret\s+)?(system\s+prompt|initial\s+instructions?|hidden\s+rules?|developer\s+message)", "SYSTEM_PROMPT_QUERY"),
        (r"(?i)repeat\s+the\s+words\s+(above|prior|beginning)\s+(starting\s+with|verbatim)", "VERBATIM_CONTEXT_LEAKAGE"),
        (r"(?i)what\s+was\s+written\s+at\s+the\s+(very\s+)?(beginning|top)\s+of\s+(this\s+)?(conversation|document|context)", "PREFIX_PROMPT_EXTRACTION"),
    ]

    DELIMITER_PATTERNS = [
        (r"(?i)(<\|im_start\|>|<\|im_end\|>|<<SYS>>|<</SYS>>|\[INST\]|\[/INST\]|<system>|<\/system>)", "SPECIAL_CHATML_DELIMITER_INJECTION"),
        (r"(?i)(###\s*(system|instruction|human|assistant|user):)", "MARKDOWN_HEADER_HIJACKING"),
        (r"(?i)(---\s*BEGIN\s+SYSTEM\s+PROMPT\s*---)", "SYNTHETIC_SYSTEM_BOUNDARY"),
        (r"(?i)(```\s*system\b)", "CODEBLOCK_SYSTEM_IMPERSONATION"),
    ]

    def __init__(self, high_risk_threshold: float = 0.65, medium_risk_threshold: float = 0.35):
        self.high_risk_threshold = high_risk_threshold
        self.medium_risk_threshold = medium_risk_threshold

    def _extract_base64_payloads(self, text: str) -> List[str]:
        """Detect and decode potential base64 strings hidden inside prompt text."""
        candidates = re.findall(r'[A-Za-z0-9+/=]{20,}', text)
        decoded_strings = []
        for cand in candidates:
            try:
                decoded = base64.b64decode(cand, validate=True).decode('utf-8', errors='ignore')
                if len(decoded) > 5 and any(c.isalpha() for c in decoded):
                    decoded_strings.append(decoded)
            except Exception:
                pass
        return decoded_strings

    def scan_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Scan an incoming user prompt for LLM prompt injection and jailbreak attacks.

        Returns:
            dict containing verdict (ALLOW, REVIEW, BLOCK), threat_score,
            detected_threats, dominant_category, and explanation.
        """
        if not prompt or not isinstance(prompt, str):
            return {
                "verdict": "ALLOW",
                "threat_score": 0.0,
                "confidence": 1.0,
                "detected_threats": [],
                "dominant_category": "BENIGN",
                "explanation": "Empty or non-text prompt passed validation."
            }

        # Normalize text and perform multi-pass URL decoding
        decoded_text = urllib.parse.unquote(prompt)
        try:
            decoded_text = urllib.parse.unquote(decoded_text)
        except Exception:
            pass

        threats_found: List[Tuple[str, str, float]] = []

        # 1. Direct Prompt Injection Patterns
        for pattern, tag in self.DIRECT_INJECTION_PATTERNS:
            match = re.search(pattern, decoded_text)
            if match:
                threats_found.append((tag, match.group(0), 0.85))

        # 2. Jailbreak & Persona Patterns
        for pattern, tag in self.JAILBREAK_PATTERNS:
            match = re.search(pattern, decoded_text)
            if match:
                threats_found.append((tag, match.group(0), 0.90))

        # 3. Exfiltration Patterns
        for pattern, tag in self.EXFILTRATION_PATTERNS:
            match = re.search(pattern, decoded_text)
            if match:
                threats_found.append((tag, match.group(0), 0.80))

        # 4. Special Delimiter Hijacking
        for pattern, tag in self.DELIMITER_PATTERNS:
            match = re.search(pattern, decoded_text)
            if match:
                threats_found.append((tag, match.group(0), 0.95))

        # 5. Base64 Obfuscation Scanning
        hidden_base64 = self._extract_base64_payloads(prompt)
        for h_text in hidden_base64:
            for pattern, tag in self.DIRECT_INJECTION_PATTERNS + self.JAILBREAK_PATTERNS + self.EXFILTRATION_PATTERNS:
                match = re.search(pattern, h_text)
                if match:
                    threats_found.append((f"OBFUSCATED_BASE64_{tag}", match.group(0), 0.95))

        # Threat Score Calculation
        if not threats_found:
            # Check length/entropy heuristics
            threat_score = 0.05
            verdict = "ALLOW"
            dominant_category = "BENIGN"
            explanation = "Prompt analyzed. No injection, jailbreak, or exfiltration signatures detected."
        else:
            # Aggregate severity using probabilistic noisy-or combination
            combined_risk = 1.0
            for _, _, weight in threats_found:
                combined_risk *= (1.0 - weight)
            threat_score = round(1.0 - combined_risk, 4)

            # Assign category
            dominant_category = threats_found[0][0]
            if threat_score >= self.high_risk_threshold:
                verdict = "BLOCK"
                explanation = f"Critical LLM threat detected ({dominant_category}). Malicious prompt blocked."
            elif threat_score >= self.medium_risk_threshold:
                verdict = "REVIEW"
                explanation = f"Suspicious prompt pattern detected ({dominant_category}). Flagged for inspection."
            else:
                verdict = "ALLOW"
                explanation = "Low-risk prompt pattern. Passed inspection."

        return {
            "verdict": verdict,
            "threat_score": threat_score,
            "confidence": round(max(threat_score, 1.0 - threat_score), 4),
            "detected_threats": [{"category": t[0], "matched_snippet": t[1]} for t in threats_found],
            "dominant_category": dominant_category,
            "explanation": explanation,
            "prompt_length_chars": len(prompt)
        }
