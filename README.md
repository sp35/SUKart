# SUKart

*Congratulations!!* For clearing the interaction round of **Students' Union Technical Team**. Now let's talk business, it's a job of backend developer to give life to the project they are going to be working on. You have to design a **shopping kart**, intimidated? Well, we will tone it down for you. Relax!! Go through this readme and then start coding.

## Users and Privileges
The shopping cart will have two types of `users`-

 1. Delivery Agent
 2. Shopping User

`Delivery Agent`has the job to deliver the goods to the shopping users. They are responsible for delivering the goods which are allotted to them to deliver in a particular timeline.
`Shopping User` is the customer and the heartbeat of our web-app. The `Shopping User` buys the product by using in-site currency (which can be filled using the django-admin portal).  

## Model Attributes

All website user will have a UID, Name, Email, DOB, City and State. Other than that they will have a currency associated with them (that's pretty obvious).
There should be a product model which will have product image, title, description, price and company.
There should also be a Company Model which contains only the company name.

## Workflow of the Site
The site will be have a very simplified workflow. The workflow is illustrated as follows-

 1. `Shopping User` and `Delivery Agent` has to register themselves
 2. `Shopping User` buys a product, and has the ability to search the product on the web-app.
 3. `Delivery Agent` is then alloted the product bought based on your algorithm.
 4. `Delivery Agent` notifies the `Shopping User` that product is arrived and then notifies regarding successful delivery via mails.
 5. The `Shopping User` can lodge a complaint in case of discrepancy using the website.

## Pro-Tip

The work distribution algorithm should be efficient enough to distribute almost equal work amongst it's `delivery agents` on the basis of location of the agent and the amount of delivery pending.
You can also wish to create a order model to keep track of status of the order.
**Bonus Task**-
Add a **cancellation feature** for user to be able to cancel their order if not yet recieved.

## Submission Phases

You might get intimidated at first so let's boil down the task into phases.

 1. **Phase 1** - Create all the models and implement views regarding showing, searching the product.
 2. **Phase 2** - Add a buy feature and develop the functionalities of the `delivery agent`.
 3. **Phase 3**- Add the complaint feature and work on the work distribution algorithm.
 4. **Phase 4** - Implement the `product upload feature`.

`Product Upload Feature` - When the *admin* logs into the website they have an additional functionality to populate the product database by uploading an excel sheet with required columns.
**Note**-
 Evaluation will be done on the basis of phases you have completed. **Incomplete Phases** won't be evaluated. It's better to switch to a different branch after a phase has been successfully completed.




## Requirements

 1. You are required to host the site on desirable hosting platforms like *Heroku*, *pythonanywhere* or *Digital Ocean*. **Unhosted** projects won't be evaluated, so take sufficient amount of time to create a proper workflow.
 2. You are supposed to use a [this](https://html5up.net/phantom). You are free to modify the html of the page or append any js to the frontend but deviation from this template will lead to **disqualification**.
 3. You are supposed to fork this repo and then start working on the forked repo. Other than hosting if the hosted site and the project files in the repository don't go hand-in-hand then we will **disqualify** you.
 4. *Plagarism is not fun*. If any of the two candidates are found to be working together on the same codebase and then showing that same codebase to the **recruiters** then they are immediately **disqualified**. You can refer from videos and documentation but copying the code of other candidates in any scale is not at all acceptable.


# My Take on this Task

A lot of efforts, time and thought is is put to develop this task. You all might be scared and frightened whether you will be able to complete this task. Well, don't worry things might go slow in the beginning but will speed up eventually. Development is not about knowing things but it's more about implementing things. Think about this, maybe later on you will be able to work on this project and can pitch it to a startup ( money heist ). Don't think of this task as a recruitment task, think that somewhere working on this project will lead you to gain more experience regarding development. When you will complete all the phases of this task for sure you will pat yourself on your back and if I am witnessing it I will too. The feeling of completing the projects will give you the happiness which is unparalleled to any material good in this world. Also do not forget to ping me if you completed all the phases, I will love to see you all grow as a developer. *Happy Coding*!!
