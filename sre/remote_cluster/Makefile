# Makefile to run Ansible playbooks

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

generate_development_group_vars:
	cp group_vars/development/awx_stack.yaml.example group_vars/development/awx_stack.yaml
	cp group_vars/development/kops_cluster.yaml.example group_vars/development/kops_cluster.yaml
	echo "ansible_python_interpreter: $(shell which python)" > group_vars/development/ansible.yaml

.PHONY: create_kops_cluster
create_kops_cluster: ## Creates a single cluster created by kops
	ansible-playbook -i inventory.yaml -v playbooks/manage_kops_cluster.yaml --tags "create"

.PHONY: list_kops_clusters
list_kops_clusters: ## Lists all active clusters created by kops
	ansible-playbook -i inventory.yaml playbooks/manage_kops_cluster.yaml --tags "list"

.PHONY: destroy_kops_cluster
destroy_kops_cluster: ## Deletes a single cluster created by kops
	ansible-playbook -i inventory.yaml playbooks/manage_kops_cluster.yaml --tags "delete"

.PHONY: export_kops_cluster_kubeconfig
export_kops_cluster_kubeconfig: ## Exports the kubeconfig of a single cluster created by kops
	ansible-playbook -i inventory.yaml playbooks/manage_kops_cluster.yaml --tags "export"

.PHONY: create_awx_stack
create_awx_stack: ## Creates an AWX stack created by kops
	ansible-playbook -i inventory.yaml playbooks/manage_awx_stack.yaml --tags "create"

.PHONY: destroy_awx_stack
destroy_awx_stack: ## Destroy an AWX stack created by kops
	ansible-playbook -i inventory.yaml playbooks/manage_awx_stack.yaml --tags "delete"

# V1

.PHONY: destroy_all_clusters
destroy_all_clusters: ## Deletes all clusters
	ansible-playbook playbooks/destroy_all_clusters.yaml

.PHONY: start
start: list_kops_clusters ## Starts an inactive cluster
	@echo "edit the file to set size both controller and workers to the desired value with min = max values = desired value"
	ansible-playbook playbooks/edit_clustersize.yaml

.PHONY: stop
stop: list_kops_clusters ## Suspends an active cluster
	@echo "edit the file to set size both controller and workers to be zero for min and max values"
	ansible-playbook playbooks/edit_clustersize.yaml

.PHONY: resize
resize: list_kops_clusters ## Resizes an active cluster
	@echo "edit the file to set size both controller and workers to the desired value with min = max values = desired value"
	ansible-playbook playbooks/edit_clustersize.yaml
