
## Good work. :tada: :clap:
Thanks for submitting the excel file. 
Your attached excel which has the configuration details generated from Nutanix.

- - - - - - - -

## Nice work :smile:
* A text file CTOEmail.txt containing a thorough summary of the tasks performed, based on emails from the CTO, networking team, and systems administration team had been submitted. ✅
* Configuration Criteria should be included in the email. ✅

- - - - - - - -

## Well done. :clap: :tada:
** You have configured the NTP server details correctly in Nutanix. **

![NTP.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1604763730/NTP.PNG)

NTP server is used for Time Synchronization and it is used across different devices and services on a network to maintain the reliability and integrity of services, data, and other critical functions.

- - - -
### Additional Resource:-
Good Read on [NTP usability.](https://next.nutanix.com/installation-configuration-23/time-synchronization-on-nutanix-cluster-33558)

- - - - - - - -

### Well done. :100: :tada:
```
Domain Name Server configuration correctly added. It is part of Google Public DNS which has id such as 8.8.8.8 or 8.8.4.4
```
### Additional Resource :-
Good read on DNS for depth understanding :- https://developers.google.com/speed/public-dns :clap:


- - - - 

## Good work. :tada:
You have named the network appropriately as well. In a real-time scenario, there will be multiple Managed networks, and providing the correct naming convention is very important.

### Additional Resources:-
[Managed Network ](https://next.nutanix.com/how-it-works-22/create-managed-network-with-powershell-33024)


![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615430890/Capture.PNG)

---- 

## Excellent :clap:
```
The unmanaged network is identified as the development network by name and has the correct Vlan and Prefix Length shown in the email provided by the Network Operations group. ✅
```

### Additional Resource:-
* [Unmanaged Network](https://www.hyve.com/insights/managed-vs-unmanaged-cloud/)

----

### Good work. :star: :clap:
You have completed these steps correctly and created the images - Disk for required OS types.

![Images.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1604367727/Images.PNG)

** Reference for more details: **

** Short Article for [Image Creation](https://next.nutanix.com/prism-infrastructure-management-26/ahv-vdisk-part-3-creating-an-image-of-or-from-an-existing-vdisk-33686) **

-----

:100: Production VMs correctly created and required Naming convention followed.
```
VM Name: db-prod (or equivalent) ✅
VM Name: app-prod (or equivalent) ✅
VM Name: web-prod (or equivalent) ✅
The VMs should be on the production/managed network listed under column B (i.e VLANs). ✅
```

### Additional Resource:-
* [Automating Nutanix Prism VMs](https://www.scottharney.com/automating-nutanix-prism-vms/)

-----

### Excellent :star: :tada:
The virtual machines needed for the development environment are successfully cloned from the production VMs and satisfy the resource specifications and naming convention as required by the Systems Administration group. They are also developed on the development network as required. Great job. :clap:

-----

### Good job. :tada:
```
Successfully created a protection configuration for the production environment and the schedule has been correctly set up to repeat after every 60 minutes to take snapshots of all the virtual machines on the production environment for a backup in case of a power or any other failure.
```

-----

### Nice Work 
You have completed this Point successfully !!

![Capture1.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615431460/Capture1.PNG)

-----

## Dear Student,

![congrats.gif](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615661006/congrats.gif)

### Congratulations! :tada:
The default network is kept and the steps sent to the CTO were revised to be more general. You have deployed and protected the three Virtual Machines composing the infrastructure for a web application: a web server VM, application VM and database server VM on the private cloud. You have configured an on-prem HCI environment to support VM's and implemented a data protection/disaster recovery strategy to protect them.

It was my pleasure to review this wonderful project. Please continue with this same sense of hard work and good luck with the next project. :udacious:

### Additional Resources 💡:-
### Below are some helpful resources related to the project implementation:

[Comparing Two Application Deployment Environments: Private Cloud Vs. On-Premises](https://www.bluepiit.com/blog/private-cloud-vs-on-premises/)

[Private cloud vs. public cloud](https://review.udacity.com/archcloudcomputing.techtarget.com/definition/private-cloud)

[Data Protection Concepts in Nutanix](https://portal.nutanix.com/page/documents/details?targetId=Web-Console-Guide-Prism-v55:wc-dr-concepts-wc-c.html)

[High Availability and Data Protection](https://www.nutanix.com/blog/nutanix-high-availability-and-data-protection)

- - - - - -
## Failed Project !!

### There are two major parts to the E-mail text file. They are,
A summary of the requirements based on emails from the CTO, networking team, and systems administration team.
An outline of the tasks that have been performed.
The submitted E-mail text contains the tasks that have been performed but there also should be a short summary containing the requirements at the beginning that have been told. Follow the below suggestions which will help you with this section.

Give a brief summary of the requirements that were asked at the beginning.
In the performed tasks outline, give more details of the configurations. For example, the name of the used NTP server, container, protection domain, etc. Also give the names, VLAN's and IP addresses of the networks and Virtual Machines.
You can use bullet points for both sections. It will give a clear view of the message.

---- 
## Good work. :tada:
You need to rename the name of Managed network to Production !! Rest Everything seems to be fine !! In a real-time scenario, there will be multiple Managed networks, and providing correct naming convention is very important

![Capture1.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615680130/Capture1.PNG)

- - - -

### Good work. :tada:
You need to rename the name of Unmanaged network to Development !! Rest Everything seems to be fine !! In a real-time scenario, there will be multiple Unmanaged networks, and providing correct naming convention is very important

-- - - -

** :100: Production VMs need to be correctly set and require correct Naming convention. **

```
VM Name: db-prod (or equivalent) ✅
VM Name: app-prod (or equivalent) ❌
VM Name: web-prod (or equivalent) ❌
The VMs should be on the production/managed network listed under column B (i.e VLANs). ✅
```


![Capture1.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615479850/Capture1.PNG)

- - - -
### :100: Development VMs need to be correctly set and require correct Naming convention.
```
VM Name: db-dev (or equivalent) ❌
VM Name: app-dev (or equivalent) ✅
VM Name: web-dev (or equivalent) ❌
The VMs should be on the development network listed under column B (i.e VLANs). ✅
```

- - - -- 

### Dear Student :smile:
You have missed configuring the NTP server details correctly in Nutanix.

### Your Submission :-

![gbb.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1631097554/gbb.JPG)

### For Reference :-
![NTP.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1604763730/NTP.PNG)

NTP server is used for Time Synchronization and it is used across different devices and services on a network to maintain the reliability and integrity of services, data, and other critical functions.

### Additional Resource:-
Good Read on [NTP usability.](https://next.nutanix.com/installation-configuration-23/time-synchronization-on-nutanix-cluster-33558) 

-----------


### There should be 6 VM in the end state in total.
2 - VM prod
3 - VM - Dev
1 VM which is cloned one after deleting any prod VM.

### Note: you have cloned VMs but they should be done after deleting production VMs!

## Your Submission

![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615680304/Capture.PNG)

## Ideally, it should look something Like this :
![Capture4.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3935679/1609335240/Capture4.PNG)

- - - - -

### Good work. :star: :clap:
You have completed these steps correctly and created the images - Disk for required OS types.

![Capture.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1618752619/Capture.PNG)

### Reference for more details:

 Short Article for [Image Creation](https://next.nutanix.com/prism-infrastructure-management-26/ahv-vdisk-part-3-creating-an-image-of-or-from-an-existing-vdisk-33686)

**Note: You need to change the name of the Container from ISO to Images.**

-  -- - - -
### Dear Student :star:

The Data Protection domain(s) should be easily identified as the protection configurations for the production environment and with the recovery parameters provided in the email from the CTO. :x:

** Note: One Protection domain or multiple Protection domains are both acceptable. **

- - - - -

## Dear Student :clap: :tada:

You are almost done! :muscle:
The structure of this project is already impressive and you’ve done a great job with most of the specifications. You have deployed and protected the three Virtual Machines composing the infrastructure for a web application: a web server VM, application VM and database server VM on the private cloud. Just some small adjustments to be made. I have provided more details in the review.
### Additional Resources  :bulb: 
### Below are some helpful resources for further reading:

* [Comparing Two Application Deployment Environments: Private Cloud Vs. On-Premises](https://www.bluepiit.com/blog/private-cloud-vs-on-premises/)

* [Private cloud vs. public cloud](https://review.udacity.com/archcloudcomputing.techtarget.com/definition/private-cloud)

* [Data Protection Concepts in Nutanix](https://portal.nutanix.com/page/documents/details?targetId=Web-Console-Guide-Prism-v55:wc-dr-concepts-wc-c.html)

* [High Availability and Data Protection](https://www.nutanix.com/blog/nutanix-high-availability-and-data-protection)
