# Git Basics

Here are COS333 notes about version control: [Link](https://www.cs.princeton.edu/courses/archive/fall22/cos333/lectures/02versionctrl/GitGitHubPrimer.pdf)

This will have information on setting up Git/Github. You can probably skip the steps about creating a new repository for now.

We will be using Git/Github for version control of our project. Version control
lets us keep track of code changes and more easily facilitate collaboration
between programmers working on a team.

To be more clear, Git is a software that, among other things, tracks project history, while Github
allows people to upload and host their Git project/repository on the internet.
There are other ways of sharing Git projects, but Github is what we use.

To get started, follow the instructions in the README. After you have done
the setup there and are ready to make changes, you can use the following
commands to contribute to the codebase.

## Branches

Git has a concept called branches. Branches allow you to make changes starting from a snapshot of the codebase. We will have one branch, main, that will be the primary starting point for your branches.

To get started with making changes, create a new branch:

`git checkout -b [your branch name] main`

This should automatically put you on your newly created branch. To navigate between branches in the future, you can use checkout like this:

`git checkout [branch name]`

By using branches, we can have several people make changes from the same starting point. You can make new features/experiment on this new branch without worrying about messing up the main branch.

At this point, the branch is only on your local computer, so to let github know that you created a branch, you would do

`git push -u origin [your branch name]`

This establishes what is called a remote branch, which your local branch is 'tracking'. This will be important for later.

## Making Changes

After writing some code/making changes, if you come to a point where you feel that you want to 'save' and officially record your current progress, you can commit what you've done so far.

First, you add the files you want to commit.

`git add [file name]`

If you want to add all the files you've made changes to, use

`git add .`

Then, you can add these desired changes into a commit:

`git commit -m "[a descriptive message]"`

Think of a commit as a checkpoint that is recorded in the project's history. A commit should generally be small so that you're consistently saving your progress. Try to make commits where the code is still in a workable state (ie distinct milestones, avoiding bugs).

You've now added a commit to your branch's history. However, these changes are only reflected on your local computer. In order to update the history on github, you would do

`git push`

This would record the commits you made to the remote branch you have setup on Github.

## General Things

Before your push code, it's generally good to see if you missed any changes that were pushed to Github.

For example, the main branch will contain all the important code that every branch needs. in order to merge any commits that have been pushed to main to the current branch you're on, run a

`git pull origin main`

This will try to reconcile the changes you've made to the branch so far and what is on main. If it cannot, then you will get a merge conflict. At that point, you have to manually fix/combine code. Git will mark these conflicts for you to fix.

If you and other teammates are working on the same branch, you should run

`git pull`

before pushing your commits. `git pull` by itself will pull changes from the remote branch your current local branch is tracking. Basically, it will merge any changes your teammates have pushed to the corresponding remote branch.
