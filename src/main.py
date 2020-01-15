#! /usr/bin/env python3

import argparse
import os

import pathspec
import git
import logging
import datetime
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

class Converter():
    def __init__(self, repo, target_path):
        self.repo = repo
        self.target_path = target_path
        self.jinja_env = Environment(
            loader=FileSystemLoader('templates/'),
            autoescape=select_autoescape(['md'])
        )

        self.templates = {}
        self.templates = {
            "posts": {
                "dest": "content/posts",
                "template": self.jinja_env.get_template("posts.template")
            },
            "notes": {
                "dest": "content/notes",
                "template": self.jinja_env.get_template("posts.template")
            },
            "about": {
                "dest": "content",
                "template": self.jinja_env.get_template("about.template")
            }
        }
        return

    def infer_category(self, filename):
        if 'book-notes' in filename:
            return 'notes'
        if 'essay' in filename:
            return 'posts'
        if 'about' in filename:
            return 'about'
        return ''

    def infer_dates(self, filename):
        commits = list(self.repo.iter_commits(paths=filename))
        
        if len(commits) > 0:
            created = datetime.datetime.fromtimestamp(commits[-1].authored_date)
            last_updated = datetime.datetime.fromtimestamp(commits[0].authored_date)
            return created, last_updated
        else:
            return datetime.datetime.now(), datetime.datetime.now()

    def infer_dest_filename(self, dest_folder, filename):
        # use this document's name by default
        # if the document's name is readme, substitute with folder name
        if os.path.basename(filename).strip().lower() == "readme.md":
            filename = os.path.basename(os.path.dirname(filename))
            filename += ".md"
        dest_file = os.path.join(dest_folder, os.path.basename(filename))
        return dest_file

    def process_content(self, src_file_name, dest_file_name):
        """reads in src_file_name, and produce title, content strings from the file
        If a title cannot be inferred, try inferring from str dest_file_name
        """
        title = ""
        content = ""
        if src_file_name.endswith(".md"):
            with open(src_file_name, "r") as infile:
                cnt = 1
                for line in infile:
                    cnt += 1
                    # we use the title if a "# " is found early enough
                    if cnt < 3 and line.strip().startswith("# ") and title == "":
                        title = line.strip().replace("# ", "").capitalize()
                        continue
                    content += line
        else:
            with open(src_file_name, "r") as infile:
                content = infile.read()
        if not title:
            title = os.path.basename(dest_file_name).replace('_', ' ').replace('-', ' ').replace('.md', '').capitalize()
        return title, content

    def create(self, filename):
        category = self.infer_category(filename)
        if category in self.templates:
            created, _ = self.infer_dates(filename)
            dest_folder = os.path.join(self.target_path, self.templates[category]["dest"])
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            dest_file = self.infer_dest_filename(dest_folder, filename)
            title, content = self.process_content(filename, dest_file)
            with open(dest_file, "w") as wfile:
                rendered = self.templates[category]["template"].render(created_date=created, title=title, content=content)
                wfile.write(rendered)
                logging.info("rendered {} from {}".format(dest_file, filename))
        return

    def create_files(self, infiles):
        for filename in infiles:
            self.create(filename)
        return

def get_local_checkout(remote, local_dir):
    try:
        repo = git.Repo(local_dir)
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.clone_from(remote, local_dir)
    except git.exc.NoSuchPathError:
        repo = git.Repo.clone_from(remote, local_dir)
    repo.remote().pull(repo.active_branch)
    logging.info("finished updating repo at {}".format(os.path.abspath(local_dir)))
    return repo

def get_src_list(local_dir, include_file):
    with open(include_file, 'r') as include:
        spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, include.readlines())
        result = [os.path.abspath(os.path.join(local_dir, f)) for f in spec.match_tree(local_dir)]
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    local_dir = "../checkout"
    repo = get_local_checkout("https://github.com/zhehaowang/zhehao.me.git", local_dir)

    include_file = "site.include"
    src_files = get_src_list(local_dir, include_file)
    
    target_dir = "../generated"
    converter = Converter(repo, target_dir)
    converter.create_files(src_files)