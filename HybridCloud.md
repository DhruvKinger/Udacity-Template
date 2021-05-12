## Passed Project !!

## Excellent Work :tada: :clap:
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

![Capture (1).png](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1619778659/Capture__1_.png)

### Additional Resources :smile: :-
### Below are some helpful resources related to the project implementation:

* [Dual Web Tier](https://classroom.udacity.com/nanodegrees/nd321-beta/parts/def00787-ddd6-4446-b326-8c94cfcbd639/modules/acac62c3-0218-4413-99fc-5a4d8f035559/lessons/f8a91839-428c-45e2-bfb2-ee70cc09e69c/concepts/f495cd57-5e82-408c-b171-98b81945af3b)
* [Load Balancing](https://www.nginx.com/resources/glossary/load-balancing/)
* [Hybrid Cloud](https://azure.microsoft.com/en-in/overview/what-is-hybrid-cloud-computing/)

- - - - - -  -
## Failed Project !!
## Excellent Work :tada: :clap:
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

### Note:
1) Please rename your Application Profiles to small and medium !!
2) For Security Reasons pls delete API_User .
3) Please use correct credentials for WebServer and HAProxy use teccadmin and for db operations use teccdba.
- ------

### WebScaleIn,WebScaleOut,AWSScaleOut,AWSScaleIn,HAProxy Install are missing AWS web server address macro in the configuration :warning: With the current configuration, HAProxy forwards all traffic to the private cloud web tier only, not the AWS web tier. Add the AWS address macro to the configuration similar to how I have attached the screenshot below.

### Your Submission:-

![dw](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1619693024/web.JPG)

### For Reference:-
![Fix.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1620049909/Fix.JPG)

### Note: Make sure that no VM resource parameters can be changed by the end user. Please change it's color from blue to black.
![resource.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1620735787/resource.JPG)



### Remember:-
We have two application profiles so always update all things on both small and medium application profiles. If anything required changes for one profile make sure to verify for the other profile too.


------
## Nice Work :star:

### Database backup custom action, adapted from the source code [MySQL_backup_file.sh.txt](https://raw.githubusercontent.com/nutanixdev/udacity/main/HybridCloudEngineer/course/3/project/MySQL_backup_file.sh.txt) to use the end-user, runtime specified password for the database root account ❌

### Database restores custom action, adapted from the source code [MySQL_restore.sh.txt](https://raw.githubusercontent.com/nutanixdev/udacity/main/HybridCloudEngineer/course/3/project/MySQL_restore.sh.txt) to use the end-user, runtime specified password for the database root account. ❌

### Note: Please use correct scripts and use Macro for Password !!
![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1616759968/Capture.PNG)

### Remember:-
We have two application profiles so always update all things on both small and medium application profiles. If anything required changes for one profile make sure to verify for the other profile too.

--  -- -- -
## Dear Student :clap: :tada:
You are almost done! :muscle:
The structure of this project is already impressive and you’ve done a great job with most of the specifications.
You are only left with renaming Application Profile Names and need to add Macro of AWS WebServer !!
Rest everything seems to be fine !!


For every change mentioned, ensure that you do the fix on both the small and medium profile. Also, check other VM and tasks to be sure they are Okay.
Launch your blueprint to ensure it gets launched and you see the corresponding VMs and instances created on both the private cloud and on AWS.
Perform the scale in/ scale out on both the private and public cloud and verify it works.
Perform a backup action and verify your database is backed up.
When all these works you will be 100% sure that your project has met all the required specs.

### Additional Resources :bulb:
### Below are some helpful resources related to the project implementation:

* [Dual Web Tier](https://classroom.udacity.com/nanodegrees/nd321-beta/parts/def00787-ddd6-4446-b326-8c94cfcbd639/modules/acac62c3-0218-4413-99fc-5a4d8f035559/lessons/f8a91839-428c-45e2-bfb2-ee70cc09e69c/concepts/f495cd57-5e82-408c-b171-98b81945af3b)
* [Load Balancing](https://www.nginx.com/resources/glossary/load-balancing/)
* [Hybrid Cloud](https://azure.microsoft.com/en-in/overview/what-is-hybrid-cloud-computing/)

