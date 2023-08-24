import git
import os
from distutils.dir_util import copy_tree
import stat
import re

class GitCommands:

    def __init__(self, type, environment):
        self.type = type

        user_input_variables = utility.get_variables(environment)

        self.cisco_msft_branch = user_input_variables['temporary_cisco_msft_branch']
        self.cisco_cisco_branch = user_input_variables['incoming_cisco_changes_local']
        self.msft_cisco_branch = user_input_variables['incoming_cisco_changes_remote']
        self.log_path = user_input_variables['log_path']
        
        git_path = user_input_variables['git_path']
        self.cisco_git_path = git_path+user_input_variables['cisco_git_path']
        self.msft_git_path = git_path+user_input_variables['msft_git_path']
        
        self.cisco_repo_name = user_input_variables['cisco_repo_name']
        self.msft_repo_name = user_input_variables['msft_repo_name']

        self.msft_username = user_input_variables['msft_username']
        self.msft_password = user_input_variables['msft_password']

        self.cisco_username = user_input_variables['cisco_username']
        self.cisco_password = user_input_variables['cisco_password']

    def authenticate(self):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
                os.system('git config --global user.name '+self.cisco_username)
                os.system('git config --global user.password '+self.cisco_password)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)
                os.system('git config --global user.name '+self.msft_username)
                os.system('git config --global user.password '+self.msft_password)
            return True
        except Exception as error:
            print(error)
            return False

    def check_status(self, branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            os.system('git checkout '+str(branch)+ ' 1> ' +self.log_path+'/git_output.txt 2>&1')
            
            log_read = open(self.log_path+"/git_output.txt", "r")
            for i in log_read.readlines():
                if "Your branch is up to date" in i:
                    return True
            
            return False
        except Exception as error:
            print(error)
            return False

    def fetch_data(self, branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)
            os.system('git checkout '+ branch)
            os.system('git fetch -v --dry-run 1> '+self.log_path+'/git_output.txt 2>&1')

            log_read = open(self.log_path+"/git_output.txt", "r")
            
            for log in log_read.readlines():
                fetch = re.compile(r'^[\d \w \W]*(up to date)[\d \W \w]*({})[\d \W \w]*$'.format(branch))
                if fetch.search(str(log)):
                    return False

            return True
        except Exception as error:
            print(error)
            return True

    def pull_and_push_data(self, origin_branch, destination_branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
                repo = git.Repo(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)
                repo = git.Repo(self.msft_git_path)
            
            self.pull_data(origin_branch)
            os.system('git checkout '+destination_branch)

            os.system('git pull origin '+origin_branch)
            os.system('git push')
            
            return True
        except Exception as error:
            print(error)
            return False

    def pull_data(self, acceptor_branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            self.checkout_branch(acceptor_branch)
            os.system('git pull 1> '+self.log_path+'/git_output.txt 2>&1')

            log_read = open(self.log_path+"/git_output.txt", "r")

            for i in log_read.readlines():
                if "Fast-forward" in i:
                    return True
            return True
        except Exception as error:
            print(error)
            return False

    def push_data(self, push_branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            os.system('git checkout '+push_branch)

            os.system("git add .")
            os.system('git commit -m "Automated git-sync from "'+self.type+'" repo"')
            os.system('git push')

            return True
        except Exception as error:
            print(error)
            return False

    def checkout_branch(self, branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            os.system('git checkout '+branch)

            return True
        except Exception as error:
            print(error)
            return False

    def check_diff(self, branch1, branch2):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
                self.checkout_branch(branch1)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)
                self.checkout_branch(branch1)
            
            os.system('git diff '+branch1+' '+branch2+' 1> '+self.log_path+'/git_output.txt 2>&1')
            
            log_read = open(self.log_path+"/git_output.txt", "r")
            
            for log in log_read.readlines():
                diff = re.compile(r'^[\d \w \W]*(index)[\d \W \w]*$')
                if diff.search(str(log)) :
                    return True
            
            return False
        except Exception as error:
            print(error)
            return True

    def stash(self, branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            self.checkout_branch(branch)
            os.system('git stash')
        except Exception as error:
            print(error)
            return False

    def pull_remote(self, branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            self.checkout_branch(branch)
            if self.check_status(branch) == False:
                self.stash(branch)
            os.system('git pull origin '+str(branch)+' 1> '+self.log_path+'/git_output.txt 2>&1')
            return True 
        except Exception as error:
            print(error)
            return False

    def check_conflict(self, base_branch, check_branch):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            self.checkout_branch(base_branch)
            
            os.system('git merge '+str(check_branch)+' --no-ff --no-commit 1> '+self.log_path+'/git_output.txt 2>&1')
            try:
                os.system('git merge --abort')
            except:
                print("No merge")

            log_read = open(self.log_path+"/git_output.txt", "r")
            
            for log in log_read.readlines():
                print(log)
                conflict_check = re.compile(r'^[\d \w \W]*(Automatic merge went well)[\d \W \w]*$')
                if conflict_check.search(str(log)) or "Already up to date" in log:
                    return False

            return True
        except Exception as error:
            print(error)
            return False

    def merge(self, branch1, branch2):
        try:
            if self.type == "cisco":
                os.chdir(self.cisco_git_path)
            elif self.type == "msft":
                os.chdir(self.msft_git_path)

            self.checkout_branch(branch1)
            os.system('git merge '+str(branch2)+' -m "Automated git sync and merge"')
            os.system('git push')
            self.checkout_branch(branch2)
            os.system('git merge '+str(branch1)+' -m "Automated git sync and merge"')
            os.system('git push')

            return True
        except Exception as error:
            print(error)
            return False
