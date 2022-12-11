
### You have done an excellent Job. :smile:

All variables and arguments must have meaningful and readable (Camel Case or Upper Camel/Pascal Case) names.  ✅
All variables should be initialized where necessary.  ✅
All arguments must start with "in", "out", or "io".  ✅
Each activity must be renamed to include the action, application name, or title it interacts with.  ✅


### Additional Resources:-
* [Variables](https://docs.uipath.com/studio/docs/types-of-variables)

**Note:** Arguments, resembling variables, are used to pass data from one workflow to another. They can store data dynamically and pass it on. One difference between variable and argument is that variables pass data to other activities while arguments pass data to other workflows.


-- - - - -

## You have done an excellent Job. :smile:

### However :
There are still some activities that you didn't rename like the "Sequence" activities". Please, check again all the activities and make sure all of them have been renamed.
You should rename those activities or give them a meaningful annotation.
### See the screenshot below:-

![snip.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1623868637/snip.PNG)

### Also Please follow Proper Naming Conventions Like UpperCase or Camel Case!

--- - -- - -

## Nice Work :tada: :clap:
Great job using the “Try Catch” activity to handle potential errors! 
You have done this section really well I can see all the exceptions being declared and caught!!

### Additional Resources:-
* [Try-Catch](https://docs.uipath.com/activities/docs/try-catch)

**Note:** Try Catch activity is used when you want to test something and handle the exception accordingly. So, whatever you want to test you can put it under the try section, and then if any error occurs, then it can be handled using the catch section.

- -----
## Nice Work :tada: :clap:

You have to do this section . It seems to be missing. You need to manage the exceptions being declared and caught!!

### For Reference :-

![ccatch.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1623868796/ccatch.PNG)

** However in some places you have missed it. For Example, if Orchestrator crashes there is no Handling there. The orchestrator HTTP exception should handle it in that case. **

--- - - - 

### Great job !!
You have done excellent work using the log message activity! You used it to Log the exception message in each catch section of the "Try Catch" activity!

```
 Logging specific state changes within the workflow. Like the beginning and end of each workflow
 and that includes the main. ✅
 Writing or saving data. Like before and after the CSV file, uploading data to the queue. ✅
 Including specific data for each transaction when it is processed. log which item is being processed. ✅
 Use detailed logs when starting and/or completing actions that may result in errors. ✅

```

### Additional Resources:-
* [Logging-Levels](https://docs.uipath.com/studio/docs/logging-levels)

--- -- - - - 

## Great job !!
You have done excellent work in the try-catch activity! 
**However, you are missing the logging part.**

 Logging specific state changes within the workflow. Like the beginning and end of each workflow
 and that includes the main :x:
 Writing or saving data. Like before and after the CSV file, uploading data to the queue. :x:
 Including specific data for each transaction when it is processed. log which item is being processed. :x:
 Use detailed logs when starting and/or completing actions that may result in errors. :x:


### For Reference:- 
![snipz.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1623868867/snipz.PNG)

** In other words, your log messages must cover all state changes in your code. **

-- - - - -

### Nice Work :tada:

Every .xaml file must have an annotation at the beginning (including a description, pre-condition, and post-action) and at any If statement, describing what the condition is testing. :white_check_mark: 

All commented-out activities (or unused workflows) should be deleted for a clean workflow. :white_check_mark: 

### Additional Info:
* [Reference](https://www.youtube.com/watch?v=n25m-mEuJQY)

**Note:** Annotation is basically used to display a short message to the developer/business for why a particular sequence/workflow is created for. To create annotations we can right-click on the activity or sequence and click on Add annotations to write the specific message.

-- - - - - 

### Nice Work :tada:

Every .xaml file must have an annotation at the beginning (including a description, pre-condition, and post-action) and at any If statement, describing what the condition is testing. :x: 

All commented-out activities (or unused workflows) should be deleted for a clean workflow. :white_check_mark: 

** Please Add Necessary Annotations. **

** Additional Info: **
* [Reference](https://www.youtube.com/watch?v=n25m-mEuJQY)

- -- - - 

## Excellent Work :tada:
No more than 2 "If" activities should be nested within each other. Instead, this must be in a “Flowchart” or “Switch” activity to improve logic understanding. ✅

Each branch should have an activity; if there is an empty branch, have a “Comment” activity explaining what this branch means. ✅

** Here is an additional reference [Link](https://docs.uipath.com/studio/docs/the-if-activity) on If Else Statements. **

- - - -- - 

## Nice Work :tada: 

You have done this section really well. :smile:
If there are multiple “Click”, “Type Into”, or other activities within the same application right after the other, they should be in a container called "Attach Browser...", "Attach Window...", “Open Application…”, or “Open Browser…”.  ✅

**Here is an additional resource [link](https://docs.uipath.com/activities/docs/browser-scope) on Attach Browser activity.**

- - - - - - 

If there are multiple “Click”, “Type Into”, or other activities within the same application right after the other, they should be in a container called "Attach Browser...", "Attach Window...", “Open Application…”, or “Open Browser…”.

### However this seems to be missing. 

### For Reference See here :-

![aaaa.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1630042852/aaaa.JPG)

-------

### Excellent Work :clap: :tada:
Use “Find Element” or “Element Exists” activities to wait for loading or lagging applications, or check that an element is present on the screen before continuing with the execution. ✅

**Note:** Find Element waits for the specified UI element to appear on the screen and returns it as a UiElement variable.

------

### Excellent Work :tada:
Use partial selectors where several activities are executed in the same window.  ✅

**Here is an additional resource [link](https://docs.uipath.com/studio/docs/full-versus-partial-selectors) that differentiates b/w a full selector and a partial selector.**

**Note:** The primary difference between full and partial selectors is the partial selector generated by the basic recorder and will include all the elements that are required to identify a UI element along with the top-level window.

-----

### Dear Student :smile:
Use partial selectors where several activities are executed in the same window.   :x: 

** This section seems to be missing it will be done once you use the attach browser activity. **

![aaaa.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1630042981/aaaa.JPG)

--- - - - - - - -

## Great work :tada:

Use at least 1 Orchestrator Assets.  :white_check_mark:
Use at least 1 Orchestrator Queue.  :white_check_mark:

** Key Point ** : Orchestrator is a product of UiPath which enables you to orchestrate the UiPath robots in continuously executing repetitive processes on various platforms.

### Additional Resource:
* [Asset Docs](https://docs.uipath.com/orchestrator/docs/about-assets)
 
-- - - - -

### Nice Work :clap:
As Per requirements Please Use at least 1 Orchestrator Assets and Orchestrator Queue. :x:
** You can add Sender Email Id as an Asset and use Get Asset Method !! **

![aas.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1629305181/aas.JPG)

![orch.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1629305122/orch.JPG)

### Please fix this mandatory requirement ...

** However there should be no hard-coded values in the workflow. You can use assets for the same. **

---- ----

### Excellent Work here !!  :tada:
You've met all the specifications of this rubric.

:white_check_mark: 3 invoked workflow .xaml files
:white_check_mark: 1 data manipulation activity or function
:white_check_mark: Interaction with 2 applications
:white_check_mark: 5 different data types
:white_check_mark: Dispatcher and Performer design frameworks

### Additional Resource:-
* [Datatypes](https://excelcult.com/uipath-data-types-complete-guide/)

- - - - - -

### Excellent Work here !!  :tada:
You've met all the specifications of this rubric except one.

:white_check_mark: 3 invoked workflow .xaml files
:white_check_mark: 1 data manipulation activity or function
:white_check_mark: Interaction with 2 applications
:white_check_mark: 5 different data types
:x: Dispatcher and Performer design frameworks

### Note: You haven't described the use of the above missing point.

### Additional Resource :-
* [Datatypes](https://excelcult.com/uipath-data-types-complete-guide/)

- - - - - -

## Excellent Work :smile:

Modules should have a direct purpose with not more than 3 uses. Minimize the number of possible use cases for any given module to ensure reusability across multiple processes. ✅
Split by Interface interaction. Split by over-complexity. If a student's module is very complex, they explain why it is necessary to not break it up. ✅

All invoked workflows must be listed in the Whiteboard file. Each workflow must have a name, detailed description, pre-condition, post-action, and argument values.✅

- - - - -

## Excellent Work :smile:

Modules should have a direct purpose with not more than 3 uses. Minimize the number of possible use cases for any given module to ensure reusability across multiple processes. ✅
Split by Interface interaction. Split by over-complexity. If a student's module is very complex, they explain why it is necessary to not break it up. ✅

All invoked workflows must be listed in the Whiteboard file. Each workflow must have a name, detailed description, pre-condition, post-action, and argument values.:x:

### Please Define all your WorkFlows in Whiteboard File !!

**Note**:- Please attach the Whiteboard file in your submission. :smile:

- -- - -

## Great work on the PDD. :clap: :smile:

* Process Overview :white_check_mark:
* Detailed Process Map :white_check_mark:
* In Scope of RPA (includes everything in their automation) :white_check_mark:
* Business Exceptions Handling :white_check_mark:
* Unknown Exceptions :white_check_mark:
* Known Errors or Exceptions :white_check_mark:

### Additional Resource:-

* [Docs](https://docs.uipath.com/task-capture/docs/details-about-the-pdd)

**Note:** A process definition document (PDD) is the representation of “AS-IS” business processes that are chosen for RPA.

- -- - - 

## Great work on the PDD. :clap: :smile:

* Process Overview :white_check_mark:
* Detailed Process Map :x:
* In Scope of RPA (includes everything in their automation) :white_check_mark:
* Business Exceptions Handling :x:
* Unknown Exceptions :white_check_mark:
* Known Errors or Exceptions :white_check_mark:

### Missing Points:-
* The As-Is and To-Be Process Map figures are missing !!
* Exceptions are not defined.

### Additional Resource :-

* [Docs](https://docs.uipath.com/task-capture/docs/details-about-the-pdd)

- - - - -

### Great work on the DSD.  :clap: :smile:
* List of Packages :white_check_mark:
* Master Project Runtime Details :white_check_mark:
* Project Details (all parts) :white_check_mark:

--- - - - - - - -

## Nice job so far :smile: 

** However, to make your DSD perfect, you should do the following: **

+ Add a runtime diagram. The runtime diagram should display the interaction between components (package/robots, Orchestrator queues). Check this [knowledge question](https://knowledge.udacity.com/questions/566782) for more information.

+ Under the "List of packages" section, you must mention the orchestrator packages that your process consists of not the activities packages. For example, if your process consists of a dispatcher and a performer, you must add two packages (the dispatcher and the performer). if it consists of one process, you must add one package. In your case, you have one package, and its name is the project name.

+ Please add Orchestrator Details. 

+ Fill in the VI, and VII fields. Check this [thread](https://knowledge.udacity.com/questions/367806) to learn how.

![dhruv.PNG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1624622842/dhruv.PNG)

------------

## Excellent Work :tada:
### You have met all the points mentioned Below:

:white_check_mark: the overall process
whether the process will be unattended or attended, and when it will be scheduled, used by a user, or triggered another way
where the student used each of the specific requirements above:
-- five data types :white_check_mark:
-- two application interactions :white_check_mark:
-- asset from Orchestrator :white_check_mark:
-- three invoked workflows :white_check_mark:
-- queue they used (or why they didn't use a queue) :white_check_mark:
-- data manipulation function or activity :white_check_mark:

- - - - -

## Dear Student :smile:
### You have met all the points mentioned below except one:

:white_check_mark: the overall process
whether the process will be unattended or attended, and when it will be scheduled, used by a user, or triggered another way
where the student used each of the specific requirements above:
-- five data types :white_check_mark:
-- two application interactions :white_check_mark:
-- asset from Orchestrator :x:
-- three invoked workflows :white_check_mark:
-- queue they used (or why they didn't use a queue) :white_check_mark:
-- data manipulation function or activity :white_check_mark:

- - - - - -

## Dear Student :clap: :tada:
You are almost done! :muscle:
The structure of this project is already impressive and you’ve done a great job with most of the specifications.
You have defined all the types of Exceptions that could arise in your case and you have used Queues and Orchestrator in an efficient way as per requirements.
All the Modifications you need to do I have mentioned below.


You are only left with renaming Naming Conventions of the activities, logging and you need to update the documentation !!
Rest everything seems to be OK!!

### Additional Resources :bulb:

* [Storage Buckets](https://docs.uipath.com/orchestrator/docs/about-storage-buckets)
* [Test Schedulers](https://docs.uipath.com/orchestrator/docs/test-schedules)
* [Managing Tenants](https://docs.uipath.com/orchestrator/docs/managing-tenants)

--- - - 

## Dear Student,

![congrats.gif](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1615661006/congrats.gif)

### Congratulations! :tada:
The structure of this project is already impressive and you’ve done a great job with most of the specifications.
You have defined all the types of Exceptions that could arise in your case and you have used Queues and Orchestrator in an efficient way as per requirements. All the state changes have been covered !!

It was my pleasure to review this wonderful project. Please continue with this same sense of hard work and good luck with the next project. :udacious:

### Additional Resources 💡:-
### Below are some helpful resources related to the project implementation:

* [Storage Buckets](https://docs.uipath.com/orchestrator/docs/about-storage-buckets)
* [Test Schedulers](https://docs.uipath.com/orchestrator/docs/test-schedules)
* [Managing Tenants](https://docs.uipath.com/orchestrator/docs/managing-tenants)

- -- - - - - 


## Missing Required Files


## Dear Student :smile:
Please include the word document that describes the aspects of your project. This document plays an important role in assessing your project and hence you're required to include that in your submission. Please read rubric points again and then resubmit.

Please find the instructions on how to write the document under Project Instructions.

![snip.JPG](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/3625268/1623663126/snip.JPG)


-- -- - - -

### :smile: The previous Reviewer Passed you on this Point !!

---- 
## Dear Student 😄
Please do all the changes as suggested by previous reviewer ! You are still missing the points mentioned by reviewer say like DSD Update, Logging, Try Catch and hence you're required to include that in your submission. Please read rubric points again and then resubmit.

Please find the instructions on how to write the document under Project Instructions.
----

