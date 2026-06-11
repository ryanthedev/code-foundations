#!/bin/bash
set -e

REPO="/Users/r/repos/code-foundations"
SKILLS=(
  "gof-design-patterns"
  "cc-debugging"
  "welc-legacy-code"
)

echo "=== DW-7.1: Validate 3 Skills ==="
for skill in "${SKILLS[@]}"; do
  echo ""
  echo "Validating: $skill"
  python3 << 'PYEOF'
import subprocess
import json
import sys

skill_path = f"/Users/r/repos/code-foundations/skills/{sys.argv[1]}"
result = subprocess.run(
    ["python3", "-m", "claude_mcp.client", "call",
     "mcp__plugin_oberskills_skill-eval__validate_skill",
     "--skill_path", skill_path],
    capture_output=True,
    text=True,
    cwd="/Users/r/repos"
)

if result.returncode != 0:
    print(f"Error: {result.stderr}")
    sys.exit(1)

try:
    output = json.loads(result.stdout)
    print(f"  valid: {output.get('valid', 'N/A')}")
    print(f"  errors: {len(output.get('errors', []))}")
    print(f"  warnings: {len(output.get('warnings', []))}")
    if output.get('errors'):
        for err in output['errors']:
            print(f"    - {err}")
    if output.get('warnings') and len(output.get('warnings', [])) <= 5:
        for warn in output['warnings'][:5]:
            print(f"    - {warn}")
    elif output.get('warnings'):
        print(f"    (showing first 5 of {len(output['warnings'])} warnings)")
except json.JSONDecodeError:
    print(result.stdout)
PYEOF
done
