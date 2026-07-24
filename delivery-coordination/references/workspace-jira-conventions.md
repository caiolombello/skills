# Workspace Jira Conventions

Load this reference whenever coordinating or creating client-scoped work in
the company's Jira.

## DevOps board client routing

- The board is named `DevOps`.
- In WorkingOps, the conceptual `work_type`/`workType` value represents the
  client and separates client work on this board.
- Preserve both client code and display name.
- For Ana Gaming, use exactly:

```text
work_type = CL039 - Ana Gaming
```

Do not substitute a label, component, free-form client name, or guessed code
for this client routing value.

## Verify the Jira representation

The same WorkingOps `work_type` concept can be represented differently by the
underlying Jira path:

- The WorkingOps issue-create flow can resolve the Jira custom field named
  `Work Type` from the selected client.
- DevOps client boards can encode the client as the Jira issue type and filter
  with JQL such as:

```jql
issuetype = "CL039 - Ana Gaming"
```

- WorkingOps can expose either source as `workType` and use issue type as a
  fallback for client grouping.

Therefore, do not blindly set both the custom field and issue type. Inspect the
target board and an analogous valid card, then use the representation expected
by that creation path. The invariant is that WorkingOps resolves the card to
`work_type = CL039 - Ana Gaming` and shows it under Ana Gaming.

## Read-before-write procedure

Before creating or editing a client card:

1. Confirm the target is the `DevOps` board.
2. Discover the board's current project/filter instead of assuming a project
   key.
3. Determine whether the board routes clients through Jira issue type, the
   `Work Type` custom field, or the WorkingOps client-resolution flow.
4. Read a recent card for the same client and representation.
5. Confirm the exact issue type, required fields, workflow, and configured
   client option.
6. Check for an existing card covering the same outcome.
7. Draft the card and routing snapshot.
8. Apply the authorized write through
   [`atlassian-acli`](../../atlassian-acli).
9. Re-read the created/edited card and verify that it appears under the
   intended client grouping.

Use this routing snapshot before a write:

```markdown
- Board: DevOps
- Project: <discovered from board/filter>
- Issue type: <verified>
- Client: <client name>
- work_type: <exact configured code and name>
- Jira representation: <issue type | Work Type custom field | WorkingOps client resolution>
- Parent/initiative: <verified key or none>
- Priority authority: <person/policy/request>
```

For any client other than Ana Gaming, discover the exact configured
`work_type` option from field metadata or an existing valid card. If it cannot
be verified, stop and ask; never extrapolate a client code.

## Boundaries

- The board is a view over Jira data, not enough information by itself to
  infer the project, issue type, or workflow.
- `work_type` routes/classifies client work at the WorkingOps level; its Jira
  storage representation is a separate implementation detail that must be
  verified.
- Client routing does not replace the card's outcome, scope, owner, priority,
  or acceptance criteria.
- A requested client and a responsible delivery owner are separate concepts.
- A requested due date is not a delivery commitment until the accountable
  team accepts it.
