# eskills — dev tooling
# Run `make` or `make help` to see available targets.

PLUGIN := eskills

.ONESHELL:
.DEFAULT_GOAL := help
.PHONY: help list check lint fmt new dev details tag install update

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-9s\033[0m %s\n",$$1,$$2}'

list: ## List skills and their trigger descriptions
	@for f in skills/*/SKILL.md; do
	  [ -e "$$f" ] || { echo "  (no skills yet)"; break; }
	  n=$$(sed -n 's/^name:[[:space:]]*//p' "$$f" | head -1)
	  d=$$(sed -n 's/^description:[[:space:]]*//p' "$$f" | head -1)
	  printf "  \033[36m%-13s\033[0m %s\n" "$$n" "$$d"
	done

lint: check ## Alias for `check`

check: ## Validate frontmatter, JSON, and design caps (run before pushing)
	@fail=0
	for f in $$(find . -name '*.json' -not -path './.git/*'); do
	  python3 -m json.tool "$$f" >/dev/null 2>&1 || { echo "✗ invalid JSON: $$f"; fail=1; }
	done
	skills=0; bars=0
	for d in skills/*/; do
	  [ -d "$$d" ] || continue
	  dir=$$(basename "$$d"); f="$$d/SKILL.md"; skills=$$((skills+1))
	  case "$$dir" in *-bar) bars=$$((bars+1));; esac
	  [ -f "$$f" ] || { echo "✗ missing SKILL.md in $$dir"; fail=1; continue; }
	  name=$$(sed -n 's/^name:[[:space:]]*//p' "$$f" | head -1)
	  desc=$$(sed -n 's/^description:[[:space:]]*//p' "$$f" | head -1)
	  [ "$$name" = "$$dir" ] || { echo "✗ name '$$name' != dir '$$dir'"; fail=1; }
	  echo "$$name" | grep -qE '^[a-z0-9-]+$$' || { echo "✗ name not kebab-case: $$dir"; fail=1; }
	  echo "$$desc" | grep -q '^Use when' || { echo "✗ description must start with 'Use when': $$dir"; fail=1; }
	  fm=$$(awk 'NR==1&&/^---/{f=1;next} /^---/{if(f)exit} f{print}' "$$f" | wc -c)
	  [ "$$fm" -le 1024 ] || { echo "✗ frontmatter >1024 chars: $$dir ($$fm)"; fail=1; }
	done
	[ "$$skills" -le 12 ] || { echo "✗ >12 skills ($$skills) — cap (raised 10→11 for context-budget, 11→12 for exploit-hunt)"; fail=1; }
	[ "$$bars" -le 4 ]   || { echo "✗ >4 quality lenses ($$bars) — hard cap"; fail=1; }
	if [ "$$fail" = 0 ]; then echo "✓ check passed ($$skills skills, $$bars lenses)"; else exit 1; fi

fmt: ## Format markdown + JSON (fetches prettier via npx on first run)
	npx --yes prettier --prose-wrap preserve --write "**/*.md" "**/*.json"

new: ## Scaffold a skill: make new name=<kebab-name>
	@test -n "$(name)" || { echo "usage: make new name=<kebab-name>"; exit 1; }
	echo "$(name)" | grep -qE '^[a-z0-9-]+$$' || { echo "name must be kebab-case"; exit 1; }
	[ -e "skills/$(name)/SKILL.md" ] && { echo "exists: skills/$(name)/SKILL.md"; exit 1; } || true
	mkdir -p "skills/$(name)"
	printf '%s\n' '---' 'name: $(name)' 'description: Use when ... — triggering conditions only, no process summary.' '---' '' '# $(name)' '' '## Overview' '' 'What is this? Core principle in 1-2 sentences.' '' '## When to use' '' '- ' '' '## Steps' '' '1. ' > "skills/$(name)/SKILL.md"
	echo "created skills/$(name)/SKILL.md"

dev: ## Load the pack at HEAD in a Claude session (dev)
	claude --plugin-dir "$(CURDIR)"

details: ## Show component inventory + token cost of the installed plugin
	claude plugin details $(PLUGIN)

tag: ## Create the {name}--v{version} release tag (validates plugin.json vs marketplace)
	claude plugin tag "$(CURDIR)"

install: ## Add this repo as a marketplace and install the plugin
	claude plugin marketplace add "$(CURDIR)"
	claude plugin install $(PLUGIN)

update: ## Update the installed plugin to latest (restart to apply)
	claude plugin update $(PLUGIN)
