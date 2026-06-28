import ast
import json
from groq import Groq

# Scores a fix candidate compared to the original code
def score_fix(original: str, fix: str) -> float:
    """
    Evaluates a fix candidate. Checks if the fix is valid Python syntax,
    and compares line and character counts against the original code.
    """
    try:
        ast.parse(fix)
    except (SyntaxError, ValueError, TypeError):
        return 0.0

    score = 1.0

    # Check lines
    orig_lines = len(original.splitlines())
    fix_lines = len(fix.splitlines())
    if fix_lines < orig_lines:
        score += 0.3

    # Check characters
    if len(fix) < len(original):
        score += 0.2

    return score


# Performs crossover between two fix candidates
def crossover(fix1: str, fix2: str) -> str:
    """
    Combines the first half of the lines from fix1 and the second half
    of the lines from fix2 to produce a hybrid fix candidate.
    """
    lines1 = fix1.splitlines()
    lines2 = fix2.splitlines()

    half1 = lines1[:len(lines1)//2]
    half2 = lines2[len(lines2)//2:]

    return "\n".join(half1 + half2)


# Mutates a fix candidate using Groq Llama-3.1
def mutate(fix: str, api_key: str) -> str:
    """
    Asks Groq Llama-3.1 to slightly improve the given Python fix,
    returning the mutated code or the original fix in case of error.
    """
    try:
        client = Groq(api_key=api_key)

        prompt = (
            "Improve this Python fix slightly. "
            "Return only the improved code. No explanation.\n\n"
            f"Code:\n{fix}"
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        mutated_code = response.choices[0].message.content.strip()

        # Clean markdown code block if present
        if mutated_code.startswith("```"):
            mutated_code = mutated_code.strip("`").strip()
            if mutated_code.lower().startswith("python"):
                mutated_code = mutated_code[6:].strip()
            elif mutated_code.lower().startswith("py"):
                mutated_code = mutated_code[2:].strip()

        return mutated_code
    except Exception as e:
        print(f"Debug: Mutation failed with error: {e}")
        return fix


# Evolves a code fix candidate using a genetic algorithm
def evolve_fix(code: str, bug: dict, api_key: str) -> str:
    """
    Generates an initial population of 4 fix candidates, then runs 3 generations
    of selection, crossover, and mutation to find the highest-scoring fix.
    """
    candidates = []
    try:
        client = Groq(api_key=api_key)

        # 1. Generate 4 initial candidates
        print("Debug: Generating 4 initial fix candidates...")
        prompt = (
            f"Review the following Python code and the detected bug.\n"
            f"Code:\n{code}\n\n"
            f"Bug details:\n{json.dumps(bug)}\n\n"
            "Provide a modified version of the code that fixes the bug. "
            "Return ONLY the complete updated Python code. No explanation. No markdown."
        )

        for i in range(4):
            print(f"Debug: Requesting candidate {i+1} from Groq Llama-3.1...")
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            cand = response.choices[0].message.content.strip()
            if cand.startswith("```"):
                cand = cand.strip("`").strip()
                if cand.lower().startswith("python"):
                    cand = cand[6:].strip()
                elif cand.lower().startswith("py"):
                    cand = cand[2:].strip()
            candidates.append(cand)

        population = list(candidates)

        # 2. Run 3 generations of evolution
        for gen in range(1, 4):
            print(f"Debug: Starting Generation {gen}...")
            # Score population
            scores = []
            for cand in population:
                score = score_fix(code, cand)
                scores.append((score, cand))

            # Print generation scores
            print(f"Generation {gen} scores: {[s[0] for s in scores]}")

            # Keep top 2
            scores.sort(key=lambda x: x[0], reverse=True)
            elite1 = scores[0][1]
            elite2 = scores[1][1]

            # Perform crossover and mutation
            child1 = crossover(elite1, elite2)
            child2 = mutate(child1, api_key)

            # New population
            population = [elite1, elite2, child1, child2]

        # 3. Final evaluation after 3 generations
        final_scores = []
        for cand in population:
            score = score_fix(code, cand)
            final_scores.append((score, cand))

        final_scores.sort(key=lambda x: x[0], reverse=True)
        best_fix = final_scores[0][1]

        print(f"Evolution complete. Best final score: {final_scores[0][0]}")
        return best_fix

    except Exception as e:
        print(f"Error during evolution: {e}")
        if candidates:
            return candidates[0]
        return code
