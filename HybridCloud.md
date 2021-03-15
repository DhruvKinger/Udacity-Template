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


- - - -- 

## Nice Work :star:
### You have done Excellent Work Here too !! :tada: :clap:
### Database backup custom action, adapted from the source code [MySQL_backup_file.sh.txt](https://raw.githubusercontent.com/nutanixdev/udacity/main/HybridCloudEngineer/course/3/project/MySQL_backup_file.sh.txt) to use the end-user, runtime specified password for the database root account ✅
### Database restores custom action, adapted from the source code [MySQL_restore.sh.txt](https://raw.githubusercontent.com/nutanixdev/udacity/main/HybridCloudEngineer/course/3/project/MySQL_restore.sh.txt) to use the end-user, runtime specified password for the database root account. ✅


- - -- - -
## Dear Student,
### Congratulations! :tada:
It was my pleasure to review this wonderful project. Please continue with this same sense of hard work and good luck with the next project. :udacious:
I like how consistent and patient you have been in implementing this project. Most of the concept displayed shows you have grasped a lot from the classroom.

**Note** : this is not a requirement for passing this project but optional!

I noticed in your environment variable for the password, In the MySQL password best practice is to use a minimum of 8 characters with at least one upper case letter. You can enforce it by checking on the box with validating with a regular expression and in the box that appears, you should enter the regex to perform the validation. You can find out how to write the regex following the tutorial here [how-to-use-regular-expressions-to-check-password-strength](https://stackoverflow.com/questions/5142103/regex-to-validate-password-strength). you will want to scroll to the section with a Minimum of 1 Uppercase Character. However, for better understanding, you can follow all along.

![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615638054/Capture.PNG)

### Additional Resources
### Below are some helpful resources related to the project implementation:

* [Dual Web Tier](https://classroom.udacity.com/nanodegrees/nd321-beta/parts/def00787-ddd6-4446-b326-8c94cfcbd639/modules/acac62c3-0218-4413-99fc-5a4d8f035559/lessons/f8a91839-428c-45e2-bfb2-ee70cc09e69c/concepts/f495cd57-5e82-408c-b171-98b81945af3b)
* [Load Balancing](https://www.nginx.com/resources/glossary/load-balancing/)
* [Hybrid Cloud](https://azure.microsoft.com/en-in/overview/what-is-hybrid-cloud-computing/)


## Failed Project !!
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

### ❌ Blueprint has two application profiles:
Small
medium

### Note: Please rename your Application Profiles to small and medium !!

- ------

### WebScaleIn,WebScaleOut,AWSScaleOut,AWSScaleIn,HAProxy Install are missing AWS web server address macro in the configuration :warning: With the current configuration, HAProxy forwards all traffic to the private cloud web tier only, not the AWS web tier. Add the AWS address macro to the configuration similar to how I have attached the screenshot below.

### Your Submission:-

![Screenshot (65).png](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615771380/Screenshot__65_.png)

### Required Change:-
![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615771464/Capture.PNG)
------
