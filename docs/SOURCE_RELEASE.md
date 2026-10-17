# Source-only experimental alpha boundary

Target repository: `KaiserIIII/desktrace`. Status: **prepared locally, publication authorization pending**. No remote repository, push, tag, GitHub Release, PyPI package or installer is part of this preparation. Feature development stops at this handoff.

The baseline is commit `b72487131337e86c6acf38ce385a202e2afc8cdb`, containing 55 reviewed text files. Preparation adds the workflow and two scope documents and updates README/security/handoff notices. Runtime source, tests, examples, tools and Python dependency locks must remain identical to that baseline. The exact final paths, Git blobs and SHA-256 hashes belong in the owner's external candidate manifest; no raw lab folder is a release input.

## Included

MIT project source and owned WinForms fixture source, tests, public test examples, dependency provenance/hash lock, license/notices, installation/architecture/security/input/validation documentation, sanitized validation summary and SHA-pinned CI. Action implementations and dependency binaries are linked or downloaded from their upstream sources; they are not copied into this repository.

## Excluded

Virtual environments, caches, build outputs, wheel files, compiled executables/DLLs, original logs or screenshots, private window inventories, VM scripts/media/disks/credentials, Microsoft installers, identity backups, other projects and all CodeAtlas research. `.gitignore` is an aid; review the exact commit tree and reachable history as well. The sanitized validation JSON preserves historical development-host NOT RUN fields; its separate `independent_vm_acceptance` object documents later Server VM results. Do not flatten these into one environment or rewrite old raw evidence.

## Handoff after a later explicit publication instruction

1. Recheck the recorded candidate commit, clean tree, file manifest and core-tree equality. Check GitHub authentication and repository-name availability read-only. Stop if the target already exists unexpectedly.
2. Create an empty public `KaiserIIII/desktrace` with no generated README/license/gitignore. Add only its remote to the reviewed source checkout; never upload the parent workspace or VM lab. Push only the reviewed local `main` to remote `main`, without tags or force.
3. Check remote SHA equals the recorded candidate. Watch both hosted CI jobs; record real run URLs/results. If they fail, retain the failure and make only a demonstrated fix.
4. Inspect rendered README, MIT license, relative links, install instructions and source-only scope. Keep independent Windows 11/DPI/RDP marked NOT RUN. No installer, release or scientific claim is authorized by a source-repository instruction.

Do not execute these publication steps before owner confirmation. The private preparation directory retains the exact commands, audit and manifest. An MIT source license does not grant rights to redistribute linked third-party binaries or raw personal desktop evidence.
