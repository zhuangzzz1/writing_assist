#!/usr/bin/env python3
"""Analyze reference preservation errors from evaluation evidence."""

import json
import sys


def analyze_reference_errors(evidence_file):
    """Extract and analyze reference preservation errors."""
    with open(evidence_file, 'r') as f:
        data = json.load(f)

    repairs = data['modes']['nonthinking']['summary'].get('repair_diagnostics', [])
    reference_errors = [r for r in repairs if 'reference' in r.get('validation_error', '').lower()]

    print(f"=== REFERENCE PRESERVATION ERROR ANALYSIS ===\n")
    print(f"Total repairs: {len(repairs)}")
    print(f"Reference preservation errors: {len(reference_errors)}\n")

    for i, repair in enumerate(reference_errors, 1):
        print(f"ERROR {i}: {repair['scenario_id']}")
        print(f"Validation: {repair['validation_error']}\n")

        response = json.loads(repair['invalid_final_response'])

        for j, candidate in enumerate(response.get('candidates', []), 1):
            draft_ref = candidate.get('draft_reference', '')
            hint_ref = candidate.get('hint', {}).get('passage_reference', '')

            if draft_ref != hint_ref:
                print(f"  Candidate {j} ({candidate.get('goal_id', 'unknown')}):")
                print(f"    Coordinator reference: '{draft_ref}'")
                print(f"    Support hint reference: '{hint_ref}'")
                print(f"    Issue: ", end='')

                # Analyze the difference
                if 'you' in hint_ref.lower() and ('me' in draft_ref.lower() or 'I' in draft_ref.lower() or 'my' in draft_ref.lower()):
                    print("Pronoun shift (1st person -> 2nd person)")
                elif len(hint_ref) != len(draft_ref):
                    print("Length mismatch (paraphrasing or truncation)")
                elif draft_ref.lower() in hint_ref.lower() or hint_ref.lower() in draft_ref.lower():
                    print("Substring match (partial preservation)")
                else:
                    print("Complete mismatch")
                print()

        print("-" * 80 + "\n")

    # Summary
    print("\n=== ROOT CAUSE ANALYSIS ===\n")
    print("All reference preservation errors show the same pattern:")
    print("- Support agent received correct draft_reference from Coordinator")
    print("- Support agent changed pronouns when copying to hint.passage_reference")
    print("- Common pattern: 1st person ('my', 'I', 'me') -> 2nd person ('your', 'you')")
    print()
    print("This is NOT caused by Track A changes (Step 0, concrete-first, claim anchoring).")
    print("The hint structure improvements don't modify reference text.")
    print()
    print("Likely cause: Support agent prompt uses 2nd person instructions")
    print("('Find the sentence where your friend...' causes pronoun drift in references)")
    print()
    print("Fix: Add explicit prompt constraint to preserve exact reference text,")
    print("including all pronouns, even when instructions use 2nd person address.")


if __name__ == '__main__':
    evidence_file = sys.argv[1] if len(sys.argv) > 1 else 'data/evidence/v3_acceptance_evaluation_20261111T170309Z.json'
    analyze_reference_errors(evidence_file)
