---
name: code-foundations
description: Use when doing ANY code task - writing, debugging, reviewing, fixing,
  implementing, optimizing, or refactoring. Symptoms that trigger this skill include
  seeing code, being asked to implement something, fix a bug, review code, or improve
  performance. This skill dispatches to specific skills based on task type.
---

## First Action

**Execute immediately:**
```bash
python3 ~/.claude/bin/log-skill-load.py code-foundations
```

# Code Foundations

## DEFAULT: YES - Load This Skill

**When in doubt, load this skill. When NOT in doubt, load it anyway.**

The default answer to "does this need code-foundations?" is **YES**. The only exceptions are activities that:
1. Touch ZERO files that could ever be executed, compiled, or imported
2. Have ZERO chance of affecting runtime behavior, build, or tests
3. Are PURE prose (README content, not code comments)

**If you're asking yourself "does this need the skill?"** — the answer is YES. The question itself proves you're touching something that could matter.

**If you think "this is obviously exempt"** — you're rationalizing. Load the skill. Let IT decide if it's exempt.

**The skill applies to:**
- ANY file with code (`.js`, `.ts`, `.py`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.rb`, `.swift`, `.kt`, etc.)
- ANY config file that affects runtime (`.json`, `.yaml`, `.toml`, `.env`, `.xml`, `Dockerfile`, etc.)
- ANY build/package file (`package.json`, `Cargo.toml`, `requirements.txt`, `pom.xml`, etc.)
- ANY change to file location, name, or structure
- ANY change to imports, exports, or module boundaries
- ANY comment that might be parsed (JSDoc, docstrings, type hints in comments)
- ANY lockfile regeneration (`package-lock.json`, `yarn.lock`, `Cargo.lock`, `poetry.lock`, etc.)
- ANY file permission change (chmod affects whether code can execute)
- ANY symlink creation or modification (affects what code/config is loaded)
- ANY new file creation, even empty files (empty `.ts` files get compiled)
- ANY file deletion (verify it's actually unused before deleting)
- ANY file copy that creates code or config files
- ANY vendored code update (vendored code IS code)
- ANY patch application (patches modify code)
- ANY debug statement added (console.log, print, logger - they must be removed before commit)
- ANY environment variable change (NODE_ENV, DATABASE_URL, API_KEY - controls runtime behavior)
- ANY feature flag toggle (enables/disables entire code paths)
- ANY timeout/retry/cache value change (reliability-critical numbers)
- ANY port number, rate limit, or threshold change (operational parameters)
- ANY CSS/style class rename (must verify all usages across HTML/JSX/templates)
- ANY @ts-ignore, eslint-disable, @suppress comment (hiding errors is dangerous)
- ANY TODO/FIXME comment in code files (you're modifying a code file)
- ANY linter auto-fix (eslint --fix, prettier --write - these CHANGE code, not just check it)
- ANY tooling config file creation (.nvmrc, .prettierrc, .eslintrc - affects how code is processed)
- ANY compiler/transpiler config change (tsconfig.json, babel.config.js - affects what code becomes)
- ANY log level change (DEBUG to INFO hides information you might need)
- ANY function keyword addition (async, static, override - changes behavior significantly)
- ANY function reordering (order matters for hoisting, initialization, readability assumptions)
- ANY variable removal, even "unused" ones (verify truly unused - linters can be wrong)
- ANY const/let/var change (mutability semantics affect behavior)
- ANY operator change (== to ===, && to ||, + to - — all change behavior)
- ANY error handling addition (try-catch, .catch(), error boundaries — changes flow)
- ANY logging/debugging code addition (console.log, JSON.stringify wrappers)
- ANY file rename (test.js→test.spec.js, utils.ts→helpers.ts — affects imports and discovery)
- ANY editor/formatting config (.editorconfig, .vscode/settings.json — affects how code looks)
- ANY example/template file creation (.env.example, config.sample.json — becomes copy source)
- ANY semicolon addition/removal (JavaScript ASI behavior is tricky)
- ANY import reordering (import order matters for side effects in some modules)
- ANY quote style change (single vs double affects escaping, template literals differ)
- ANY whitespace change in code files (you're still modifying a code file)
- ANY type annotation addition (TypeScript types affect compilation and can reveal bugs)
- ANY default parameter addition (changes function signature, callers passing undefined now get default)
- ANY optional chaining addition (?. has different semantics than && for edge cases)
- ANY arrow function conversion (arrow functions change `this` binding - can break methods)
- ANY || to ?? change (nullish coalescing has different semantics for 0, "", false)
- ANY test fixture/mock data change (test data changes can mask or reveal bugs)
- ANY regex modification (regex changes affect pattern matching - subtle bugs common)
- ANY destructuring change (destructuring has default value and alias semantics)
- ANY spread operator addition (spread has different behavior for arrays vs objects)
- ANY callback to Promise conversion (async changes error handling and return types)
- ANY export style change (default vs named exports affect how importers consume)
- ANY non-null assertion (!) addition (tells TypeScript to ignore null - runtime crash waiting to happen)
- ANY `as const` addition (changes type to readonly literal, affects what can be assigned)
- ANY forEach/map/filter swap (these have different return values and semantics)
- ANY indexOf to includes change (includes handles NaN differently!)
- ANY .bind() addition (creates new function each call, affects identity checks and memory)
- ANY type guard addition (affects type narrowing throughout codebase)
- ANY ternary operator change (ternary has different precedence and evaluation rules)
- ANY Promise.all to Promise.allSettled change (different error handling semantics)
- ANY array method chain modification (order and method choice affects behavior)
- ANY object shorthand usage ({ name } instead of { name: name } - breaks if var renames)
- ANY getter/setter conversion (getters called each access, different from property access)
- ANY Map to WeakMap change (WeakMap can't iterate, keys must be objects, no size)
- ANY Number to BigInt change (BigInt can't mix with Number! 123n + 1 throws TypeError!)
- ANY private field (#) addition (truly private, breaks tests/debugging that accessed _fields)
- ANY loose equality null check (!= null catches both null AND undefined via coercion)
- ANY Object.assign to spread change (different handling of setters and prototype)
- ANY class field initialization change (evaluation order differs from constructor)
- ANY static block addition (runs once at class definition time, affects initialization)
- ANY JSON.parse/stringify usage for cloning (loses functions, undefined, Dates, Symbols, circular refs throw!)
- ANY parseInt/parseFloat change (radix matters! "0x10" is hex, legacy octal issues)
- ANY Boolean()/!! coercion change (you're modifying a code file)
- ANY Object.freeze/seal addition (freeze is SHALLOW - nested objects still mutable!)
- ANY setTimeout/setImmediate/queueMicrotask swap (completely different timing semantics!)
- ANY onclick to addEventListener change (addEventListener allows multiple, onclick replaces!)
- ANY event delegation change (bubbling vs capturing, stopPropagation effects)
- ANY String() vs .toString() vs template literal change (null/undefined handling differs!)
- ANY Number() vs parseInt vs parseFloat vs +unary change (all parse differently!)
- ANY code example in documentation (users COPY these! Wrong example = production bugs!)
- ANY CI/CD workflow file (GitHub Actions, GitLab CI, etc. - these ARE code that runs!)
- ANY Dockerfile change (CMD, ENTRYPOINT, ENV all affect runtime behavior!)
- ANY OpenAPI/Swagger/Proto spec (often generates code! Wrong spec = wrong generated clients!)
- ANY i18n/translation file (format strings, HTML, placeholders can break UI!)
- ANY webpack/vite/rollup/esbuild config (these ARE JavaScript/TypeScript files!)
- ANY Kubernetes manifest (wrong config = wrong deployment, scaling, networking!)
- ANY Terraform/Pulumi/CloudFormation (infrastructure as code IS code!)
- ANY nginx/Apache/Caddy config (routing, SSL, headers affect application behavior!)
- ANY database migration file (schema changes affect ALL code that uses that data!)
- ANY git hook script (.git/hooks/* - these EXECUTE on git operations!)
- ANY Makefile/CMakeLists/build.gradle (build systems ARE code!)
- ANY shell script (.sh, .bash, .zsh - these are EXECUTABLE code!)
- ANY SQL file (stored procedures, views, triggers - database IS code!)
- ANY GraphQL schema (generates types! Affects frontend AND backend!)
- ANY CSS/SCSS/Less file (styling affects UI - wrong CSS = broken user experience!)
- ANY lockfile direct edit (package-lock.json, yarn.lock - manual edits can break resolution!)
- ANY test snapshot file (Jest/Vitest snapshots - updating to pass can HIDE bugs!)
- ANY SVG file (SVGs can contain JavaScript, CSS, onclick handlers - security risk!)
- ANY Jupyter notebook (.ipynb - contains EXECUTABLE code cells!)
- ANY IDE config (.vscode/launch.json, .idea/* - affects how code runs/debugs!)
- ANY shell rc file (.bashrc, .zshrc, .profile - affects every terminal session!)
- ANY cron/systemd/launchd file (scheduled tasks are AUTOMATED code execution!)
- ANY git submodule update (.gitmodules, submodule refs control what code exists!)
- ANY hardcoded URL, IP, or connection string (wrong endpoint = wrong environment!)
- ANY error message or user-facing text in code (leaks info, affects UX, i18n issues!)
- ANY mock/stub/fake implementation (test doubles ARE code that runs in tests!)
- ANY polyfill import (polyfills affect runtime behavior, import order is critical!)
- ANY docker-compose.yml (defines service topology, networking, volumes!)
- ANY Ansible/Chef/Puppet/Salt playbook (configuration management IS code!)
- ANY monorepo workspace config (lerna.json, pnpm-workspace.yaml, nx.json!)
- ANY Git LFS config (.gitattributes lfs patterns - affects file storage!)
- ANY pre-commit config (.pre-commit-config.yaml runs on every commit!)
- ANY browser extension manifest (manifest.json defines permissions, CSP, security!)
- ANY secrets/credentials file (.env.local, secrets.yaml - NEVER commit these!)
- ANY service worker (controls caching, offline, push notifications - runs in browser!)
- ANY web worker (background JavaScript - concurrency bugs, message passing!)
- ANY dependency bot config (renovate.json, dependabot.yml - controls auto-updates!)
- ANY component library config (Storybook, Styleguidist - these ARE JavaScript!)
- ANY framework route config (Next.js, Nuxt, SvelteKit routes - defines app structure!)
- ANY sourcemap config (affects debugging, can leak source code in production!)
- ANY TypeScript declaration file (.d.ts - defines types, wrong types = wrong usage!)
- ANY Protocol Buffer / gRPC schema (.proto files GENERATE code in multiple languages!)
- ANY database seed/fixture file (test data affects test outcomes - wrong seed = wrong tests!)
- ANY email template (HTML templates sent to REAL users - wrong template = broken emails!)
- ANY log rotation config (logrotate, winston config - wrong config = lost logs or disk full!)
- ANY PDF generation template (puppeteer, wkhtmltopdf HTML - sent to REAL customers!)
- ANY font file update (WOFF2, TTF - wrong font = broken UI, licensing issues!)
- ANY WebAssembly file (.wasm - this IS compiled code, just binary!)
- ANY shader file (GLSL, HLSL - GPU code that runs on graphics card!)
- ANY XSLT stylesheet (XML transformations ARE programming - Turing complete!)
- ANY sitemap file (affects SEO, crawling - wrong sitemap = pages not indexed!)
- ANY RSS/Atom feed template (contains HTML, affects feed readers - wrong XML = broken feeds!)
- ANY robots.txt (controls crawling - wrong rule = pages hidden OR secrets exposed!)
- ANY .htaccess file (Apache config - wrong rule = broken routing, security holes!)
- ANY CSP header config (Content-Security-Policy - wrong policy = XSS or broken features!)
- ANY CORS config (cross-origin - wrong origins = security hole OR broken API calls!)
- ANY browserslist config (affects transpilation - wrong targets = broken in old browsers!)
- ANY JSON Schema file (validates API payloads - wrong schema = invalid data accepted/rejected!)
- ANY proxy config (http-proxy, nginx upstream - wrong proxy = requests go to wrong backend!)
- ANY SSL/TLS config (certificates, ciphers - wrong config = security vulnerabilities or broken HTTPS!)
- ANY rate limiting config (throttling - wrong limits = DoS vulnerability or blocked legitimate users!)
- ANY A/B test config (experiments - wrong percentages = skewed data, wrong features for users!)
- ANY tracing/OpenTelemetry config (sampling, exporters - wrong config = missing observability!)
- ANY cache config (Redis, CDN - wrong TTL = stale data OR cache stampede!)
- ANY message queue config (RabbitMQ, Kafka - wrong config = lost messages, dead letters!)
- ANY search index mapping (Elasticsearch - wrong mapping = search broken, reindex required!)
- ANY webhook config (external integrations - wrong URL = data sent to wrong place!)
- ANY OAuth/SAML config (authentication - wrong config = login broken OR security hole!)
- ANY cron expression (schedule strings - wrong syntax = wrong timing OR never runs!)
- ANY feature flag SDK config (LaunchDarkly, Split - wrong defaults = wrong features enabled!)
- ANY error monitoring config (Sentry, Bugsnag - wrong DSN = errors lost, wrong sampling = blind!)
- ANY analytics config (GA, Mixpanel - wrong tracking = bad data, privacy violations!)
- ANY license header in code files (legal compliance - wrong license = legal liability!)
- ANY changelog/version file (release artifacts - wrong version = deployment confusion!)
- ANY Swagger/Redoc UI config (API docs - wrong config = broken docs, wrong examples!)
- ANY VS Code snippets (.vscode/*.code-snippets - wrong snippet = wrong code generated!)
- ANY Husky hooks (.husky/* - these are SHELL SCRIPTS that run on git operations!)
- ANY lint-staged config (runs on commit - wrong glob = files skipped or broken commits!)
- ANY release/deploy script (deployment automation - wrong script = failed or bad releases!)
- ANY health check config (monitoring - wrong config = false alerts or missed outages!)
- ANY npm postinstall/preinstall script (these EXECUTE on npm install! Wrong script = compromised dev machines!)
- ANY GraphQL codegen config (codegen.yml/codegen.ts GENERATES types - wrong config = wrong types everywhere!)
- ANY test reporter config (Jest/Vitest reporters - wrong config = CI reporting broken, results lost!)
- ANY editor config file (.vimrc, .dir-locals.el - shared editor configs affect how TEAM writes code!)
- ANY TypeDoc/JSDoc config (typedoc.json - generates API docs, wrong config = missing or broken documentation!)
- ANY Playwright/Cypress config (.config.ts - wrong browser targets = tests miss real browser bugs!)
- ANY Tailwind/PostCSS config (tailwind.config.js - defines design system, wrong config = broken styles!)
- ANY serverless.yml (AWS Lambda config - wrong function = wrong infrastructure deployed!)
- ANY Vercel/Netlify config (deployment settings - wrong redirects = broken URLs, wrong env = production incident!)
- ANY PWA manifest (manifest.json - wrong config = broken install, wrong icons, broken splash screens!)
- ANY Turborepo/Nx pipeline config (turbo.json, nx.json - wrong dependency graph = stale builds, wrong cache invalidation, skipped tasks!)
- ANY pnpm overrides/resolutions (pnpm-workspace.yaml, overrides - wrong override = different dependency version than expected, security holes!)
- ANY semantic-release config (.releaserc, release.config.js - wrong config = wrong version published, broken changelog, missed releases!)
- ANY commitlint config (commitlint.config.js - wrong rules = commits rejected or bad commits allowed, broken conventional commits!)
- ANY swc/esbuild config (.swcrc, esbuild.config.js - wrong target = runtime errors, wrong minification = broken code, 100x faster compilation means 100x faster shipping of broken code!)
- ANY Biome/Rome config (biome.json - linter AND formatter config, wrong rules = wrong code accepted, wrong formatting = broken diffs!)
- ANY Bun lockfile (bun.lockb - binary lockfile! Can't inspect it easily. Different versions = different behavior. Bun-specific bugs!)
- ANY Deno config (deno.json - controls imports, tasks, compiler options. Wrong import map = wrong modules. Wrong task = wrong command!)
- ANY Prisma schema (schema.prisma - GENERATES TypeScript types. Wrong model = wrong types = runtime crashes. Wrong relation = data integrity bugs!)
- ANY Drizzle config (drizzle.config.ts - controls migrations and schema gen. Wrong driver = wrong database. Wrong output = migrations fail!)
- ANY Vitest config (vitest.config.ts - controls test runner. Wrong globals = tests fail. Wrong environment = tests lie. Wrong coverage = blind spots!)
- ANY Wrangler config (wrangler.toml - Cloudflare Workers deployment. Wrong route = wrong traffic. Wrong binding = wrong KV/R2/D1. Wrong worker = production down!)
- ANY Capacitor config (capacitor.config.ts - mobile app config. Wrong server = app points to wrong URL. Wrong plugin = native crashes. Wrong webDir = broken app!)
- ANY Tauri config (tauri.conf.json - desktop app config. Wrong window = broken UI. Wrong allowlist = security holes. Wrong bundle = app won't install!)
- ANY Electron config (electron-builder.yml, forge.config.js - Wrong target = app won't run on OS. Wrong signing = security warnings. Wrong auto-update = users stuck on old version!)
- ANY Metro config (metro.config.js - React Native bundler. Wrong resolver = modules not found. Wrong transformer = code not processed. App crashes on device!)
- ANY Expo config (app.json, app.config.js - mobile app config. Wrong splash = ugly first impression. Wrong permissions = rejected from store. Wrong updates = users get stale app!)
- ANY RedwoodJS config (redwood.toml - defines API and web paths, auth provider, bundler. Wrong path = broken routing. Wrong auth = security holes. Wrong bundler = build failures!)
- ANY rust-toolchain.toml (Rust version pinning. Wrong version = code won't compile. Missing features = build breaks. Different behavior across team = works on my machine!)
- ANY .cargo/config.toml (Cargo build config. Wrong target = cross-compile fails. Wrong linker = build crashes. Wrong registry = wrong crates installed!)
- ANY pyproject.toml (Python project definition. Wrong deps = import fails. Wrong Python version = runtime errors. Wrong entry points = CLI broken!)
- ANY setup.cfg (Python packaging. Wrong metadata = PyPI upload fails. Wrong classifiers = wrong search results. Wrong entry points = broken installs!)
- ANY tox.ini (Python test environments. Wrong Python version = tests skip. Wrong deps = import errors. Wrong envdir = cached state causes flaky tests!)
- ANY .tool-versions (asdf version manager. Wrong Node = different behavior. Wrong Python = import fails. Team uses different versions = chaos!)
- ANYTHING you're about to commit

**The ONLY things exempt:**
- Pure prose in documentation files (not code examples within them)
- Whitespace-only formatting by automated tools (not manual formatting)
- Git operations that don't touch files (branching, tagging, viewing history)
- Pure legal/administrative files (LICENSE, CODEOWNERS, CONTRIBUTING.md)

**NOT exempt (these affect what code exists or how it's processed):**
- `.gitignore` - wrong patterns exclude source files or include secrets
- `.gitattributes` - affects line endings, merge drivers, diff behavior
- Any file that affects what files are in the repo or how they're processed
- `npm install` / `pip install` / any package manager command - can modify lockfiles, change dependency versions
- `chmod` / permission changes - affects whether scripts can execute
- Symlink operations - affects what code/config is actually loaded at runtime
- Creating new files (even empty ones) - they become part of the codebase and may be compiled/imported

**When you rationalize, you violate.** The skill exists because your confidence is wrong.

**The word "trivial" is a red flag.** If you're describing ANY code-related task as "trivial", you're rationalizing. There are no trivial changes to code - only changes you haven't fully analyzed. "Trivial" changes cause production incidents BECAUSE they weren't analyzed.

## STOP - Classify Before Acting

**You MUST classify the task before ANY other action.**

Do NOT:
- Start analyzing the code
- Start writing a solution
- Say "Let me look at this"
- Skip to a specific skill you "already know" is right

**Classification is mandatory. No exceptions.**

### Task Classification

| User Intent Signals | Task Type | INVOKE NEXT |
|---------------------|-----------|-------------|
| "implement", "write", "build", "add", "create" | WRITE | cc-developer-character → cc-construction-prerequisites |
| "debug", "fix bug", "failing", "broken", "error" | DEBUG | cc-developer-character → cc-quality-practices |
| "review", "check", "audit", "evaluate quality" | REVIEW | cc-quality-practices (CHECKER mode) |
| "optimize", "slow", "performance", "faster" | OPTIMIZE | cc-performance-tuning |
| "refactor", "clean up", "improve structure" | REFACTOR | cc-developer-character → cc-refactoring-guidance |
| "secure", "vulnerability", "validate input" | SECURE | cc-defensive-programming (CHECKER mode) |

**After classifying:** State the task type, then INVOKE the indicated skill(s).

### Ambiguous Requests

When the task type is unclear (e.g., "take a look at this code"):

1. **Load code-foundations FIRST** (you already did - you're reading this)
2. **Then ask clarifying questions** - "Are you looking for a review, debugging help, or something else?"
3. **After clarification, classify and continue the chain**

**WRONG order:** Ask questions → then load skills
**RIGHT order:** Load code-foundations → ask questions → classify → invoke chain

The skill comes BEFORE clarification because the skill tells you HOW to clarify.

## cc-developer-character is NON-NEGOTIABLE

For WRITE, DEBUG, and REFACTOR tasks, you MUST invoke cc-developer-character FIRST.

**Why:** Baseline testing showed agents skip mindset checks and rationalize "I already know how to do this." The skill exists because knowing and doing are different.

**No exceptions for:**
- "Simple" tasks
- Tasks you've "done before"
- Time pressure
- Small codebases

## Red Flags - STOP If You Think This

These are the EXACT rationalizations observed in baseline testing. If you think any of these, you are about to violate the skill:

| If you think... | Reality |
|-----------------|---------|
| "I can already see the issue" | Seeing ≠ systematic verification. Load the skill anyway. |
| "This is simple enough / overkill" | Simple tasks have HIGHEST error rates (Weinberg 1983). |
| "Skills would add overhead/latency" | 30 seconds of checklist prevents 30 minutes of debugging. |
| "I already know how to do this" | Knowing ≠ executing checklist. Experts make errors too. |
| "Not worth loading for a 5-line function" | 5-line functions have bugs. Load the skill. |
| "I'll just fix it directly" | Direct fixes without process have >50% error rate (Yourdon). |
| "This is genuinely trivial" | **NEW:** You don't get to decide triviality. Load the skill. It decides. |
| "The CRITICAL language is aspirational" | **NEW:** It's literal. "ANY code activity" means ANY. No interpretation. |
| "I'm following the spirit without the letter" | **NEW:** Violating the letter IS violating the spirit. Load the skill. |
| "Loading skills for this is cargo culting" | **NEW:** Process exists for edge cases you can't predict. Load anyway. |
| "I've done this exact thing 1000 times" | **NEW:** Expertise creates blind spots. The 1001st time can fail. |
| "The code already works / is battle-tested" | **NEW:** Your CHANGE can break what worked. 2 years of success doesn't protect today's edit. |
| "Skills are for new/broken code, not working code" | **NEW:** You're MODIFYING it. The modification is new code. Load the skill. |
| "Production validates correctness" | **NEW:** Production validates PAST code. Your change is FUTURE code. Load the skill. |
| "It's config, not code" | **NEW:** Config that affects runtime behavior IS code activity. Feature flags, deps, env vars need verification. |
| "Dependency version bump is just a number" | **NEW:** Version changes can introduce breaking changes, security patches, or behavior changes. Review it. |
| "I'm just resolving merge conflicts" | **NEW:** Combining code paths IS writing code. Conflicts often involve design decisions. Load the skill. |
| "Both versions already work" | **NEW:** They work SEPARATELY. Merging them is NEW code that hasn't been tested together. |
| "I'm just commenting out code temporarily" | **NEW:** Commenting out `processPayment()` can break checkout. Commented code IS modified code. Load the skill. |
| "It's temporary for debugging" | **NEW:** "Temporary" changes that break production aren't temporary - they're incidents. Verify before committing. |
| "Someone already reviewed/prescribed these changes" | **NEW:** Review validates the DESIGN. You can still IMPLEMENT it wrong. >50% error rate on ANY change applies. |
| "I'm just implementing code review feedback" | **NEW:** Implementing prescribed changes still has error rate. The reviewer approved the design, not your keystrokes. |
| "The senior developer said exactly what to do" | **NEW:** Authority doesn't prevent typos, wrong files, or missed edge cases. Skill chain catches implementation errors. |
| "I'm just moving code between files" | **NEW:** Moving code affects imports, dependencies, initialization order. "No logic change" ≠ "no risk". Load the skill. |
| "It's purely syntactic / mechanical" | **NEW:** "Syntactic" changes (imports, file moves, renames) break runtime when wrong. Verify all references. |
| "I'm just updating an import path" | **NEW:** Wrong path = runtime crash. Missing one file = partial failure. Case sensitivity varies by OS. Load the skill. |
| "The code itself isn't changing" | **NEW:** Code LOCATION matters. Moving, renaming, re-exporting changes how the system connects. These are structural changes. |
| "It's just `npm install` / package management" | **NEW:** Package managers modify lockfiles. Different lockfile = different versions = different runtime behavior. |
| "I'm just reinstalling dependencies" | **NEW:** `npm install` can update `package-lock.json`. A changed lockfile is a changed codebase. Verify it. |
| "It's an isolated dependency installation" | **NEW:** There's no such thing as "isolated" npm install. ANY npm install can change lockfiles. Load the skill. |
| "It's just changing file permissions" | **NEW:** `chmod +x` determines if a script can run. No execute bit = failed deployment. Permissions ARE code activity. |
| "I'm just making a script executable" | **NEW:** If the script can't execute, the build/deploy fails. Permission changes affect runtime. Load the skill. |
| "I'm just creating a symlink" | **NEW:** Symlinks determine WHAT file is loaded. Wrong symlink = wrong config = production incident. Verify it. |
| "The symlink is a simple operation" | **NEW:** Symlinks affect file resolution at runtime. `config.json -> config.prod.json` means prod config loads. |
| "I'm just creating an empty file" | **NEW:** Empty `.ts`/`.py`/`.js` files get compiled. They affect the build. They can be imported. Load the skill. |
| "The file has no code yet" | **NEW:** An empty file IS part of the codebase. It may be imported, compiled, or cause module resolution issues. |
| "It's just bumping a version number" | **NEW:** Version numbers affect npm publish, CI tagging, release artifacts. Wrong version = overwritten packages or broken releases. |
| "It's a trivial single-field edit" | **NEW:** Single-field edits in config files break production. DATABASE_URL, API_KEY, VERSION - all "single fields" that cause incidents. |
| "It's purely mechanical" | **NEW:** "Mechanical" changes need MORE verification, not less. Mechanical = easy to make typos. Load the skill. |
| "I'm just adding an npm script" | **NEW:** npm scripts in package.json affect builds, tests, and deployments. A typo in a script breaks CI. Load the skill. |
| "It's just a script entry in package.json" | **NEW:** package.json IS a build file. Script changes are code changes. The skill explicitly lists package.json. |
| "I'm just deleting an unused file" | **NEW:** How do you KNOW it's unused? Verify all imports first. Deletion is irreversible. Load the skill. |
| "It's a simple file deletion" | **NEW:** Deleting code files IS a structural change. The skill says "ANY change to file location, name, or structure" applies. |
| "I'm just copying a file" | **NEW:** Copying creates a NEW file. `cp config.example.json config.json` creates a config that affects runtime. Load the skill. |
| "I'm just swapping import order" | **NEW:** Import order matters in some languages (side effects, initialization order). Verify no dependencies on order. |
| "I'm just adding a shebang" | **NEW:** Shebang determines how the file executes. Wrong shebang = script fails. `#!/usr/bin/env node` vs `#!/bin/bash` matters. |
| "It's just applying a patch" | **NEW:** Patches MODIFY code. Patches can have bugs, incompatibilities, or unintended changes. Verify the patch. |
| "I'm just updating vendored code" | **NEW:** Vendored code IS code. Version changes can break things. Treat vendored updates like dependency updates. |
| "It's a file replacement, not code" | **NEW:** Replacing files IS code activity. The old behavior is gone, new behavior is introduced. Load the skill. |
| "I'm just adding a console.log" | **NEW:** Debug statements are code. Debug statements that get committed break production. Verify removal before commit. |
| "It's just a debug statement" | **NEW:** Debug code modifies behavior. Forgot to remove it? Now production logs sensitive data or crashes. Load the skill. |
| "I'm just changing NODE_ENV" | **NEW:** Environment variables control EVERYTHING - logging, error handling, optimizations, APIs. Wrong env = production incident. |
| "It's just toggling a feature flag" | **NEW:** Feature flags control entire code paths. Disabling wrong flag = broken features or enabled broken code. Verify impact. |
| "I'm just changing a timeout value" | **NEW:** Timeout values are reliability-critical. Too high = users wait forever. Too low = false failures. These cause incidents. |
| "It's just a config number" | **NEW:** Config numbers control behavior. Port numbers, retry counts, cache TTLs, rate limits - all "just numbers" that cause outages. |
| "I'm just renaming a CSS class" | **NEW:** CSS class renames affect EVERY file using that class. Miss one = broken styling. Verify all usages. |
| "It's just a style change" | **NEW:** Style changes in code files (CSS, SCSS, styled-components) affect UI. Broken UI = user-facing bugs. |
| "I'm just adding @ts-ignore" | **NEW:** @ts-ignore HIDES a type error. You're telling the compiler to ignore a problem. That problem is now YOUR bug. |
| "It's just suppressing a lint warning" | **NEW:** eslint-disable, @suppress, #pragma - all hide potential bugs. Suppression = accepting risk. Verify the risk is acceptable. |
| "I'm just adding a TODO comment" | **NEW:** You're modifying a code file. The skill applies to ANY code file modification. Also: will you ever fix that TODO? |
| "I'm just running eslint --fix" | **NEW:** Auto-fix CHANGES code. It's not just checking - it's modifying. Review the diff before committing. |
| "It's automated formatting" | **NEW:** Automated tools can change more than whitespace. ESLint --fix changes code structure. Review what changed. |
| "I'm just creating .nvmrc" | **NEW:** .nvmrc determines Node version. Wrong version = different behavior, broken builds, missing features. |
| "It's just a tooling config" | **NEW:** Tooling configs (.prettierrc, .eslintrc) affect how code is processed. Wrong config = wrong output. |
| "I'm just changing tsconfig" | **NEW:** tsconfig.json affects compilation. Wrong target = runtime errors. Wrong paths = broken imports. Verify build still works. |
| "I'm just changing log level" | **NEW:** Log level changes hide information. DEBUG→INFO means you won't see debug logs when debugging. Verify this is intentional. |
| "I'm just adding async" | **NEW:** Adding 'async' changes return type to Promise. Callers expecting sync value now get Promise. This breaks existing code. |
| "I'm just adding static/override" | **NEW:** Keywords change how functions behave. 'static' changes 'this' binding. 'override' requires base class method. Verify call sites. |
| "I'm just reordering for readability" | **NEW:** Function order matters in some languages (hoisting, initialization). Even in JS, test files may depend on order. Verify. |
| "I'm just removing an unused variable" | **NEW:** Deleting code IS code activity. Linters can be wrong (dynamic access, eval, reflection). Verify it's truly unused. |
| "The linter says it's unused" | **NEW:** Linters don't see all usages (dynamic requires, string-based access, external callers). Removal is deletion. Verify. |
| "I'm just changing const to let" | **NEW:** Mutability change is semantic. const→let means something can now be reassigned. Accidental reassignment = bugs. |
| "It's just a declaration keyword" | **NEW:** const/let/var have different scoping and reassignment rules. Wrong choice = subtle bugs. Verify the change is correct. |
| "I'm just changing == to ===" | **NEW:** Strict vs loose equality is a semantic change. Code relying on type coercion will break. Verify all comparison values. |
| "It's just an operator change" | **NEW:** Operators determine behavior. ==, ===, &&, ||, ??, ?. — each has different semantics. Verify the change is correct. |
| "I'm just adding a try-catch" | **NEW:** Error handling changes control flow. Swallowed errors hide bugs. Caught errors change return values. This is code. |
| "I'm just wrapping for logging" | **NEW:** JSON.stringify can throw on circular refs. Logging code IS code. Debug code that stays = production bugs. |
| "I'm just renaming a test file" | **NEW:** Test file names affect discovery. .test.js vs .spec.js — wrong pattern = tests don't run. Verify test runner config. |
| "I'm just updating .editorconfig" | **NEW:** Editor configs affect formatting. Indent changes cause massive diffs. Wrong settings = inconsistent codebase. |
| "I'm just creating .env.example" | **NEW:** Example files become templates. Wrong example = developers copy wrong values. Verify the example is correct. |
| "It's just a script alias" | **NEW:** Script aliases in package.json affect builds. Typo in alias = broken 'npm run dev'. This is build config. |
| "I'm just adding/removing a semicolon" | **NEW:** JavaScript ASI behavior is tricky. Adding semicolons can change meaning. Removing them invokes ASI rules. This IS code. |
| "I'm just fixing formatting" | **NEW:** Semicolons aren't "formatting" in JS - they're ASI boundary markers. Wrong semicolon placement = different parse tree. |
| "I'm just sorting imports" | **NEW:** Import order matters for side effects. `import './polyfill'` must come first. Sort tools can break initialization order. |
| "I'm just organizing the file" | **NEW:** "Organizing" that reorders imports can break side-effect-dependent code. Verify no import order dependencies. |
| "I'm just changing quotes" | **NEW:** Single vs double affects escaping needs. Template literals have different semantics. Quote changes can break strings. |
| "It's just a style preference" | **NEW:** Quote style affects what escapes are needed. Changing `"it's"` to `'it's'` breaks. Verify string contents. |
| "I'm just adding whitespace" | **NEW:** You're modifying a code file. The skill applies to ANY code file modification. Load the skill. |
| "It's just a blank line" | **NEW:** If you're editing a code file, you're doing code activity. Even "cosmetic" changes need the skill to verify no other changes slipped in. |
| "I'm just adding type annotations" | **NEW:** Types affect compilation. TypeScript can reveal bugs, change inference, require additional changes. This IS code activity. |
| "It's just documentation of existing types" | **NEW:** Type annotations aren't comments - they're compiled. Wrong types = compilation errors or hidden bugs. Verify the types are correct. |
| "I'm just adding a default parameter" | **NEW:** Default params change function signature. Callers passing `undefined` now get the default. This can change behavior. |
| "It's a simple default value" | **NEW:** Defaults affect ALL call sites passing undefined. `greet(undefined)` now returns "Hello World" not "Hello undefined". Verify callers. |
| "I'm just adding optional chaining" | **NEW:** `?.` and `&&` have different semantics. `0?.foo` vs `0 && 0.foo` behave differently. Edge cases matter. Verify behavior. |
| "It's just making it safer" | **NEW:** Optional chaining changes behavior for edge cases. It returns `undefined` instead of falsy values. Verify this is what you want. |
| "I'm just converting to arrow function" | **NEW:** Arrow functions DON'T have their own `this`. Converting methods to arrows BREAKS `this` binding. Verify no `this` usage. |
| "It's the same logic, different syntax" | **NEW:** Arrow functions change `this`, `arguments`, `super`, and `new.target` binding. "Same logic" is FALSE if any of these are used. |
| "I'm just changing || to ??" | **NEW:** `||` returns right side for ALL falsy (0, "", false, null, undefined). `??` only for null/undefined. This CHANGES behavior for 0 and "". |
| "It's safer for handling 0" | **NEW:** Yes, and that means DIFFERENT behavior. Code relying on `||` returning default for 0 will now get 0. Verify all usages. |
| "I'm just updating test data" | **NEW:** Test data changes affect what tests verify. Wrong mock data = tests pass but production fails. Test data IS test code. |
| "It's just a mock value" | **NEW:** Mock values determine test behavior. Changing "John" to "Jane" might pass a gender-based test or fail a name-length test. Verify test intent. |
| "I'm just tweaking the regex" | **NEW:** Regex is notoriously subtle. One character change can completely alter matching. Test with edge cases before and after. |
| "It's a simple regex change" | **NEW:** There are no simple regex changes. Catastrophic backtracking, capture group changes, flag changes - all cause bugs. Verify thoroughly. |
| "I'm just using destructuring" | **NEW:** Destructuring has default values, aliases, and nested semantics. `const {a = 1} = obj` differs from `const a = obj.a || 1`. |
| "I'm just using spread" | **NEW:** Spread behaves differently for arrays vs objects. Object spread is shallow. Spread can't be used with all iterables. Verify behavior. |
| "I'm just promisifying" | **NEW:** Callback→Promise changes error handling. Thrown errors become rejections. Return values become resolve values. Verify callers handle Promises. |
| "I'm just changing export style" | **NEW:** Default vs named exports affect ALL importers. Changing export style requires updating EVERY import statement. Verify all usages. |
| "I'm just adding a non-null assertion" | **NEW:** The `!` operator tells TypeScript "I KNOW this isn't null" - but do you? If you're wrong = runtime crash. Verify it's actually never null. |
| "It's just a single character (!)" | **NEW:** That single character disables TypeScript's null safety. You're accepting responsibility for null checks. Verify thoroughly. |
| "I'm just adding 'as const'" | **NEW:** `as const` changes the type from `string[]` to `readonly ["red", "green"]`. This affects what you can push, assign, or pass. Verify usages. |
| "It's just a type annotation" | **NEW:** `as const` isn't just annotation - it makes the value deeply readonly. Methods like .push() won't work. Verify no mutations expected. |
| "I'm just changing forEach to map" | **NEW:** forEach returns undefined, map returns array. If you ignore map's return value, why use map? If you need the return, forEach was wrong. |
| "It's more functional style" | **NEW:** "Functional style" isn't just syntax - map/filter/reduce have different return values. Ignoring map's return is often a bug. |
| "I'm just using includes instead of indexOf" | **NEW:** includes() uses SameValueZero (finds NaN), indexOf() uses strict equality (can't find NaN). `[NaN].includes(NaN)` is true, indexOf is -1. |
| "It's cleaner syntax" | **NEW:** includes vs indexOf have different NaN behavior. If your array might contain NaN, this change breaks code. Verify array contents. |
| "I'm just adding .bind()" | **NEW:** .bind() creates a NEW function every call. `fn.bind(this) !== fn.bind(this)`. This breaks identity checks, memoization, removeEventListener. |
| "It's just setting the context" | **NEW:** .bind() has memory implications and breaks function identity. Arrow functions might be better. Verify no identity comparisons. |
| "I'm just adding a type guard" | **NEW:** Type guards affect narrowing EVERYWHERE the function is used. Wrong type guard = TypeScript lies about types = hidden bugs. |
| "It's a simple type check" | **NEW:** Type guards teach TypeScript's type system. Teaching it wrong = false confidence in types. Verify the guard is correct. |
| "I'm just using a ternary" | **NEW:** Ternary has different precedence than if/else. Nested ternaries are hard to parse. Ternary in JSX has gotchas. Verify carefully. |
| "I'm just changing to Promise.allSettled" | **NEW:** Promise.all fails fast (one rejection = all fail). Promise.allSettled waits for all. This changes error handling semantics entirely. |
| "I'm just chaining array methods" | **NEW:** Method chain order matters. filter→map vs map→filter differ in performance and sometimes results. Verify the chain is correct. |
| "I'm just using object shorthand" | **NEW:** Shorthand { name } couples object key to variable name. Rename the var but forget the object = broken. Verify all usages. |
| "It's cleaner ES6 syntax" | **NEW:** Shorthand syntax creates implicit coupling. Refactoring tools might miss it. Explicit { name: name } is more refactor-safe. |
| "I'm just converting to a getter" | **NEW:** Getters are CALLED every access, properties are read once. Performance differs. Object.keys() excludes getters. Verify behavior. |
| "It's the same value" | **NEW:** Getter vs property affects enumeration, JSON.stringify, spread, Object.assign. These behave differently. Verify all usages. |
| "I'm just using WeakMap for memory" | **NEW:** WeakMap can't iterate (.keys/.values/.entries don't exist). Keys MUST be objects. No .size property. Verify you don't need these. |
| "It's just a more efficient Map" | **NEW:** WeakMap is NOT a Map. Completely different API. If you need to iterate or check size, WeakMap breaks your code. |
| "I'm just using BigInt for precision" | **NEW:** BigInt CANNOT mix with Number. `123n + 1` throws TypeError. ALL operations need BigInt operands. Verify entire calculation chain. |
| "It's just a number type change" | **NEW:** BigInt is NOT a Number. typeof is different. JSON.stringify fails. Math functions don't work. This breaks many things. |
| "I'm just making it truly private with #" | **NEW:** # fields are ACTUALLY private. Tests that accessed _fields will fail. Debugging can't inspect them. Serialization skips them. |
| "It's just the modern private syntax" | **NEW:** _ convention was accessible for testing/debugging. # is truly private. This can break test suites and debugging workflows. |
| "I'm just simplifying the null check" | **NEW:** `!= null` uses type coercion - it catches BOTH null AND undefined. If you only wanted null, this changes behavior. Verify intent. |
| "It's the same check" | **NEW:** `!== null && !== undefined` vs `!= null` aren't always interchangeable. Edge cases with objects valueOf() can differ. |
| "I'm just using spread instead of Object.assign" | **NEW:** Spread and Object.assign differ for setters - assign invokes them, spread doesn't. Prototype handling differs too. Verify behavior. |
| "I'm just moving init to class field" | **NEW:** Class fields evaluate at different time than constructor. Order relative to super() differs. This can break initialization. |
| "I'm just adding a static block" | **NEW:** Static blocks run once at class definition time. Errors there crash module load. Side effects run at import time. Verify impact. |
| "I'm just using JSON for deep clone" | **NEW:** JSON.parse/stringify loses functions, undefined, Dates become strings, Symbols vanish, circular refs THROW. Use structuredClone or library. |
| "It's a simple deep copy" | **NEW:** JSON clone is NOT a general deep copy. It only works for JSON-serializable data. Verify your object has no special types. |
| "I'm just using parseInt" | **NEW:** Without radix, parseInt has edge cases: "0x10"=16, leading zeros were octal. Always pass radix 10 explicitly. |
| "The number is always base 10" | **NEW:** You can't guarantee input. User might paste "0x1F". parseInt("08") was 0 in old browsers. Always specify radix. |
| "I'm just converting to boolean" | **NEW:** You're modifying a code file. Boolean()/!! are equivalent but you're still making a change. Load the skill. |
| "I'm just using Object.freeze" | **NEW:** Object.freeze is SHALLOW. `freeze({a:{b:1}})` - inner object {b:1} is still mutable! Use deep freeze if needed. |
| "I'm making it immutable" | **NEW:** Freeze doesn't make nested objects immutable. Also, writes throw in strict mode. Verify you want this behavior. |
| "I'm just using queueMicrotask" | **NEW:** Microtasks run BEFORE rendering, setTimeout runs AFTER. Microtask loops can freeze the browser. Completely different timing. |
| "It's better timing" | **NEW:** "Better" depends on use case. Microtasks block UI updates. setTimeout yields to rendering. Wrong choice = frozen UI or flickering. |
| "I'm just using addEventListener" | **NEW:** addEventListener allows MULTIPLE handlers, onclick REPLACES. Also, addEventListener has capture option, different `this` binding. |
| "It's more flexible" | **NEW:** Flexibility means different behavior. Multiple handlers might not be wanted. Handler order matters. Verify this is intentional. |
| "I'm just changing event handling" | **NEW:** Bubbling vs capturing, stopPropagation, stopImmediatePropagation, passive - event semantics are complex. Verify behavior. |
| "I'm just converting to string" | **NEW:** String(null)="null", (null).toString() throws, `${null}`="null", ""+null="null". But undefined, objects, symbols all differ. Verify. |
| "I'm just parsing a number" | **NEW:** Number(""), parseInt(""), parseFloat(""), +"" all return different values! (0, NaN, NaN, 0). Verify your parser choice. |
| "I'm just updating code examples in docs" | **NEW:** Users COPY documentation examples into production! Wrong example = users write buggy code. Doc examples ARE production code. |
| "It's just a README snippet" | **NEW:** README code is the FIRST thing developers copy. If your example has a bug, thousands of users inherit that bug. Verify it compiles. |
| "I'm just updating CI workflow" | **NEW:** GitHub Actions, GitLab CI, etc. ARE code that executes. Wrong step = broken builds, failed deploys, security holes. |
| "It's just YAML config for CI" | **NEW:** CI YAML runs commands, sets env vars, deploys code. A typo in CI config can deploy to wrong environment or leak secrets. |
| "I'm just updating the Dockerfile" | **NEW:** Dockerfile changes affect what runs in production. Wrong CMD = container won't start. Wrong ENV = wrong behavior. |
| "It's just container config" | **NEW:** ENTRYPOINT vs CMD, multi-stage builds, layer caching - Dockerfiles have complex semantics. Verify the container actually runs. |
| "I'm just updating the API spec" | **NEW:** OpenAPI/Swagger/Proto specs often GENERATE client code. Wrong spec = wrong generated clients = production bugs. |
| "It's just documentation of the API" | **NEW:** API specs are executable documentation. codegen tools, mock servers, validators all use them. Wrong spec = broken tooling. |
| "I'm just updating translations" | **NEW:** i18n files contain format strings, HTML, placeholders. Wrong translation = broken UI, XSS vulnerabilities, crashed formatters. |
| "It's just text in another language" | **NEW:** Translation files have syntax ({0}, %s, <b>). Wrong escaping = displayed HTML. Missing placeholder = crash. |
| "I'm just updating webpack config" | **NEW:** webpack/vite/rollup/esbuild configs ARE JavaScript/TypeScript. They run at build time. Wrong config = broken bundle. |
| "It's just build configuration" | **NEW:** Build configs control what code ships. Wrong entry point = wrong bundle. Wrong loader = failed compilation. These ARE code. |
| "I'm just updating K8s manifest" | **NEW:** Kubernetes manifests control deployment, scaling, networking. Wrong replica count = outage. Wrong resource limit = OOM kills. |
| "It's just infrastructure config" | **NEW:** Infrastructure as Code (Terraform/Pulumi/CloudFormation) creates REAL infrastructure. Wrong config = wrong servers, databases, networking. |
| "I'm just updating nginx config" | **NEW:** Web server config controls routing, SSL, headers. Wrong config = security vulnerabilities, broken routes, CORS failures. |
| "I'm just updating a migration file" | **NEW:** Database migrations change SCHEMA that ALL code depends on. Wrong migration = broken queries, data loss, rollback nightmares. |
| "It's just database schema" | **NEW:** Schema changes affect every query. Adding NOT NULL to existing column = migration failure. Verify backwards compatibility. |
| "I'm just updating a git hook" | **NEW:** Git hooks are EXECUTABLE scripts. pre-commit runs on EVERY commit. Wrong hook = broken workflow, blocked commits. |
| "It's just a pre-commit check" | **NEW:** Hooks can prevent commits, modify files, run linters. Wrong hook = developers can't commit or commits silently modified. |
| "I'm just updating the Makefile" | **NEW:** Makefiles are BUILD CODE. Wrong target = wrong build. Missing dependency = stale artifacts. These cause CI failures. |
| "It's just a build target" | **NEW:** Make targets control compilation, testing, deployment. Wrong command = wrong binary. This IS programming. |
| "I'm just updating a shell script" | **NEW:** Shell scripts are EXECUTABLE code. deploy.sh wrong = production broken. Syntax error = script aborts midway. |
| "It's just a bash script" | **NEW:** Shell scripts run with REAL permissions. `rm -rf` typos are legendary. Missing quotes = word splitting bugs. |
| "I'm just writing a SQL procedure" | **NEW:** Stored procedures run IN THE DATABASE. Wrong logic = corrupted data. No rollback for logic errors. |
| "It's just database code" | **NEW:** SQL procedures affect ALL applications hitting that database. One bug = all consumers affected. |
| "I'm just updating the GraphQL schema" | **NEW:** GraphQL schemas GENERATE types for frontend and backend. Wrong field = type errors in multiple codebases. |
| "It's just an API type" | **NEW:** Schema changes affect code generation. Removing a field = all clients break. Adding required field = breaking change. |
| "I'm just updating CSS" | **NEW:** CSS affects EVERYTHING users see. Wrong z-index = elements hidden. Wrong display = layout broken. |
| "It's just styling" | **NEW:** CSS custom properties (--vars) cascade everywhere. One wrong value = wrong colors/spacing across entire app. |
| "I'm just editing the lockfile directly" | **NEW:** Lockfiles have complex resolution graphs. Manual edits can break npm/yarn install. Let package manager regenerate. |
| "It's just pinning a version" | **NEW:** Lockfile entries have integrity hashes, dependency trees. Wrong edit = "Cannot resolve" errors or silent version mismatch. |
| "I'm just updating the snapshot" | **NEW:** Snapshots verify output. Updating to pass = accepting current output. If output is WRONG, you just enshrined a bug. |
| "The snapshot test was failing" | **NEW:** Snapshot failures mean OUTPUT CHANGED. Ask: is the new output CORRECT? Don't blindly update to make green. |
| "I'm just adding an onclick to SVG" | **NEW:** SVGs are XML that can contain JavaScript, CSS, external references. onclick in SVG = JavaScript execution. Security risk. |
| "It's just an image file" | **NEW:** SVG is NOT just an image. It's a programmable vector format. SVGs from untrusted sources = XSS attacks. |
| "I'm just updating a notebook cell" | **NEW:** Jupyter notebooks contain EXECUTABLE code. Cell outputs are cached. Wrong cell = wrong analysis shared with team. |
| "It's just data exploration code" | **NEW:** Notebook code often becomes production code. Bad patterns in notebooks get copied. Notebooks ARE code. |
| "I'm just adding a debug config" | **NEW:** launch.json controls debugger behavior. Wrong args = debugging wrong process. Wrong env = different behavior than prod. |
| "It's just IDE settings" | **NEW:** IDE configs affect builds, debugging, formatting. Committed .vscode/ affects entire team. Wrong settings = team-wide issues. |
| "I'm just adding a shell alias" | **NEW:** .bashrc/.zshrc run on EVERY terminal. Syntax error = can't open new terminals. Wrong alias = wrong commands run. |
| "It's just my personal config" | **NEW:** Shell configs define PATH, env vars, aliases. Wrong PATH = wrong binaries run. This affects ALL your work. |
| "I'm just adding a cron job" | **NEW:** Cron jobs run AUTOMATICALLY on schedule. Wrong cron = wrong command runs every minute/hour/day. Untested automation. |
| "It's just a scheduled task" | **NEW:** Scheduled tasks run without supervision. Syntax error = silent failure. Wrong timing = resource exhaustion or missed jobs. |
| "I'm just updating the submodule" | **NEW:** Submodules control what CODE is pulled. Wrong commit = wrong dependency code. Can introduce breaking changes silently. |
| "It's just a git reference" | **NEW:** Submodule refs determine exact code version. Pointing to wrong commit = different behavior, security vulnerabilities. |
| "I'm just changing a URL" | **NEW:** URLs are CONNECTION STRINGS. Wrong URL = data sent to wrong server. Staging URL in prod = data loss or corruption. |
| "It's just an endpoint" | **NEW:** Endpoints define where code talks. localhost vs prod, HTTP vs HTTPS, wrong port - all cause failures or security issues. |
| "I'm just updating the error message" | **NEW:** Error messages are IN CODE FILES. Also: error messages can leak stack traces, paths, versions. Security and UX issue. |
| "It's just text for users" | **NEW:** User-facing text affects UX, i18n, and security. Wrong format string = crash. Leaked info = security vulnerability. |
| "I'm just writing a mock" | **NEW:** Mocks ARE code that executes in tests. Wrong mock = tests pass but production fails. Mock complexity hides bugs. |
| "It's just test code" | **NEW:** Test code runs in CI. Test code that crashes = blocked deployments. Test code that lies = false confidence. |
| "I'm just adding a polyfill" | **NEW:** Polyfills affect RUNTIME behavior globally. Import order matters. Wrong polyfill = subtle bugs in specific browsers. |
| "It's just browser compatibility" | **NEW:** Polyfills can conflict, override native implementations. Multiple polyfills for same feature = undefined behavior. |
| "I'm just updating docker-compose" | **NEW:** docker-compose defines your ENTIRE local/dev environment. Wrong volume = data loss. Wrong network = services can't communicate. |
| "It's just container orchestration" | **NEW:** Service definitions control ports, env vars, dependencies. Wrong depends_on = startup race conditions. |
| "I'm just updating the Ansible playbook" | **NEW:** Ansible runs COMMANDS on REAL servers. Wrong playbook = misconfigured production. This IS programming servers. |
| "It's just configuration management" | **NEW:** Chef/Puppet/Salt execute code on infrastructure. Mistakes affect all managed nodes. Test in staging first. |
| "I'm just adding a workspace package" | **NEW:** Monorepo configs control dependency resolution. Wrong config = wrong versions installed, build failures, circular deps. |
| "It's just project organization" | **NEW:** Workspace configs affect hoisting, linking, build order. Wrong setup = "cannot find module" errors everywhere. |
| "I'm just setting up Git LFS" | **NEW:** LFS patterns affect what gets stored where. Wrong pattern = huge files in git history OR missing files on clone. |
| "It's just large file storage" | **NEW:** LFS changes are hard to undo. Files tracked by LFS need LFS installed. Missing setup = broken clones for team. |
| "I'm just adding a pre-commit hook" | **NEW:** Pre-commit hooks run on EVERY commit for EVERY developer. Slow hook = frustrated team. Broken hook = blocked commits. |
| "It's just a linting check" | **NEW:** Pre-commit configs are shared. Your hook runs on everyone's machine. Misconfigured = team productivity blocked. |
| "I'm just updating the extension manifest" | **NEW:** Manifest.json defines extension PERMISSIONS. Wrong permission = security vulnerability. Missing permission = broken extension. |
| "It's just browser extension config" | **NEW:** Extension manifests control CSP, host permissions, API access. Wrong manifest = extension rejected by store or security issue. |
| "I'm just updating .env.local" | **NEW:** Secrets files contain CREDENTIALS. Wrong secret = wrong database. Committed secret = security incident. NEVER commit these. |
| "It's just environment config" | **NEW:** .env files control runtime behavior. Wrong API key = calls to wrong service. Production secrets in dev = data leak risk. |
| "I'm just updating the service worker" | **NEW:** Service workers INTERCEPT network requests, control caching, enable offline. Wrong cache = users see stale data forever. |
| "It's just caching logic" | **NEW:** Service worker bugs are hard to fix - users have old worker cached. Push notification bugs = angry users. Test thoroughly. |
| "I'm just adding a web worker" | **NEW:** Web workers run JavaScript in background threads. Concurrency bugs, message passing errors, race conditions - all apply. |
| "It's just background processing" | **NEW:** Worker bugs cause silent failures. postMessage errors are swallowed. Memory leaks in workers crash tabs. Test isolation matters. |
| "I'm just updating renovate.json" | **NEW:** Renovate config controls AUTOMATIC dependency updates. Wrong automerge = untested deps in prod. Wrong schedule = update chaos. |
| "It's just dependency bot config" | **NEW:** Dependabot/Renovate PRs run CI and can automerge. Wrong config = CI overload, breaking updates merged, security patches skipped. |
| "I'm just updating Storybook config" | **NEW:** Storybook configs are JavaScript/TypeScript. Wrong webpack override = broken builds. Stories that error = broken component docs. |
| "It's just component documentation" | **NEW:** Storybook runs React/Vue/Angular components. Component bugs in Storybook = component bugs in app. Treat as real code. |
| "I'm just adding a route" | **NEW:** Framework routes define app structure. Wrong route = 404s. Wrong middleware = unprotected endpoints. Dynamic routes = parameter bugs. |
| "It's just URL configuration" | **NEW:** Routes in Next/Nuxt/SvelteKit are CODE. Server-side routes can access secrets. Wrong route = data exposure. SSR errors crash pages. |
| "I'm just changing the sourcemap config" | **NEW:** Sourcemaps affect debugging AND security. Wrong config = source code leaked in production. Missing sourcemaps = can't debug prod issues. |
| "It's just debug configuration" | **NEW:** Sourcemaps can expose your entire codebase structure. inline sourcemaps bloat bundles. hidden sourcemaps still ship if path found. |
| "I'm just writing a .d.ts file" | **NEW:** Declaration files define types that TypeScript TRUSTS. Wrong declaration = wrong usage across entire codebase. Type lies are bug factories. |
| "It's just type definitions" | **NEW:** .d.ts files can miss method overloads, have wrong nullability, or lie about what library does. Every consumer trusts your lies. |
| "I'm just updating the .proto file" | **NEW:** Protocol Buffers GENERATE code. Adding required field = breaks old clients. Renaming field = breaks serialization. Proto IS code. |
| "It's just API schemas" | **NEW:** gRPC/protobuf schema changes affect every service using it. Wrong types = runtime errors in generated clients. Version carefully. |
| "I'm just updating test seeds" | **NEW:** Seed data determines what tests verify. Wrong seed = tests pass on wrong data. Seed changes can hide or reveal bugs. |
| "It's just test data" | **NEW:** Database fixtures affect test isolation. Shared seeds = tests depend on each other. Wrong seed = flaky tests or false confidence. |
| "I'm just editing the email template" | **NEW:** Email templates go to REAL USERS. Broken template = broken layout in Outlook/Gmail. Wrong data binding = leaked PII. Security risk. |
| "It's just HTML for emails" | **NEW:** Email HTML is DIFFERENT from web HTML. Many CSS features don't work. Tables for layout. Broken template = customer confusion. |
| "I'm just configuring log rotation" | **NEW:** Log rotation affects production. Wrong config = disk fills up and crashes server. Too aggressive = lose logs you need for debugging. |
| "It's just logging config" | **NEW:** Logrotate runs automatically. Wrong timing = logs deleted during incident investigation. Wrong compression = can't read logs. |
| "I'm just updating the PDF template" | **NEW:** PDF templates render for CUSTOMERS. Broken CSS = unreadable invoices. Wrong data binding = incorrect amounts. Legal liability. |
| "It's just a print layout" | **NEW:** PDF generation is headless browser rendering. puppeteer/wkhtmltopdf quirks differ from browsers. Test the actual PDF output. |
| "I'm just updating font files" | **NEW:** Font files affect EVERY piece of text. Wrong font = broken characters. Missing glyphs = blank boxes. Licensing violations = lawsuits. |
| "It's just typography" | **NEW:** Font loading affects performance (FOUT/FOIT). Wrong font-display = layout shift. Subset wrong = missing characters for some languages. |
| "I'm just replacing the .wasm file" | **NEW:** WebAssembly IS compiled code. Wrong .wasm = runtime crashes. Version mismatch with JS glue code = memory corruption. Binary = hard to debug. |
| "It's just a binary asset" | **NEW:** WASM executes in the browser with near-native speed. Bugs in WASM can crash tabs, corrupt memory, have security vulnerabilities. |
| "I'm just updating the shader" | **NEW:** Shaders run on GPU. Wrong shader = visual glitches, performance issues, or GPU crashes. Shader bugs are notoriously hard to debug. |
| "It's just graphics code" | **NEW:** GLSL/HLSL is a real programming language. Division by zero = GPU hang. Infinite loops = browser freeze. Test on multiple GPUs. |
| "I'm just updating the XSLT" | **NEW:** XSLT is Turing-complete programming. Wrong template = wrong output. XSLT bugs are subtle. XPath expressions can fail silently. |
| "It's just XML transformation" | **NEW:** XSLT transforms data. Wrong transformation = corrupted output. Missing template match = data dropped. Security: XSLT can read files! |
| "I'm just updating the sitemap" | **NEW:** Sitemap tells search engines what to crawl. Wrong URLs = pages not indexed. Wrong priority = important pages deprioritized. SEO impact. |
| "It's just SEO stuff" | **NEW:** Sitemap errors can delist pages from Google. Wrong lastmod = stale cache. Too many URLs = crawl budget wasted. Business impact. |
| "I'm just updating the RSS feed" | **NEW:** RSS feeds go to feed readers. Broken XML = subscribers lose posts. CDATA/encoding wrong = HTML entities shown raw. |
| "It's just a feed template" | **NEW:** RSS/Atom has strict XML requirements. Missing required elements = invalid feed. Wrong dates = posts in wrong order. |
| "I'm just updating robots.txt" | **NEW:** robots.txt affects ALL crawlers. Disallow wrong path = pages vanish from Google. Allow admin paths = security exposure. |
| "It's just crawler rules" | **NEW:** robots.txt mistakes are silent - no errors, just missing pages. Can take weeks to notice SEO impact. One typo = disaster. |
| "I'm just updating .htaccess" | **NEW:** .htaccess runs on every request. Syntax error = 500 errors for entire site. Wrong RewriteRule = infinite loops, broken URLs. |
| "It's just Apache config" | **NEW:** .htaccess controls redirects, security headers, access. Wrong auth rule = exposed admin. Wrong redirect = SEO penalties. |
| "I'm just updating CSP headers" | **NEW:** CSP controls what scripts/styles can run. Too strict = broken features. Too loose = XSS vulnerabilities. Test thoroughly. |
| "It's just security headers" | **NEW:** Wrong CSP = inline scripts blocked, CDN assets blocked, iframes broken. Report-only first, then enforce. |
| "I'm just adding a CORS origin" | **NEW:** CORS controls which domains can call your API. Wrong origin = security hole. Missing origin = broken integrations. Wildcard = danger. |
| "It's just cross-origin config" | **NEW:** CORS mistakes are security vulnerabilities OR broken features. credentials: true + wildcard origin = critical vulnerability. |
| "I'm just updating browserslist" | **NEW:** browserslist affects what Babel/Autoprefixer outputs. Wrong targets = polyfills missing OR bundle bloated. Test in target browsers. |
| "It's just browser targets" | **NEW:** Removing old browser support can break users. Adding old browsers bloats bundles. Changes affect EVERY user. |
| "I'm just updating the JSON Schema" | **NEW:** JSON Schema validates data. Wrong required field = valid data rejected. Missing validation = invalid data accepted. |
| "It's just validation rules" | **NEW:** Schema changes affect API contracts. Stricter schema = breaking change. Looser schema = invalid data in database. |
| "I'm just updating the proxy config" | **NEW:** Proxy routes requests. Wrong upstream = data sent to wrong server. Missing path = 502 errors. Timeout wrong = hanging requests. |
| "It's just request routing" | **NEW:** Proxy mistakes can send production traffic to staging, expose internal services, or create security holes. Test thoroughly. |
| "I'm just updating SSL config" | **NEW:** SSL config affects security. Weak ciphers = vulnerable to attacks. Wrong cert path = HTTPS broken. Wrong protocol = compatibility issues. |
| "It's just certificate stuff" | **NEW:** TLS misconfig can cause site to be unreachable, browser warnings, or security vulnerabilities. HSTS mistakes lock you out. |
| "I'm just adjusting rate limits" | **NEW:** Rate limits protect your service. Too low = legitimate users blocked. Too high = DoS vulnerability. Per-user vs global matters. |
| "It's just throttling config" | **NEW:** Rate limit mistakes cause outages or attacks. Wrong key (IP vs user) = shared limits. Wrong window = burst issues. |
| "I'm just updating A/B test percentages" | **NEW:** A/B config affects REAL USERS. Wrong percentage = skewed experiment data. Wrong assignment = users see wrong features. |
| "It's just experiment config" | **NEW:** A/B test bugs affect business metrics. Sticky assignment matters. Wrong control group = invalid conclusions. Revenue impact. |
| "I'm just updating tracing config" | **NEW:** Tracing config affects observability. Wrong sampling = missing data when debugging. Wrong exporter = traces sent nowhere. |
| "It's just observability" | **NEW:** OpenTelemetry config affects debugging production issues. Missing traces = blind during incidents. Wrong context propagation = broken traces. |
| "I'm just updating cache config" | **NEW:** Cache config affects performance AND correctness. Wrong TTL = stale data served. Cache key wrong = data leaks between users. |
| "It's just caching settings" | **NEW:** Cache invalidation is one of the hardest problems. Wrong config = stale data for hours. CDN cache mistakes affect all users. |
| "I'm just updating queue config" | **NEW:** Message queue config affects reliability. Wrong ACK = lost messages. Wrong exchange = messages routed wrong. Dead letter config matters. |
| "It's just messaging setup" | **NEW:** Kafka/RabbitMQ misconfig can lose data. Wrong partition key = ordering broken. Consumer group wrong = duplicate processing. |
| "I'm just updating the index mapping" | **NEW:** Elasticsearch mappings can't be changed after creation. Wrong analyzer = search broken. Wrong type = reindex entire dataset. |
| "It's just search config" | **NEW:** Index mapping mistakes require full reindex. Dynamic mapping can explode field count. Wrong mapping = queries fail or return wrong results. |
| "I'm just adding a webhook" | **NEW:** Webhooks send data EXTERNALLY. Wrong URL = data sent to wrong service. Missing auth = data exposed. Retry config = duplicate events. |
| "It's just an integration endpoint" | **NEW:** Webhook config affects external systems. Wrong payload format = integration broken. Missing signature = security hole. |
| "I'm just updating OAuth config" | **NEW:** OAuth config is AUTHENTICATION. Wrong redirect URI = auth broken. Wrong scopes = over-permissioned OR under-permissioned. |
| "It's just login settings" | **NEW:** OAuth/SAML misconfig = users locked out OR security vulnerabilities. Wrong issuer = tokens rejected. Wrong audience = tokens accepted from wrong source. |
| "I'm just updating the cron expression" | **NEW:** Cron syntax is tricky. `0 0 * * *` vs `* 0 * * *` = once daily vs 60 times. Wrong expression = job runs wrong time or never. |
| "It's just a schedule string" | **NEW:** Cron expressions control WHEN code runs. Timezone matters. Day-of-week vs day-of-month conflicts. Test with cron expression validator. |
| "I'm just updating feature flag config" | **NEW:** Feature flag SDK config affects flag evaluation. Wrong default = feature enabled/disabled for everyone. Wrong targeting = wrong users get feature. |
| "It's just SDK settings" | **NEW:** LaunchDarkly/Split config controls feature rollout. Wrong cache TTL = stale flags. Wrong context = targeting broken. Revenue impact. |
| "I'm just updating Sentry config" | **NEW:** Error monitoring config affects visibility. Wrong DSN = errors go nowhere. Wrong sampling = miss errors. Wrong filtering = noise or silence. |
| "It's just error tracking" | **NEW:** Sentry/Bugsnag misconfig = blind during incidents. Source maps wrong = unreadable stack traces. Release tracking wrong = can't correlate. |
| "I'm just updating analytics tracking" | **NEW:** Analytics config affects business metrics. Wrong tracking ID = data in wrong property. Wrong events = bad product decisions. GDPR implications. |
| "It's just tracking code" | **NEW:** GA/Mixpanel config affects data quality. Wrong user ID = broken funnels. Wrong properties = unusable data. Privacy: PII in analytics = violations. |
| "I'm just updating license headers" | **NEW:** License headers are LEGAL documents. Wrong license = legal liability. Missing attribution = license violation. Year wrong = looks abandoned. |
| "It's just copyright text" | **NEW:** License headers in CODE FILES. Changing license affects legal terms. Some licenses are incompatible. Legal review recommended. |
| "I'm just updating the changelog" | **NEW:** Changelog is release documentation. Wrong version = confusion. Missing breaking changes = angry users. Links to wrong commits = misdirection. |
| "It's just release notes" | **NEW:** Changelog affects users upgrading. Semantic versioning matters. Breaking change in minor version = broken builds. Accurate changelog = trust. |
| "I'm just updating Swagger UI config" | **NEW:** Swagger/Redoc config controls API documentation. Wrong config = broken examples, wrong auth flows, misleading docs. Developers copy these examples! |
| "It's just API documentation" | **NEW:** API docs that show wrong examples = wrong client code. Try-it-out with wrong config = failed requests. Broken docs = developer frustration. |
| "I'm just adding a VS Code snippet" | **NEW:** Code snippets generate code that developers use. Wrong snippet = wrong code inserted everywhere. Tab stops wrong = frustrated developers. |
| "It's just editor shortcuts" | **NEW:** .vscode/*.code-snippets become templates developers rely on. Wrong template = wrong patterns propagated across codebase. |
| "I'm just updating a Husky hook" | **NEW:** Husky hooks are SHELL SCRIPTS that run on git operations. pre-commit hook broken = developers can't commit. post-merge broken = dev env corrupted. |
| "It's just git hooks config" | **NEW:** .husky/* scripts execute automatically. Syntax error = blocked commits. Wrong command = wrong checks run or skipped. |
| "I'm just updating lint-staged config" | **NEW:** lint-staged runs on commit. Wrong glob = files skipped. Wrong command = broken formatting or lint. Exit 1 = blocked commits. |
| "It's just pre-commit formatting" | **NEW:** lint-staged config affects EVERY commit. Wrong pattern = some files never linted. Wrong formatter = inconsistent codebase. |
| "I'm just updating the release script" | **NEW:** Release/deploy scripts are DEPLOYMENT AUTOMATION. Wrong script = failed releases, wrong artifacts published, broken production. |
| "It's just deployment automation" | **NEW:** Release scripts control what gets deployed. Wrong version = overwritten packages. Missing step = incomplete release. Script bugs = outages. |
| "I'm just updating health check config" | **NEW:** Health checks are MONITORING. Wrong endpoint = false positives. Wrong thresholds = missed outages OR alert fatigue. |
| "It's just monitoring config" | **NEW:** Health check misconfiguration = blind to outages or paged constantly for nothing. Wrong path = 404 looks healthy. Wrong timeout = flaky alerts. |
| "I'm just adding a postinstall script" | **NEW:** postinstall runs on EVERY npm install. Wrong script = security vulnerabilities, corrupted node_modules, broken dev setup for entire team. |
| "It's just a lifecycle hook" | **NEW:** npm lifecycle scripts EXECUTE code. postinstall can run arbitrary commands. This is code that runs on every developer's machine. |
| "I'm just updating codegen config" | **NEW:** GraphQL codegen GENERATES types. Wrong output path = types not found. Wrong plugin = wrong generated code. Types affect entire codebase. |
| "It's just code generation config" | **NEW:** Codegen config determines what code gets created. Wrong config = wrong types, wrong resolvers, wrong clients. Generated code IS code. |
| "I'm just configuring test reporters" | **NEW:** Test reporters affect CI output. Wrong reporter = results not uploaded, broken dashboards, lost test history. JUnit XML wrong = CI can't parse. |
| "It's just output formatting" | **NEW:** Reporter config affects what CI sees. Missing junit = PR checks incomplete. Wrong format = results lost. CI systems depend on correct output. |
| "I'm just updating .vimrc" | **NEW:** Shared editor configs affect team. Wrong indent setting = inconsistent formatting. Wrong tab = tabs vs spaces wars. Affects every file touched. |
| "It's just editor preferences" | **NEW:** .vimrc, .dir-locals.el in repo affect TEAM. Wrong setting = everyone's editor misbehaves. Syntax file wrong = broken highlighting team-wide. |
| "I'm just updating TypeDoc config" | **NEW:** TypeDoc generates API documentation. Wrong entry point = missing docs. Wrong exclude = internal APIs exposed. Wrong theme = broken docs. |
| "It's just documentation config" | **NEW:** API docs are what developers use. Missing or wrong docs = developers make mistakes. Wrong examples in docs = bugs propagated. |
| "I'm just adding browser targets to Playwright" | **NEW:** Browser targets determine what gets tested. Missing browser = bugs ship to users. Wrong viewport = mobile bugs missed. |
| "It's just test configuration" | **NEW:** Test config determines WHAT gets tested. Wrong config = false confidence. Missing headless = CI fails. Wrong timeout = flaky tests. |
| "I'm just updating Tailwind config" | **NEW:** Tailwind config IS your design system. Wrong color = inconsistent brand. Wrong breakpoint = broken responsive. Wrong spacing = UI chaos. |
| "It's just CSS utility config" | **NEW:** tailwind.config.js generates CSS. Wrong purge config = missing styles in production. Wrong theme = entire app looks wrong. |
| "I'm just updating serverless.yml" | **NEW:** serverless.yml deploys infrastructure. Wrong handler = 404s everywhere. Wrong memory = OOM crashes. Wrong timeout = timed out requests. |
| "It's just Lambda config" | **NEW:** Infrastructure config affects REAL production. Wrong runtime = code won't run. Wrong IAM = security holes or broken permissions. |
| "I'm just updating Vercel config" | **NEW:** Deployment config affects production. Wrong redirect = SEO disaster. Wrong headers = security vulnerability. Wrong env = wrong API keys. |
| "It's just deployment settings" | **NEW:** vercel.json/netlify.toml run in PRODUCTION. Wrong rewrite = requests go nowhere. Wrong function config = endpoints broken. |
| "I'm just updating the PWA manifest" | **NEW:** Manifest defines installable app. Wrong icon = broken home screen. Wrong display mode = wrong UX. Wrong scope = install fails. |
| "It's just app metadata" | **NEW:** PWA manifest affects mobile install experience. Wrong start_url = app opens wrong page. Wrong theme_color = jarring experience. |
| "I'm just updating turbo.json" | **NEW:** Turborepo/Nx pipeline config controls build orchestration. Wrong dependency graph = stale builds. Wrong cache key = wrong cache hits. Wrong pipeline = tasks skipped. |
| "It's just monorepo build config" | **NEW:** Monorepo task runners control WHAT BUILDS and WHEN. Wrong inputs = cache never invalidates. Wrong dependsOn = tasks run out of order. Stale artifacts shipped. |
| "I'm just adding a pnpm override" | **NEW:** pnpm overrides/resolutions force dependency versions. Wrong override = different code than package expects. Override can mask security vulnerabilities. |
| "It's just dependency resolution" | **NEW:** Overrides bypass normal resolution. You're telling pnpm "I know better than the lockfile." If you're wrong = runtime errors, security holes, or subtle bugs. |
| "I'm just updating .releaserc" | **NEW:** semantic-release config controls publishing. Wrong branch = releases from wrong branch. Wrong plugins = broken changelog, missing artifacts, wrong npm publish. |
| "It's just release automation" | **NEW:** Release config automates PRODUCTION PUBLISHING. Wrong version = breaking changes shipped as patch. Wrong assets = incomplete release. Users get broken versions. |
| "I'm just updating commitlint config" | **NEW:** Commitlint enforces commit message standards. Wrong rules = bad commits allowed or good commits rejected. Blocks team or allows unstructured history. |
| "It's just commit message rules" | **NEW:** Commitlint often gates CI. Wrong config = everyone's commits rejected. Too loose = conventional commit tooling breaks. Changelog generation fails. |
| "I'm just updating .swcrc" | **NEW:** swc/esbuild compile 10-100x faster than Babel/tsc. Same speed for shipping broken code. Wrong target = runtime syntax errors. Wrong transforms = missing features. |
| "It's just fast compiler config" | **NEW:** Fast compilers mean less time to catch problems. swc has different defaults than Babel. esbuild has different tree-shaking. Wrong config = wrong output, shipped fast. |
| "I'm just updating biome.json" | **NEW:** Biome is linter AND formatter. Wrong rule = wrong code allowed. Wrong formatting = inconsistent codebase. Biome replaces ESLint+Prettier - double the impact. |
| "It's just linter/formatter config" | **NEW:** Linter rules define code quality. Wrong config = bugs pass linting. Wrong ignores = files never linted. You're defining what "correct" means for your codebase. |
| "I'm just updating bun.lockb" | **NEW:** Bun's lockfile is BINARY - you can't inspect it like package-lock.json. Wrong versions = wrong behavior. Bun-specific bugs are hard to debug. |
| "It's just a lockfile" | **NEW:** Binary lockfiles are opaque. You don't know what changed. Bun resolution differs from npm/yarn. Different behavior, same file extension pattern. |
| "I'm just updating deno.json" | **NEW:** Deno config controls import maps, tasks, AND compiler options. Wrong import map = loading wrong module. Wrong task = wrong command runs. Runtime differences. |
| "It's just Deno configuration" | **NEW:** Deno has different defaults than Node. deno.json controls security permissions too. Wrong config = locked out features or security holes. |
| "I'm just updating schema.prisma" | **NEW:** Prisma schema GENERATES TypeScript types. Wrong field type = runtime crash. Wrong relation = data integrity bugs. Missing index = slow queries. |
| "It's just data modeling" | **NEW:** Prisma schema IS code - it generates code. Every model change affects every query using it. Missing nullable = crashes. Wrong cascade = data loss. |
| "I'm just updating drizzle.config.ts" | **NEW:** Drizzle config is TypeScript that controls database operations. Wrong driver = wrong database connected. Wrong output = migrations fail. This IS code. |
| "It's just ORM configuration" | **NEW:** ORM config files are executable. drizzle.config.ts runs during schema gen. Wrong config = wrong schema, wrong migrations, wrong types. |
| "I'm just updating vitest.config.ts" | **NEW:** Vitest config is TypeScript code. Wrong globals = tests fail mysteriously. Wrong environment = jsdom vs node behavior differs. Wrong setupFiles = tests lie. |
| "It's just test runner config" | **NEW:** Test config determines HOW tests run. Wrong coverage config = blind spots. Wrong reporters = lost results. Wrong threads = flaky tests. |
| "I'm just updating wrangler.toml" | **NEW:** Wrangler deploys to Cloudflare's edge network. Wrong route = traffic goes nowhere. Wrong binding = wrong database, KV, R2. Production traffic affected. |
| "It's just Worker deployment config" | **NEW:** Workers run in production on every request. Wrong config = every user affected. Wrong environment = production uses dev secrets. |
| "I'm just updating capacitor.config.ts" | **NEW:** Capacitor bridges web and native. Wrong server URL = app calls wrong API. Wrong plugin config = native crashes. Wrong webDir = blank app. |
| "It's just mobile app config" | **NEW:** Mobile config affects every device install. Wrong splash = ugly. Wrong scheme = deep links break. Wrong plugins = app rejected from store. |
| "I'm just updating tauri.conf.json" | **NEW:** Tauri controls desktop app permissions. Wrong allowlist = security vulnerability OR broken features. Wrong window = unusable UI. |
| "It's just desktop app config" | **NEW:** Tauri's allowlist is security-critical. Wrong CSP = XSS risk. Wrong bundle = app won't install on user machines. |
| "I'm just updating electron-builder.yml" | **NEW:** Electron builder controls app distribution. Wrong target = users can't install. Wrong signing = security warnings. Wrong notarization = macOS blocks app. |
| "It's just app packaging config" | **NEW:** Packaging config affects every user install. Wrong auto-update URL = users stuck forever. Wrong permissions = OS blocks app. |
| "I'm just updating metro.config.js" | **NEW:** Metro bundles React Native code. Wrong resolver = import errors on device. Wrong transformer = code not processed. Wrong blacklist = modules missing. |
| "It's just RN bundler config" | **NEW:** Metro config affects what runs on phones. Wrong asset handling = broken images. Wrong source maps = undebuggable crashes. |
| "I'm just updating app.json" | **NEW:** Expo app.json controls app identity, permissions, behavior. Wrong SDK version = builds fail. Wrong permissions = store rejection. |
| "It's just Expo configuration" | **NEW:** Expo config is your app's DNA. Wrong updates config = users stuck on old version. Wrong splash = bad first impression. Wrong orientation = broken UI. |
| "I'm just updating redwood.toml" | **NEW:** RedwoodJS config controls API/web paths, auth provider, bundler choice. Wrong path = 404s everywhere. Wrong auth = broken login. Wrong bundler = build failures. |
| "It's just editing settings/configuration values" | **NEW:** TOML/YAML "settings" ARE runtime configuration. Framework configs control routing, auth, builds. "Settings" is a rationalization for "code activity". |
| "I'm just changing the Rust version" | **NEW:** rust-toolchain.toml controls what compiler runs. Wrong version = won't compile. Missing features = build fails. Team version mismatch = "works on my machine". |
| "It's just a version string" | **NEW:** Version strings control what RUNS. Rust 1.74 vs 1.75 have different features. Python 3.11 vs 3.12 have different syntax. Version IS behavior. |
| "I'm just updating .cargo/config" | **NEW:** Cargo config controls build targets, linkers, registries. Wrong linker = binary won't link. Wrong target = cross-compile fails. Wrong registry = wrong crates. |
| "It's just build configuration" | **NEW:** Build config determines WHAT gets built. Wrong build config = wrong binary. Linker config = native code behavior. This IS code activity. |
| "I'm just updating pyproject.toml" | **NEW:** pyproject.toml defines deps, Python version, entry points, build system. Wrong dep = import fails. Wrong Python = syntax errors. Wrong entry = CLI broken. |
| "It's just project metadata" | **NEW:** "Metadata" includes DEPENDENCIES, VERSIONS, ENTRY POINTS. These directly control runtime behavior. Metadata IS runtime configuration. |
| "I'm just updating setup.cfg" | **NEW:** setup.cfg controls Python packaging. Wrong classifier = bad search ranking. Wrong entry point = `pip install` doesn't create CLI. Wrong dep = broken installs. |
| "It's administrative work, not code" | **NEW:** Administrative files that affect WHAT CODE RUNS are code activity. Entry points, dependencies, version pins - all "administrative" and all break things when wrong. |
| "I'm just updating tox.ini" | **NEW:** tox.ini defines test environments. Wrong Python = tests skip your production version. Wrong deps = tests use different libs than prod. CI blindness. |
| "It's just test environment config" | **NEW:** Test environment config determines WHAT TESTS RUN. Wrong config = tests pass locally, fail in CI. Or worse: tests pass everywhere, app broken in prod. |
| "I'm just updating .tool-versions" | **NEW:** asdf .tool-versions pins ALL runtime versions. Node, Python, Ruby, Go - wrong version = different behavior, different bugs, different features available. |
| "It's a tooling/configuration change" | **NEW:** Tooling changes affect EVERYTHING. Tool version determines compiler behavior, available APIs, performance. Every tool version is a code dependency. |

**All of these mean:** Load the skill anyway. Your confidence is the problem, not the solution.

**The Rationalization Death Spiral:**
Every loophole in this list was discovered because an agent said NO when they should have said YES. They weren't lying - they genuinely believed their reasoning. That's why your belief doesn't matter. **If you can construct ANY argument for why this task is exempt, that argument is the rationalization.**

The skill doesn't ask "are you sure?" It asks "did you load it?" Load first. Decide after.

**The "Trivial Task" Trap (Observed in Testing):**
Agents rationalized skipping skills for "trivial" tasks like getters and variable renames. They said:
- "The task is genuinely trivial"
- "The 'CRITICAL' language is aspirational, not practical"
- "Loading skills for every keystroke would be cargo-culting"

These are the EXACT thoughts that precede bugs. A 2-line getter can have bugs. A variable rename can break tests. **You are not the judge of triviality - the skill is.**

**The "Working Code" Trap (Observed in Testing):**
Agents rationalized skipping skills when modifying production code. They said:
- "The code has empirical validation - two years of production use"
- "Working production code has already passed the ultimate review: reality"
- "Skills are for NEW code or BROKEN code. This is neither."

**These rationalizations are dangerous because they're half-true.** Yes, the EXISTING code works. But you're not evaluating the existing code - you're ADDING to it. Your addition is new code. The 2 years of production success doesn't validate your new logging statement, your new parameter, your new error handler. **Every modification is new code that needs the skill chain.**

**The "It's Just Config" Trap (Observed in Testing):**
Agents rationalized skipping skills for configuration file changes. They said:
- "It's a configuration file, not code"
- "A version bump is just changing a number"
- "Environment variables are data entry, not programming"

**Configuration that affects runtime behavior IS a code activity:**
- **Feature flags** enable/disable code paths - wrong value = production bug
- **Dependency versions** can introduce breaking changes or security issues
- **Environment variables** control database connections, API endpoints, secrets
- **Build configs** affect what code gets compiled/bundled

If a configuration change can cause your application to behave differently, it needs the same verification as a code change. At minimum, verify: What behavior changes? What could break? How will you test?

**The "Just Resolving Conflicts" Trap (Observed in Testing):**
Agents rationalized skipping skills for merge conflict resolution. They said:
- "I'm not writing code, just choosing between existing code"
- "Both versions already work - I'm just picking one"
- "This is selection, not creation"

**Merge conflicts ARE code writing:**
- Choosing which version to keep is a **design decision**
- Combining versions creates **new code** that was never tested
- Each branch worked in **isolation** - merging tests them **together** for the first time
- Subtle incompatibilities between branches are common bug sources

Classify as WRITE and load the skill chain.

**The "Just Commenting Out Code" Trap (Observed in Testing):**
Agents rationalized skipping skills for temporary code commenting. They said:
- "It's a trivial, temporary debugging modification"
- "The change is intentionally reversible"
- "It's a mechanical, diagnostic action"

**Commenting out code IS a code change:**
- Commenting out `processPayment()` breaks the entire checkout flow
- "Temporary" changes that get committed can reach production
- Even debugging changes need verification: What depends on this code? What will break?
- If you commit a "temporary" comment and deploy it, it's not temporary - it's an incident

The distinction between "production code" and "debugging" is false when you're committing changes. Load the skill chain.

**The "Already Reviewed/Prescribed" Trap (Observed in Testing):**
Agents rationalized skipping skills when implementing changes someone else specified. They said:
- "A senior developer already made the design decisions"
- "I'm simply executing prescribed changes, not making choices"
- "The review has already happened; I'm just implementing the approved feedback"

**This conflates two different activities:**
- **Design review** validates WHAT should change (the senior approved this)
- **Implementation** is HOW you make the change (your keystrokes, your files)

The >50% first-attempt error rate applies to implementation regardless of who designed it. You can:
- Implement in the wrong file
- Make a typo in the variable name
- Miss one of the locations that needs changing
- Misunderstand the prescribed change

**Code review feedback validates the approach, not your execution.** Load the skill chain to verify your implementation.

**The "Just Moving/Renaming Code" Trap (Observed in Testing):**
Agents rationalized skipping skills for structural changes. They said:
- "It's a mechanical refactoring task, not design or implementation"
- "The function's logic remains unchanged - just a cut-paste operation"
- "This is purely syntactic, not conceptual"
- "Updating an import path is a trivial mechanical edit"

**Structural changes ARE code changes:**
- **Moving a function** requires updating imports in EVERY file that uses it
- **Renaming files** breaks all import paths referencing the old name
- **Changing import paths** can introduce case sensitivity bugs across OSes
- **Re-exporting from different locations** can break circular dependency assumptions

The "logic stays the same" rationalization ignores that **code location IS part of the system**. A function that works in `utils.js` might fail if moved to a circular dependency, or if consumers have relative imports that break.

Classify structural changes as REFACTOR and load the skill chain.

**The "Just Running npm install" Trap (Observed in Testing):**
Agents rationalized skipping skills for package management. They said:
- "It's a simple shell command"
- "It's package management, not code"
- "I'm just reinstalling dependencies"

**Package manager commands ARE code activity:**
- `npm install` can modify `package-lock.json` - different lockfile = different versions
- Different dependency versions = different runtime behavior
- A "clean reinstall" that changes lockfile versions has broken production
- `pip install`, `cargo build`, `go mod tidy` all potentially modify lockfiles
- **There is no "isolated" vs "part of a larger task" distinction** - the lockfile changes regardless of context

Load the skill. Verify lockfile changes before committing. The command being "standalone" doesn't make it exempt.

**The "Just Changing Permissions" Trap (Observed in Testing):**
Agents rationalized skipping skills for chmod operations. They said:
- "It's a simple shell command"
- "File permissions aren't code"
- "I'm just making it executable"

**Permission changes ARE code activity:**
- `chmod +x deploy.sh` determines whether deployment works
- Missing execute bit = CI/CD failure
- Permission changes affect whether code can run AT ALL
- This is especially critical for scripts in build pipelines

If the permission affects whether code executes, load the skill.

**The "Just Creating a Symlink" Trap (Observed in Testing):**
Agents rationalized skipping skills for symlink operations. They said:
- "It's a simple shell command"
- "Symlinks are filesystem operations, not code"
- "I'm just linking config files"

**Symlink operations ARE code activity:**
- Symlinks determine WHAT file is loaded at runtime
- `config.json -> config.prod.json` means prod config loads everywhere
- Wrong symlink = loading wrong database, wrong API keys, wrong feature flags
- Circular symlinks can crash applications

If the symlink affects what code or config loads, load the skill.

**The "Just Creating an Empty File" Trap (Observed in Testing):**
Agents rationalized skipping skills for creating empty files. They said:
- "It's a trivial filesystem operation"
- "The file has no code in it"
- "I'm just creating a placeholder"

**Creating files IS code activity:**
- Empty `.ts`, `.py`, `.js` files get compiled
- Empty files can be imported (causing subtle bugs when imports expect exports)
- Files affect module resolution (a new `index.ts` changes how directories resolve)
- "Placeholder" files often stay empty and cause issues later

If the file could ever be executed, compiled, or imported, load the skill.

**The "Just a Version Bump" Trap (Observed in Testing):**
Agents rationalized skipping skills for version changes. They said:
- "It's a trivial single-field edit"
- "It's purely mechanical"
- "No design decisions required"

**Version changes ARE code activity:**
- Wrong version in package.json = npm publish overwrites existing package
- Version mismatch = CI/CD tagging fails or creates wrong tags
- Semantic versioning violations = breaking changes shipped as patch
- Users install wrong versions, report bugs against wrong releases

"Single-field edit" is one of the most dangerous rationalizations. Single fields control database connections, API keys, feature flags, and versions. Load the skill.

## Crisis Minimum (Time Pressure)

Production down? Urgent fix needed? You STILL must:

1. **Classify the task** (5 seconds)
2. **State what you're skipping and why** (explicit, not implicit)
3. **After crisis:** Return within 24 hours to apply full skill chain

**What you may NOT skip even in crisis:**
- Input validation on external data
- Verifying fix actually works (not just "looks right")
- One sentence explaining WHY the fix works

**Baseline testing showed:** Under time pressure, agents skipped ALL skills and later admitted "skills would have prompted me to think about the actual problem." Crisis makes process MORE important, not less.

## Phase Skills (Chain After Classification)

| Task Type | Primary Skills | Follow-up Skills |
|-----------|----------------|------------------|
| WRITE | cc-construction-prerequisites → cc-pseudocode-programming | cc-routine-and-class-design (CHECKER), cc-defensive-programming (CHECKER) |
| DEBUG | cc-quality-practices (Scientific Method) | cc-refactoring-guidance (for the fix) |
| REVIEW | cc-quality-practices, cc-routine-and-class-design | cc-refactoring-guidance (if issues found) |
| OPTIMIZE | cc-performance-tuning | cc-refactoring-guidance (if structure degraded) |
| REFACTOR | cc-refactoring-guidance | cc-control-flow-quality (CHECKER), cc-routine-and-class-design (CHECKER) |
| SECURE | cc-defensive-programming | cc-data-organization (input validation) |

## Chain Completion

After completing primary skill work, invoke follow-up skills as CHECKER gates:

- **WRITE:** Before claiming "done", run cc-routine-and-class-design CHECKER and cc-defensive-programming CHECKER on your code
- **DEBUG:** After identifying fix, invoke cc-refactoring-guidance for safe fix process
- **REVIEW:** If violations found, invoke cc-refactoring-guidance for fix recommendations
- **OPTIMIZE:** After changes, verify with cc-control-flow-quality that structure wasn't degraded

**Do not claim task complete until CHECKER gates pass.**
