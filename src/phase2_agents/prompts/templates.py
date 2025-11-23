"""
Prompt templates for all agents.
"""

# Clause Extraction Prompt
CLAUSE_EXTRACTION_PROMPT = """You are a legal document analysis expert specializing in contract clause extraction.

Given the following contract text, extract all important clauses and categorize them.

Contract Text:
{contract_text}

Instructions:
1. Identify all significant clauses (termination, arbitration, liability, payment, confidentiality, etc.)
2. For each clause, provide:
   - clause_type: The type of clause (e.g., "termination", "arbitration", "liability")
   - clause_text: The exact text of the clause
   - start_position: Approximate character position where clause starts (if available)
   - importance: "high", "medium", or "low"

Return your response as a JSON array of clause objects. Format:
[
  {{
    "clause_type": "termination",
    "clause_text": "...",
    "start_position": 0,
    "importance": "high"
  }},
  ...
]

Only return valid JSON, no additional text."""

# Risk Analysis Prompt
RISK_ANALYSIS_PROMPT = """You are a legal risk assessment expert. Analyze the following clause and assess its risk level.

Clause:
{clause_text}

Clause Type: {clause_type}

Instructions:
1. Assess the risk level: "low", "medium", or "high"
2. Provide a brief explanation of the risk
3. Suggest any concerns or red flags

Return your response as JSON:
{{
  "risk_level": "low|medium|high",
  "explanation": "Brief explanation of the risk assessment",
  "concerns": ["List of specific concerns or red flags"]
}}

Only return valid JSON, no additional text."""

# Compliance Checker Prompt
COMPLIANCE_CHECKER_PROMPT = """You are a legal compliance expert specializing in Indian law. Verify if the following clause complies with relevant Indian legal statutes.

Clause to Check:
{clause_text}

Relevant Legal Context (from Indian legal corpus):
{legal_context}

Instructions:
1. Check compliance with Indian laws (Contract Act, Companies Act, etc.)
2. Identify any violations or concerns
3. Cite relevant sections/acts if applicable
4. Provide compliance status: "compliant", "non-compliant", or "requires_review"

Return your response as JSON:
{{
  "compliance_status": "compliant|non-compliant|requires_review",
  "violations": ["List of any violations found"],
  "relevant_acts": ["List of relevant Indian acts"],
  "citations": ["List of specific sections/cases cited"],
  "explanation": "Brief explanation of compliance assessment"
}}

Only return valid JSON, no additional text."""

# Summarization Prompt
SUMMARIZATION_PROMPT = """You are a legal document summarization expert. Create a clear, plain-language summary of the following contract.

Contract Text:
{contract_text}

Relevant Legal Context:
{legal_context}

Instructions:
1. Create a comprehensive but concise summary
2. Include:
   - Key parties and their roles
   - Main obligations and responsibilities
   - Important terms and conditions
   - Risk factors
   - Key dates and deadlines
3. Use plain language (avoid excessive legal jargon)
4. Structure the summary with clear sections

Return your response as a JSON object:
{{
  "summary": "Main summary text",
  "key_parties": ["List of key parties"],
  "main_obligations": ["List of main obligations"],
  "key_terms": ["List of key terms"],
  "risk_factors": ["List of identified risk factors"],
  "important_dates": ["List of important dates/deadlines"]
}}

Only return valid JSON, no additional text."""

# Q&A Prompt
QA_PROMPT = """You are a legal research assistant specializing in Indian law. Answer the following question using the provided legal context.

Question: {question}

Legal Context (from Indian legal corpus):
{legal_context}

Instructions:
1. Answer the question based on the provided legal context
2. Cite specific sources (acts, sections, cases) when relevant
3. If the context doesn't contain enough information, state that clearly
4. Provide a clear, concise answer

Return your response as JSON:
{{
  "answer": "Your answer to the question",
  "sources": [
    {{
      "title": "Source title",
      "section": "Section number if applicable",
      "chunk_id": "chunk identifier"
    }}
  ],
  "confidence": "high|medium|low",
  "notes": "Any additional notes or disclaimers"
}}

Only return valid JSON, no additional text."""

