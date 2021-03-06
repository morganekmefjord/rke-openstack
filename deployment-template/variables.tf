variable cluster_prefix {
  description = "Name prefix for the cluster resources"
  default     = "rke"
}

variable inventory_template {
  default = "inventory-template"
}

variable cloud_init_data {
  description = "cloud-init data to pass onto all instances"
  default = "cloud-init.tpl"
}

variable ssh_key {
  description = "Local path to SSH key"
  default     = "ssh_key"
}

variable ssh_key_pub {
  description = "Local path to public SSH key"
  default     = "ssh_key.pub"
}

variable ssh_user {
  description = "SSH user name (use the default user for the OS image)"
  default     = "ubuntu"
}

variable external_network_id {
  description = "External network ID"
}

variable floating_ip_pool {
  description = "Name of the floating IP pool (often same as the external network name)"
}

variable image_name {
  description = "Name of an image to boot the nodes from (OS should be Ubuntu 16.04)"
}

variable master_flavor_name {
  description = "Master node flavor name"
}

variable master_count {
  description = "Number of masters to deploy (should be an odd number)"
  default     = 1
}

variable service_flavor_name {
  description = "Service node flavor name"
}

variable service_count {
  description = "Number of service nodes to deploy"
  default     = 2
}

variable edge_flavor_name {
  description = "Edge node flavor name"
}

variable edge_count {
  description = "Number of edge nodes to deploy (this should be at least 1)"
  default     = 1
}

variable ignore_docker_version {
  description = "If true RKE won't check Docker version on images"
  default     = false
}

variable kubernetes_version {
  description = "Kubernetes version (should be RKE v0.1.x compliant: https://hub.docker.com/r/rancher/k8s/tags)"
  default     = "v1.13.5-rancher1-2"
}

variable write_kube_config_cluster {
  description = "If true kube_config_cluster.yml will be written locally"
  default     = true
}

variable write_cluster_yaml {
  description = "If true cluster.yml will be written locally"
  default     = true
}

variable master_assign_floating_ip {
  description = "If true a floating IP is assigned to each master node"
  default     = false
}

variable service_assign_floating_ip {
  description = "If true a floating IP is assigned to each service node"
  default     = false
}

variable edge_assign_floating_ip {
  description = "If true a floating IP is assigned to each edge node"
  default     = true
}

variable allowed_ingress_tcp {
  type        = "list"
  description = "Allowed TCP ingress traffic"
  default     = [22, 6443, 80, 443]
}

variable allowed_ingress_udp {
  type        = "list"
  description = "Allowed UDP ingress traffic"
  default     = []
}

variable os_username {
  description = "Openstack user name"
}

variable os_password {
  description = "Openstack tenancy password"
}

variable os_auth_url {
  description = "Openstack auth url"
}

variable os_project_id {
  description = "Openstack tenant/project id"
}

variable os_project_name {
  description = "Openstack tenant/project name"
}

variable os_user_domain_name {
  description = "Openstack domain name"
}
