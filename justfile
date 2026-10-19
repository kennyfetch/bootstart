# Template justfile. /init-project replaces it with the chosen stack pack's justfile.
# Until then, the standard recipes only print a hint, and `selftest` validates every pack.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# List recipes
default:
    @{{ just_executable() }} --list

setup: _not-initialized
dev: _not-initialized
format: _not-initialized
fix: _not-initialized
lint: _not-initialized
typecheck: _not-initialized
test: _not-initialized
check: _not-initialized

# Run setup + check in every stack pack (template maintenance)
selftest:
    {{ just_executable() }} --justfile stacks/python/justfile --working-directory stacks/python setup
    {{ just_executable() }} --justfile stacks/python/justfile --working-directory stacks/python check
    {{ just_executable() }} --justfile stacks/typescript/justfile --working-directory stacks/typescript setup
    {{ just_executable() }} --justfile stacks/typescript/justfile --working-directory stacks/typescript check

[private]
_not-initialized:
    @echo "Template not initialized: run /init-project (or follow .claude/skills/init-project/SKILL.md)."
