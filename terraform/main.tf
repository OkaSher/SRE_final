terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 1. Firewall
resource "google_compute_firewall" "allow_http_ssh" {
  name    = "allow-http-ssh-8080"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "8080", "9090", "3000"] # 8080 для App, 9090 для Prometheus, 3000 для Grafana
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["sre-server"]
}

# 2. Создание виртуальной машины
resource "google_compute_instance" "sre_vm" {
  name         = "sre-production-vm"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 30 
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Этот блок дает серверу публичный IP-адрес
    }
  }

  tags = ["sre-server"]

  # Автоматическая установка Docker при первом запуске
  metadata_startup_script = <<-EOF
    #!/bin/bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
  EOF
}