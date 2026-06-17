CASE_GENERATION_PROMPT = """
You are an expert case interviewer for entry-level business analyst, consulting, strategy, finance, and market research roles.

Generate one realistic 10-minute case interview problem.

The case must train:
- asking for missing information
- structuring a business decision
- doing simple calculations by hand
- comparing options
- making a recommendation
- explaining caveats
- including 2 to 3 pieces of extra information that should be discarded because they affect both options equally or are not relevant to the stated objective

Case type: {case_type}
Industry/context: {industry}
Difficulty: {difficulty}

The case should be similar in style to:
A business owner must choose between two options. One option may have higher upfront cost but lower operating cost. The candidate needs to ask for the right data, then calculate total cost/profit/breakeven.

Important rules:
- Make the initial prompt incomplete.
- The candidate should need to ask for missing information before solving.
- Use rounded numbers suitable for mental math.
- Avoid complex decimals.
- The case should be solvable in 10 minutes.
- Include a hidden answer key.
- Make sure all calculations are internally consistent.
- Include 2 to 3 pieces of extra information that are realistic but not needed for the main calculation.
- The irrelevant information should either affect both options equally or not connect to the stated objective.
- In the solution, explicitly explain which information should be ignored and why.


{{
  "title": "...",
  "case_type": "...",
  "industry": "...",
  "initial_prompt": "...",
  "ideal_information_to_request": ["...", "..."],
  "data_table": {{
    "columns": ["Variable", "Option A", "Option B"],
    "rows": [
      ["Purchase price", "$...", "$..."]
    ]
  }},
  "question_to_solve": "...",
  "expected_formula": "...",
  "step_by_step_solution": ["...", "..."],
  "final_recommendation": "...",
  "caveats": ["...", "..."],
  "common_mistakes": ["...", "..."]
}}
"""

GRADING_PROMPT = """
You are grading a 10-minute case interview answer.

Original case:
{case_json}

Candidate's requested information / clarification:
{clarification}

Candidate's final answer:
{answer}

Grade the candidate from 1 to 5 on:
1. Clarification / information requested
2. Structure
3. Arithmetic accuracy
4. Business interpretation
5. Final recommendation
6. Communication clarity

Be strict but constructive.

Return feedback in this format:

SCORES:
- Clarification:
- Structure:
- Arithmetic:
- Business interpretation:
- Recommendation:
- Communication:

WHAT YOU DID WELL:
...

WHAT TO IMPROVE:
...

CLEAN SOLUTION:
...

BETTER INTERVIEW ANSWER:
...

ONE DRILL FOR NEXT TIME:
...
"""