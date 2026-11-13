# Domain: native code, binaries, and local apps

Load the part whose boundary reconnaissance found:

- **Part A** — untrusted bytes in memory-unsafe or privileged code: C, C++, Objective-C, unsafe Rust, FFI, kernel modules and drivers, parsers and decoders, network daemons, firmware, loaders, runtimes, JITs.
- **Part B** — desktop and mobile apps, privileged helpers, updaters, local daemons, webview hosts, deep-link handlers, native-messaging hosts, local IPC.

Bold names and headings are ledger block identifiers.

## Part A — memory safety and binaries

### Native discipline

```text
- Re-derive every bound and lifetime from attacker-controlled input and all callers.
  Check the worst accepted case, not a typical test vector.
- A panic, sanitizer report, or crash proves a defect only when realistic untrusted
  input reaches it. Do not infer memory corruption, code execution, or shared outage
  from a label.
- Validate with the narrowest harness: sanitizers, deterministic concurrency tests,
  existing fuzz targets, debugger classification. Stop at the violated invariant; do
  not develop post-corruption techniques.
- Assembly, JIT code, custom allocators, intra-object accesses, and foreign libraries
  can escape sanitizers; note which operations were actually instrumented.
- For each parser or FFI boundary, tabulate accepted length and type, checked
  representation, allocation owner, consumer, thread, and teardown. Audit duplicated
  paths: a check in one caller, architecture, role, or feature flag does not protect
  its siblings.
```

**Out-of-bounds read or write** — a length, offset, index, or terminator reaches a buffer without a correct bound; recompute headroom after prefixes, alignment, padding, and terminators, on both source and destination.

**Integer overflow, underflow, truncation, and signedness** — attacker arithmetic before allocation, copy, loop, or indexing: `a - b` with `b > a`, `count * size`, additions near the maximum, negative to unsigned, 64-to-32-bit narrowing, `-1` sentinels becoming sizes.

**Unit and pointer-depth confusion** — bytes versus elements, code units, pages, words, or wire units mixed between parse, check, allocation, and copy. A bounds check in the same wrong unit is still wrong.

**Uninitialized or partially initialized data** — buffers, padding, or fields returned, hashed, serialized, or sent across a boundary before initialization, with an observable consumer.

**Use-after-free, stale view, and double free** — owners released while callbacks, waiters, timers, iterators, borrowed slices, or cached pointers remain; check every error, cancel, close, and realloc path.

**Type confusion and invalid downcast** — a tag, vtable, discriminator, or handle checked differently from the representation later read; stale tags after reuse.

**Reference-count and ownership races** — non-atomic retain/release or unlocked use after a check frees or mutates an object during access.

**Shared-state races and TOCTOU** — concurrent streams, global caches, lazy init, signal handlers, or teardown invalidate earlier bounds, policy, or pointers. Needs a repeatable schedule or sanitizer trace; a hypothetical interleaving stays `needs_validation`.

**Lock-order, deadlock, and starvation** — inconsistent lock order or locks held across callbacks and blocking I/O; an availability issue only when bounded input stops shared progress.

**Pointer-length and ownership contract mismatch** — caller and callee disagree on who allocates, frees, pins, or mutates, on pointer lifetime, or on bytes versus elements, across `extern`, CGo, JNI, Python, or generated bindings.

**Layout, alignment, and enum disagreement** — struct, bitfield, packing, callback signature, integer width, enum, or calling convention differs by architecture or flag. In-repo mismatches are locally confirmable; opaque foreign code is `needs_validation`.

**Unwind, exception, and thread-affinity violations** — panics or exceptions crossing a no-unwind ABI, callbacks after teardown, or single-thread APIs called elsewhere.

**Library, plugin, and executable search-order trust** — a privileged process loads code from a path a less-trusted principal can write, or resolves a bare name through attacker-influenced working directory or environment. Users loading their own plugins into their own process is not a boundary.

**Missing artifact identity or signature binding** — the loader verifies one file or record but maps a different image through path resolution, replacement, architecture slices, or embedded resources.

**Malformed binary metadata and relocation handling** — offsets, counts, sections, relocations, symbols, or bytecode trusted before range and overlap checks; separate corruption from safe rejection.

**JIT and generated-code consistency** — validator, interpreter, optimizer, and generated code disagree on types, bounds, side effects, or lifetime; confirm a process-integrity effect.

**Unload, reload, and teardown safety** — function pointers, callbacks, threads, or views survive module unload or runtime reset.

**User-copy bounds and repeated reads** — a syscall, ioctl, or driver derives a fact from user memory and reads the same mutable address again; size, direction, and access checks at each copy.

**Privileged object lifecycle and dispatch consistency** — unbalanced retain/release, teardown without draining observers, unchecked selector or table indices, compatibility paths missing a guard.

**Under-authorized powerful interfaces** — a device node, admin socket, or management API validates shape but not the caller's authority over the resource; external permissions make it `needs_validation`.

### Native validation

1. Establish a realistic untrusted entry and the exact operation that violates a bounds, type, lifetime, ABI, concurrency, loader, or authority invariant.
2. Classify the observed effect precisely — invalid read, invalid write, stale alias, wrong object, uninitialized output, unauthorized image load, deadlock, safe termination — and claim nothing stronger.
3. Reproduce with the narrowest sandboxed harness, test, sanitizer, or fuzzer; confirm the faulting operation was instrumented; record architecture and build flags.
4. Concurrency needs a deterministic schedule or sanitizer trace. Loader claims prove the checked identity differs from the mapped one and name the lower-trust writer.

## Part B — desktop, mobile, and local IPC

### Local app discipline

```text
- State the realistic attacker: another app, another OS user, a sandboxed child, an
  untrusted document, or a remote origin. Same-account self-harm is not a boundary.
- Paths, process names, bundle or package IDs, and claimed sender fields are not peer
  authentication. Use OS peer credentials, code identity, capability handles, or
  protected channel state.
- A native bridge or helper authorizes each operation and final resource after
  parsing; a trusted UI does not make its arguments trusted.
- OS sandbox, signing, entitlements, permissions, keychain ACLs, exported-component
  policy, and consent prompts are real controls when pinned and visible.
- Enumerate every process, component, local endpoint, URI scheme, file association,
  webview origin, and helper with its OS identity and callable operations. Read final
  packaging inputs (merged manifest, entitlements, installer rules) — declarations can
  be overridden downstream.
```

**Custom-scheme and deep-link ambiguity** — another app or page invokes a route that mutates state, imports data, completes authentication, or picks an account without current-session and one-time binding.

**App and account handoff confusion** — OAuth, SSO, magic-link, invite, pairing, or payment callbacks return to the wrong app, profile, tenant, or pending transaction.

**File-open and intent authority confusion** — associated files, share intents, drag and drop, clipboard, notification actions, or open-file events trigger privileged operations without checking content, sender, user intent, and target.

**Navigation-origin to bridge confusion** — remote or attacker frames reach a native bridge meant for packaged content; origin must be checked at call time, after every navigation, redirect, subframe, popup, and error page.

**Over-broad native bridge capabilities** — web content selects arbitrary files, commands, IPC methods, credentials, or system actions through a generic bridge.

**Webview file and universal access** — remote content reads app-local files, privileged schemes, or internal origins through file access, universal access, mixed content, debug interfaces, or custom protocol handlers.

**IPC peer-authentication gaps** — Unix sockets, named pipes, XPC, Binder, D-Bus, native messaging, shared memory, or loopback listeners accept a lower-trust peer without checking OS credentials or code identity, with a meaningful method behind them.

**Claimed principal versus channel identity** — the channel belongs to one user or app but request fields select another user, profile, or capability.

**Exported service, activity, receiver, or provider overreach** — a mobile component or local automation endpoint is externally invokable and performs an app-internal operation; check merged manifests, intent filters, permission levels, and aliases.

**IPC lifecycle and correlation confusion** — predictable request IDs, reused handles, stale channels, inherited descriptors, world-writable socket paths, or restart behavior let one peer answer or reuse another's operation.

**Privileged helper as confused deputy** — a low-privilege caller selects a privileged command, file, service, user, or setting without per-operation authorization (sudo, polkit, UAC, XPC helper rules).

**Install, update, and repair path trust** — a privileged installer reads manifests, scripts, packages, symlinks, or working directories writable by a lower-trust actor after authorization.

**Local file ownership and TOCTOU** — a privileged path is checked, then replaced via symlink, mount, or case/normalization change before use.

**Credential-store and local-secret boundary mismatch** — keychain items, token files, backups, logs, clipboard, or notification previews readable by another app, profile, or user with less authority. Plaintext readable only by the same intended account is not automatically a finding.

**Account switch, logout, and device restore leakage** — caches, background tasks, widgets, notifications, local databases, webview storage, or biometric approvals survive logout or account change.

**Pending-action and user-presence confusion** — a notification, widget, shortcut, share sheet, biometric prompt, or deferred action authorizes something other than what was shown, after expiry, or for another profile.

### Local app validation

1. Name the attacker's starting capability, the OS or app principal crossed, the entry channel, the accepted argument or state, and the unauthorized operation or disclosure.
2. Confirm which sandbox, peer-credential, signing, entitlement, permission, consent, and installer controls apply; unknown packaging, OS version, or device policy makes it `needs_validation`.
3. Bridges: cite the navigation/origin control and the privileged native sink. IPC: cite peer authentication and per-resource authorization. Helpers: verify the final normalized destination.
4. Use dummy profiles and non-sensitive fixtures on an isolated machine or emulator; stop at the boundary result, with no persistence or wider system modification.
