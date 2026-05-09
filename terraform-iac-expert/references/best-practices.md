# Terraform IaC Best Practices — Knowledge Base

## Index

1. [Project Structure and Patterns](#project-structure-and-patterns)
2. [State, Backend and Security](#state-backend-and-security)
3. [Provider, Versions and Reproducibility](#provider-versions-and-reproducibility)
4. [Conventions (Naming, Tags, Patterns)](#conventions-naming-tags-patterns)
5. [Code Quality and Maintenance](#code-quality-and-maintenance)
6. [Pipeline, Review and Policies](#pipeline-review-and-policies)
7. [Testing](#testing)
8. [Safe Changes](#safe-changes)
9. [Operational Best Practices](#operational-best-practices)
10. [Common Anti-patterns](#common-anti-patterns)
11. [Golden Rules for Module Creation](#golden-rules-for-module-creation)
12. [Standard Module Structure](#standard-module-structure)
13. [Specific Best Practices](#specific-best-practices)
14. [Module Documentation](#module-documentation)
15. [Module Testing](#module-testing)

---

## Project Structure and Patterns

### Define a repository pattern and stick to it

Either of these two models works well:

1. **Monorepo**:
   ```
   /modules
   /envs/{dev,stg,prd}
   /live
   ```

2. **Separate repos**:
   - One repository per module
   - Separate repository (or repositories) for "live" (stacks per environment)

**Rule**: modules are reusable; "live" only orchestrates.

### Separate "module" from "stack"

- **Module**: creates resources (VPC, EKS, IAM, etc.)
- **Stack**: calls modules, defines `providers`, `backend`, `tfvars`, dependencies

Avoid complex logic inside a "stack"; push it into the module when it makes sense.

### Well-defined module API

- Minimal, explicit inputs
- Only the outputs that are really needed
- Document invariants: naming, tags, regions, limits

### Avoid contortions with count / for_each

- Use `for_each` for collections
- `count` only when the toggle is really binary
- Prefer **smaller modules** over one mega-module stuffed with flags

---

## State, Backend and Security

### Remote state is mandatory

Requirements:
- State locking (avoid concurrent writes)
- Encryption at rest
- Minimal access control (RBAC)

### Never version secrets

- No secrets in `*.tfvars`, `*.tfstate`, or outputs without `sensitive = true`
- Integrate with Vault / SSM / Secrets Manager
- Use data sources carefully

### Per-environment isolation

- Separate state per `dev/stg/prd` (and often per stack)
- Reduces blast radius and makes rollback easier

---

## Provider, Versions and Reproducibility

### Pin versions

- `required_version` for Terraform
- `required_providers` with constraints
- Commit `.terraform.lock.hcl` for reproducibility

### Avoid dependency on the "default provider config"

- Parameterize region / account / project explicitly
- Use provider `alias` for multi-account / multi-region setups

---

## Conventions (Naming, Tags, Patterns)

### Predictable naming

- Prefix by organization / product / environment: `org-app-env-*`
- Standardize `locals` for common names and tags

Example:
```hcl
locals {
  name_prefix = "${var.org}-${var.app}-${var.env}"
  common_tags = {
    Environment  = var.env
    Application  = var.app
    ManagedBy    = "terraform"
    Owner        = var.owner
    CostCenter   = var.cost_center
  }
}
```

### Mandatory tags

Recommended minimum:
- `owner`
- `cost_center`
- `env`
- `app`
- `managed_by=terraform`
- `data_classification`

Validate: if any required tag is missing, fail.

---

## Code Quality and Maintenance

### Organize code by intent

```
locals.tf       # constants, tags, names
variables.tf    # inputs
outputs.tf      # outputs
main.tf         # resources
versions.tf     # providers / terraform
```

### Use locals sparingly

- Good for standardization
- Bad when it turns into an obscure "mini language"

### Validations

Use `validation` in `variables` to enforce formats, ranges, enums.

Example:
```hcl
variable "environment" {
  type        = string
  description = "Environment name"

  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "Environment must be dev, stg, or prd."
  }
}

variable "instance_size" {
  type        = string
  description = "Instance size"

  validation {
    condition     = var.environment != "prd" || !can(regex("^(micro|small)$", var.instance_size))
    error_message = "Production cannot use micro or small instances."
  }
}
```

---

## Pipeline, Review and Policies

### Standard CI for every PR

Required:
1. `terraform fmt -check`
2. `terraform validate`
3. `tflint`
4. `tfsec` (or Checkov)
5. `terraform plan` with a PR comment (plan visible and auditable)

### Clear separation: Plan vs Apply

- `apply` only on protected branches and through a controlled workflow
- Prefer human approval for `apply` in `stg` / `prd`

### Policy as Code

Use Open Policy Agent (OPA) / Conftest or Sentinel for rules like:
- "S3 without encryption fails"
- "Security group `0.0.0.0/0` on port 22 fails"
- "Resources must carry tag X"

---

## Testing

### Static testing

- lint + security scanners (`fmt`, `validate`, `tflint`, `tfsec`)

### Module testing

- Use **`terraform test`** for basic asserts
- For integration testing: Terratest (Go) or pipelines that provision into a sandbox account and tear down

### Ephemeral environments

For critical stacks, stand them up in a throwaway account/project and run smoke tests.

---

## Safe Changes

### Avoid accidental recreation

- Use `lifecycle` carefully (`prevent_destroy`) on critical resources
- Use `moved` blocks when renaming resources (avoids destroy/create)

`moved` example:
```hcl
moved {
  from = aws_instance.old_name
  to   = aws_instance.new_name
}
```

### Dependency control

- `depends_on` only when needed (not as a crutch)
- Prefer reference-based dependencies (IDs / outputs)
- **IMPORTANT**: when a module depends on another, do not use `depends_on`. The dependency is created by passing outputs of module A as inputs to module B.

Example:
```hcl
# CORRECT — dependency by reference
module "vpc" {
  source = "./modules/vpc"
  # ...
}

module "eks" {
  source     = "./modules/eks"
  vpc_id     = module.vpc.vpc_id          # implicit dependency
  subnet_ids = module.vpc.private_subnets # implicit dependency
}

# INCORRECT — do not use depends_on between modules
module "eks" {
  source     = "./modules/eks"
  vpc_id     = module.vpc.vpc_id
  depends_on = [module.vpc]  # UNNECESSARY and hides dependencies
}
```

---

## Operational Best Practices

### IaC observability

- Keep pipeline logs
- Audit who applied what (by commit SHA)

### Drift management

- Run scheduled `plan` (daily / weekly) to detect drift
- Investigate and fix any drift found

### Minimum mandatory documentation

Every module README must include:
- Purpose
- Inputs / outputs
- Examples
- Architectural decisions

---

## Common Anti-patterns

**AVOID**:

1. Local state on a developer machine
2. One "monster module" for the whole infrastructure
3. Secrets in non-sensitive variables / outputs
4. Manual `terraform apply` in production
5. Renaming a resource without `moved` (turns into destruction)
6. `ignore_changes` without justification (silently accepted drift)
7. `depends_on` between modules (use output references)
8. Hard-coded values that should be variables
9. Modules that "discover" resources via internal data sources

---

## Golden Rules for Module Creation

### 1) Have a single purpose

- A module should represent **one cohesive logical block**
  - Examples: `vpc`, `eks-cluster`, `rds-postgres`, `iam-role`, `alb`
- If the module needs 20 flags to enable/disable resources, it is doing too much
- Split into 2–5 smaller modules

### 2) Define the contract (inputs/outputs) as an API

- **Minimal inputs**: only what changes between uses
- **Sensible defaults**: reduce boilerplate
- **Validations** in `variables.tf`: format, ranges, enums, invalid combinations
- **Useful outputs**: IDs / ARNs / endpoints that consumers actually use
- Mark sensitive outputs with `sensitive = true`

### 3) Standardize naming and tags inside the module

Centralize in `locals`:
```hcl
locals {
  name_prefix = "${var.project}-${var.environment}-${var.component}"

  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "vpc"
    }
  )
}
```

Enforce mandatory tags (and fail if they are missing).

### 4) Make the module composable

Expose **extension points** without coupling:
- Accept lists / maps for rules (for example, security group rules)
- Expose outputs to connect to other modules
- Avoid hidden dependencies (for example, looking up a VPC "by name" through a data source inside the module)

### 5) Do not "hide" providers and backends inside the module

- **Provider config** and **backend** live in the stack (live), not in the module
- The module should work in any account / region that the caller configures

### 6) Iteration: prefer for_each over maps/sets

- Create multiple resources with `for_each` and stable keys (avoids state churn)
- Avoid `count` when resource identity matters

Example:
```hcl
# GOOD — stable keys
resource "aws_subnet" "private" {
  for_each = var.private_subnets  # map keyed by AZ

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr
  availability_zone = each.key

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-${each.key}"
  })
}

# BAD — count with unstable order
resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  cidr_block = var.private_subnet_cidrs[count.index]  # reordering the list = recreate
}
```

### 7) Compatibility and upgrades

- Pin `required_providers` and compatible versions in the module
- Keep changes SemVer-compatible:
  - **Breaking change**: changes types / variable / output names, or behavior that forces recreate
  - Use `moved` blocks when renaming resources

---

## Standard Module Structure

### Healthy minimum

```
modules/<name>/
├── README.md
├── versions.tf
├── main.tf
├── variables.tf
├── outputs.tf
├── locals.tf
├── examples/
│   └── basic/
│       └── main.tf
└── test/   (optional)
```

### Recommended content

**versions.tf**:
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

**variables.tf**:
- Strong types + validations
- Clear descriptions
- Defaults when applicable

**locals.tf**:
- Names / tags / constants
- Data transformations

**outputs.tf**:
- Integration contract
- Only necessary outputs
- Mark sensitive outputs accordingly

---

## Specific Best Practices

### Typed and consistent inputs

Use explicit types:

```hcl
# String, number, bool
variable "name" {
  type        = string
  description = "Resource name"
}

variable "replica_count" {
  type        = number
  description = "Number of replicas"
  default     = 1
}

variable "enable_backup" {
  type        = bool
  description = "Enable automated backups"
  default     = true
}

# Collections
variable "allowed_cidrs" {
  type        = list(string)
  description = "Allowed CIDR blocks"
  default     = []
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
  default     = {}
}

# Structured objects
variable "database_config" {
  type = object({
    instance_class    = string
    allocated_storage = number
    engine_version    = string
    backup_retention  = optional(number, 7)
  })
  description = "Database configuration"
}

# Sets for unique-value resources
variable "security_group_ids" {
  type        = set(string)
  description = "Security group IDs"
}
```

**Avoid `any`** — it becomes chaos and silently breaks consumers.

### "Feature flags" with a limit

- Up to ~3 flags is acceptable
- Beyond that, extract submodules:
  - `vpc` + `vpc_endpoints` + `vpc_flow_logs`
  - `eks` + `eks_nodegroups` + `eks_addons`

### Data sources with care

Inside the module, use `data` only when:
- It is deterministic and part of the contract (for example, fetching available AZs)

To "discover" existing resources (VPC / Subnet / SG), prefer having the caller pass IDs:

```hcl
# GOOD — the caller passes IDs explicitly
module "app" {
  source    = "./modules/app"
  vpc_id    = "vpc-123456"
  subnet_ids = ["subnet-111", "subnet-222"]
}

# BAD — module "discovers" VPC internally
# (harder to test, creates coupling, hides dependencies)
module "app" {
  source   = "./modules/app"
  vpc_name = "production-vpc"  # module looks it up via data source
}
```

### Secure by default

- Encryption enabled where possible
- Parameterized security-group rules and "deny-by-default"
- Do not open to the world (`0.0.0.0/0`) without an explicit request

Example:
```hcl
variable "allow_public_access" {
  type        = bool
  description = "Allow public internet access (0.0.0.0/0) - USE WITH CAUTION"
  default     = false

  validation {
    condition     = var.allow_public_access == false || var.environment != "prd"
    error_message = "Public access cannot be enabled in production."
  }
}
```

---

## Module Documentation

### README checklist

Every module must ship a README with:

1. **What the module creates** (list of main resources)
2. **Simple diagram** (optional but recommended)
3. **Inputs / outputs** (table)
4. **Minimal example** in `examples/basic`
5. **Important decisions** (for example, naming, tags, limits)

### README template

```markdown
# Module: VPC

Creates an AWS VPC with public and private subnets, NAT gateways and routing configuration.

## Resources created

- VPC with DNS enabled
- Public subnets (one per AZ)
- Private subnets (one per AZ)
- Internet Gateway
- NAT Gateways (one per AZ or a single shared one)
- Route tables and associations

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `vpc_cidr` | string | - | CIDR block for the VPC |
| `azs` | list(string) | - | Availability zones |
| `public_subnets` | list(string) | - | CIDRs for public subnets |
| `private_subnets` | list(string) | - | CIDRs for private subnets |
| `single_nat_gateway` | bool | false | Use a single NAT gateway |
| `tags` | map(string) | {} | Additional tags |

## Outputs

| Name | Description |
|------|-------------|
| `vpc_id` | VPC ID |
| `public_subnet_ids` | Public subnet IDs |
| `private_subnet_ids` | Private subnet IDs |
| `nat_gateway_ips` | NAT gateway public IPs |

## Usage example

```hcl
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr = "10.0.0.0/16"
  azs      = ["us-east-1a", "us-east-1b", "us-east-1c"]

  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  single_nat_gateway = false

  tags = {
    Environment = "production"
    Project     = "myapp"
  }
}
```

## Design decisions

- **NAT Gateways**: by default, one NAT gateway per AZ for high availability
- **Tags**: every subnet carries tag `Type` = `public` / `private` to ease discovery
- **Naming**: resources follow `{vpc_name}-{type}-{az}`
```

---

## Module Testing

### Static tests in CI

Required on every PR:

```bash
# Formatting
terraform fmt -check -recursive

# Validation
terraform init -backend=false
terraform validate

# Linting
tflint --init
tflint

# Security scanning
tfsec .
# or
checkov -d .
```

### Executable example

`examples/basic` should run `init` / `plan` with no tricks:

```hcl
# examples/basic/main.tf
provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "../../"

  vpc_cidr = "10.0.0.0/16"
  azs      = ["us-east-1a", "us-east-1b"]

  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

Test:
```bash
cd examples/basic
terraform init
terraform plan
```

### Integration (ideal)

Provision in a sandbox and destroy:

**Terratest** (Go):
```go
func TestVPCModule(t *testing.T) {
    opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/basic",
    })

    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)

    vpcID := terraform.Output(t, opts, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

**Smoke pipeline**:
```yaml
test-module:
  script:
    - cd examples/basic
    - terraform init
    - terraform apply -auto-approve
    - terraform output vpc_id
    - terraform destroy -auto-approve
```
