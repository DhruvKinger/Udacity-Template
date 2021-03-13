## Passed Project !!

## You have done Excellent Work Here !! :tada: :clap:
### ✅Blueprint has two SSH credentials:
teccadmin
teccdba

### ✅ Blueprint has four VM service tiers:
Web Private Cloud
Web Public Cloud
Database
Load Balancer

### ✅ Security standards:
All VMs use the CentOS or Red Hat image specified and cloud-init to provision SSH credentials
All VMs use the teccadmin credential for tasks by default
Database VM uses teccdba credential to perform database tasks

### ✅ Blueprint has two application profiles:
Small
medium

-- ---

## Nice Work :tada: :star:
A web application configured to read and write to the database ✅

Post-deployment operation: a web-tier that scales and orchestrate updates to the load balancer configuration ✅

Web tier scaling actions that update the load balancer configuration across both web tiers ✅

Two profiles for deployment: small and medium, with specified VM resource and replicas configuration ✅

In HAProxy_Install during HAProxy Package Install, the HAProxy configuration doesn't contain an AWS web tier address. As a result, the load balancer doesn't forward traffic to the AWS web tier upon initial deployment. To resolve the issue, you should add AWS address macro to the configuration. ✅
