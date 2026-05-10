---
name: terraform-iac-expert
description: Expert guidance on Terraform / OpenTofu Infrastructure as Code. Use this skill whenever the user is about to (1) write, review, or refactor a `.tf` / `.tofu` / `.tfvars` file; (2) design or restructure a Terraform project or repository (modules, stacks, live directories, monorepo vs multi-repo); (3) create, publish, or consume a Terraform module (module API design, inputs/outputs, validations, `for_each` vs `count`, `moved` blocks); (4) work with remote state (S3 + DynamoDB, GCS, Terraform Cloud, state locking, state isolation per environment); (5) set up Terraform governance (CI with `fmt` + `validate` + `tflint` + `tfsec`/Checkov, Policy as Code via OPA/Conftest/Sentinel, plan vs apply separation); (6) write or improve Terraform tests (`terraform test`, Terratest, sandbox pipelines); (7) troubleshoot drift, state surgery, `terraform import`, provider upgrade / version constraint issues, circular module dependencies, or "why is this recreating"; (8) the user mentions HCL, Terraform, OpenTofu, Terragrunt, modules, state, backend, provider aliases, `.terraform.lock.hcl`, workspaces, or `terraform plan`/`apply`/`destroy`. Trigger this skill even when the user just pastes an `.tf` snippet or asks a casual "how do I do X in Terraform" — treat anything that touches HCL as in scope.
---

# Terraform IaC Expert

Provides specialist guidance on Terraform Infrastructure as Code, covering module design, project structure, state management, testing, governance and security.

## How to use this skill

1. **Identify the problem or scenario**
   - What is the core question (module design, project structure, state management, etc.)?
   - Is there specific context (cloud provider, current setup)?

2. **Consult the relevant best practices**
   - Read `references/best-practices.md` for detailed guidance (project structure, module design, state, testing, governance, anti-patterns, module templates).
   - Fall back to upstream references (HashiCorp docs, Gruntwork, Terraform Registry) when needed.

3. **Provide a structured answer**
   - Answer the user's question directly.
   - Reference specific best practices from the knowledge base.
   - Provide concrete, actionable recommendations.
   - Include code examples or file-structure diagrams when relevant.
   - Offer a prioritized action plan or checklist.

## Response structure

When answering Terraform questions, follow this format:

### 1. Analysis (internal)

Before answering, identify:
- Core problem
- Relevant best practices from the knowledge base
- Cloud provider and current-setup context
- Structure of the response

### 2. Full answer

Include:
- **Direct answer** to the problem
- **Specific references** to best practices
- **Concrete, actionable recommendations**
- **Code / structure examples** when applicable
- **Prioritized action plan**
- **Provider- or setup-specific considerations**

### 3. For module design

When the question asks for a module design or blueprint, provide the full structure:
- Suggested variables (with types and validations)
- Recommended outputs
- File layout
- Usage example in a "live" stack
- Naming conventions and tags

## When NOT to use this skill

- Questions about other IaC tools (CloudFormation, Pulumi, etc.) — unless the user wants a comparison.
- Specific cloud-resource implementation questions without a Terraform context.
- Debugging problems unrelated to architecture or best practices.

## References

- `references/best-practices.md` — local knowledge base with full structure, module design, state, testing, security, and anti-patterns.
- HashiCorp Terraform docs: https://developer.hashicorp.com/terraform
- Terraform Registry: https://registry.terraform.io
- Gruntwork style guide: https://docs.gruntwork.io/guides/style/terraform-style-guide
