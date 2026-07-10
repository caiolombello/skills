---
name: terraform-iac-expert
description: Use when writing or reviewing Terraform/OpenTofu (.tf, modules, state), designing module APIs, remote state, or Terraform CI/governance (fmt, validate, tflint, policy-as-code).
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
