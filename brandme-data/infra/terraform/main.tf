# Copyright (c) Brand.Me, Inc. All rights reserved.
# Terraform stub for Brand.Me data infrastructure on GCP.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-east1"
}

provider "kubernetes" {
  host                   = var.gke_endpoint
  token                  = var.gke_token
  cluster_ca_certificate = var.gke_ca_certificate
}

# TODO: Configure secure secret management for database credentials.

resource "google_compute_network" "brandme_vpc" {
  name = "brandme-vpc"
}

resource "google_container_cluster" "brandme_gke" {
  name               = "brandme-gke"
  location           = "us-east1"
  network            = google_compute_network.brandme_vpc.name
  remove_default_node_pool = true
  initial_node_count      = 1

  # TODO: Define node pools, workload identity, and network policies.
}

resource "google_sql_database_instance" "brandme_postgres" {
  name             = "brandme-postgres"
  database_version = "POSTGRES_15"
  region           = "us-east1"

  settings {
    tier = "db-custom-2-7680"
    availability_type = "REGIONAL"
    backup_configuration {
      enabled = true
    }
  }

  # TODO: Configure VPC peering and authorized networks.
}

resource "google_storage_bucket" "passport_blobs" {
  name     = "brandme-passport-blobs"
  location = "US"
  force_destroy = false

  uniform_bucket_level_access = true

  # TODO: Apply lifecycle rules and retention policies aligned with compliance.
}

# Placeholder for NATS JetStream deployment on GKE via Helm.
# TODO: Add helm_release resources for data migrations and observability stack.

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gke_endpoint" {
  description = "GKE API endpoint"
  type        = string
}

variable "gke_token" {
  description = "GKE access token"
  type        = string
}

variable "gke_ca_certificate" {
  description = "GKE cluster CA certificate"
  type        = string
}
