# Laboratorio: Docker, Terraform, IAM ed ECS

## 1. Obiettivo e prerequisiti

Distribuire l'API del capstone come container su ECS/Fargate usando Terraform.

- **Terraform:** strumento Infrastructure as Code che confronta configurazione
  dichiarata e stato reale, producendo un piano di modifiche.
- **ECS:** orchestratore container AWS.
- **Fargate:** capacità serverless per eseguire task ECS senza gestire istanze.
- **ECR:** registry di immagini.
- **task definition:** specifica immagine, CPU, memoria, porte, log e ruoli.
- **task:** istanza della task definition.
- **service:** mantiene il numero desiderato di task e gestisce rollout.

Il laboratorio assume VPC, subnet private e target group ALB già creati da un modulo
di networking separato. Separare networking e servizio riduce lo scope, ma gli input
restano espliciti.

## 2. Dockerfile

```dockerfile
FROM python:3.12-slim AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /build
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

FROM python:3.12-slim AS runtime
RUN useradd --create-home --uid 10001 appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED="1"
USER appuser
EXPOSE 8080
CMD ["uvicorn", "ai_ops.api.app:app", "--host=0.0.0.0", "--port=8080"]
```

Build e test:

```powershell
docker build --tag ai-ops:local .
docker run --rm --publish 8080:8080 --read-only --tmpfs /tmp ai-ops:local
curl http://localhost:8080/health/live
```

Usa un digest immutabile nel deploy:

```text
ACCOUNT.dkr.ecr.REGION.amazonaws.com/ai-ops@sha256:...
```

## 3. Struttura Terraform

```text
infra/
  versions.tf
  variables.tf
  iam.tf
  ecs.tf
  outputs.tf
  environments/
    staging.tfvars
```

Non committare `terraform.tfstate`: può contenere dati sensibili. In team usa backend
remoto S3 con versioning, cifratura e locking.

## 4. Provider e variabili

```hcl
terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ai-ops"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region"            { type = string }
variable "environment"           { type = string }
variable "image_uri"             { type = string }
variable "private_subnet_ids"    { type = list(string) }
variable "service_security_group" { type = string }
variable "target_group_arn"      { type = string }
variable "knowledge_bucket_arn"  { type = string }
variable "provider_secret_arn"   { type = string }
```

In CI valida che `image_uri` contenga `@sha256:` invece di un tag mutabile.

## 5. Due ruoli distinti

Il **execution role** viene usato da ECS per avviare il task, leggere secret
referenziati e inviare log. Il **task role** viene assunto dall'applicazione per
accedere a S3 o altri servizi. Non confonderli.

```hcl
data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "ai-ops-${var.environment}-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "execution_managed" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "execution_secret" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [var.provider_secret_arn]
  }
}

resource "aws_iam_role_policy" "execution_secret" {
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.execution_secret.json
}

resource "aws_iam_role" "task" {
  name               = "ai-ops-${var.environment}-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

data "aws_iam_policy_document" "task" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${var.knowledge_bucket_arn}/approved/*"]
  }
}

resource "aws_iam_role_policy" "task" {
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.task.json
}
```

La policy non concede `s3:*`, non usa resource `*` e non consente scrittura. Aggiungi
permessi solo quando un acceptance test li richiede.

## 6. Cluster, log e task definition

```hcl
resource "aws_ecs_cluster" "main" {
  name = "ai-ops-${var.environment}"
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/ai-ops/${var.environment}"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "api" {
  family                   = "ai-ops-${var.environment}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name      = "api"
    image     = var.image_uri
    essential = true
    readonlyRootFilesystem = true
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "LOG_LEVEL", value = "INFO" }
    ]
    secrets = [{
      name      = "OPENAI_API_KEY"
      valueFrom = var.provider_secret_arn
    }]
    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/health/live')\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 20
    }
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "api"
      }
    }
  }])
}
```

CPU e memoria sono una baseline da load testare. Il secret viene risolto dal runtime,
non incluso nell'immagine o nel file `.tfvars`.

## 7. Service

```hcl
resource "aws_ecs_service" "api" {
  name            = "ai-ops-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 30

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.service_security_group]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = 8080
  }
}
```

Le subnet private richiedono egress controllato verso provider esterni, tramite NAT o
proxy/VPC endpoint quando disponibile. Il security group accetta traffico solo
dall'ALB.

## 8. Workflow

```text
terraform fmt -check
terraform init
terraform validate
terraform plan -var-file=environments/staging.tfvars
review del plan
terraform apply del plan approvato
smoke test
canary/monitor
```

In produzione separa account/ruoli e richiedi approval. `terraform apply` non sostituisce
quality gate applicativo e rollback.

## 9. Acceptance test infrastrutturali

- task eseguito come UID non-root;
- filesystem root read-only;
- immagine referenziata per digest;
- secret assente da image, log, state e plan;
- task role non può leggere path S3 di un altro tenant;
- porta task accessibile solo da ALB;
- health check fallito impedisce il rollout;
- due task distribuiti su Availability Zone quando richiesto;
- log retention definita;
- rollback alla task definition precedente provato.

## 10. Costo e cleanup

Stima separatamente Fargate, ALB, NAT, log, data transfer, storage e provider LLM.
In ambienti lab, NAT e ALB possono costare più del container.

Non creare risorse cloud solo per spuntare una casella. È accettabile consegnare:

1. `terraform validate` e plan revisionato;
2. diagramma e threat model;
3. deploy temporaneo con screenshot/metriche;
4. `terraform destroy` verificato;
5. costo mensile stimato.
