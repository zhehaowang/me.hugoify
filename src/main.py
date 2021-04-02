#! /usr/bin/env python3

import argparse
import os
import re

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
            },
            "emcpp": {
                "dest": "content/effectives",
                "tocdest": "content/notes",
                "template": self.jinja_env.get_template("posts.template")
            }
        }

        # state we hold for parsing Effective series book notes
        self.effectives = {}

        self.code_ext = ["cpp", "c", "sh", "cc", "h", "hpp", "py", "js", "java"]
        self.comment_style = {
            "cpp": "//",
            "c": "//",
            "cc": "//",
            "h": "//",
            "hpp": "//",
            "sh": "#",
            "py": "#",
            "js": "//",
            "java": "//"
        }
        self.canonical_ext = {
            "cpp": "cpp",
            "c": "cpp",
            "cc": "cpp",
            "h": "cpp",
            "hpp": "cpp",
            "sh": "sh",
            "py": "python",
            "js": "javascript",
            "java": "java"
        }
        self.cannonical_book_name = {
            "ecpp": "Effective C++",
            "emcpp": "Effective Modern C++",
            "estl": "Effective STL",
            "epython": "Effective Python"
        }
        return

    def infer_category(self, filename):
        # priority 1 conditions
        for it in ['emcpp', 'ecpp', 'estl']:
            if it in filename:
                return 'emcpp'
        
        # priority 2 conditions
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

    def render_default_category(self, category, filename):
        """render one
            book-notes/*/readme.md => contents/notes/*.md
            essays/*.md  => contents/posts/*.md
        """
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
    
    def parse_effective_content(self, filename):
        m = re.match("it([0-9]+).*", os.path.basename(filename))
        contents = {}
        if m:
            current_item_num = int(m.group(1)) - 1
            with open(filename, 'r') as infile:
                for line in infile:
                    if line.startswith("### "):
                        current_item_num += 1
                        contents[current_item_num] = {
                            "title": line.replace("### ", "").strip(),
                            "content": ""
                        }
                    else:
                        if current_item_num in contents:
                            # filter out front matter before the start of the first chapter
                            contents[current_item_num]["content"] += line
        else:
            logging.error("failed to parse starting item from {}".format(filename))
        return contents

    def render_effective_category(self, category, filename):
        """load given file from one effective book series notes (chapter-level notes, individual notes, or multiple snippets file) into self.effectives
        """
        parts = filename.split('/')
        book_name = ""
        for idx in range(len(parts)):
            if parts[idx] == 'book-notes':
                book_name = parts[idx + 1]
        if not book_name:
            logging.error("failed to find book name for {}".format(filename))
        if not book_name in self.effectives:
            self.effectives[book_name] = {}

        if filename.endswith(".md"):
            # collection of notes file
            contents = self.parse_effective_content(filename)
            for item_id in contents:
                if not item_id in self.effectives[book_name]:
                    self.effectives[book_name][item_id] = contents[item_id]
                else:
                    for key in contents[item_id]:
                        self.effectives[book_name][item_id][key] = contents[item_id][key]
        else:
            for ext in self.code_ext:
                if filename.endswith(ext):
                    # single snippet file
                    item_name = os.path.basename(os.path.dirname(filename))
                    m = re.match("it([0-9]+).*", item_name)
                    if m:
                        item_id = int(m.group(1))
                        if item_id not in self.effectives[book_name]:
                            self.effectives[book_name][item_id] = {
                                "snippet-lang": self.canonical_ext[ext],
                                "snippet": ""
                            }
                        elif "snippet" not in self.effectives[book_name][item_id]:
                            self.effectives[book_name][item_id]["snippet"] = ""
                            self.effectives[book_name][item_id]["snippet-lang"] = self.canonical_ext[ext]
                        basename = os.path.basename(filename)
                        with open(filename, "r") as infile:
                            self.effectives[book_name][item_id]["snippet"] += "{} {}\n{}\n".format(self.comment_style[ext], basename, infile.read())
                    else:
                        logging.info("effective snippet {} does not match an item".format(filename))
        return

    def create(self, filename):
        category = self.infer_category(filename)
        if category in self.templates:
            default_categories = ["notes", "about", "posts"]
            if category in default_categories:
                self.render_default_category(category, filename)
            elif category == "emcpp":
                self.render_effective_category(category, filename)
            else:
                logging.error(f"unknown category {category} file {filename}")
        return

    def create_files(self, infiles):
        for filename in infiles:
            self.create(filename)
        
        def item_id_to_filename(item_id, ext):
            return "it{}{}".format(item_id, ext)

        # produce effective series
        for book_name in self.effectives:
            dest_folder = os.path.join(self.target_path, self.templates["emcpp"]["dest"], book_name)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            table_of_content = {}
            
            # produce individual items pages
            for item_id in self.effectives[book_name]:
                item = self.effectives[book_name][item_id]
                dest_file = os.path.join(dest_folder, item_id_to_filename(item_id, ".md"))
                with open(dest_file, "w") as outfile:
                    outfile.write("# {}\n".format(item["title"]))
                    outfile.write(item["content"] + "\n")
                    if "snippet" in item:
                        outfile.write("Snippet:\n```{}\n{}\n```\n".format(item["snippet-lang"], item["snippet"]))
                logging.info("rendered {} from effective {} items".format(dest_file, book_name))
                table_of_content[item_id] = item["title"]
            
            table_of_content_text = ""
            for item_id in sorted(table_of_content.keys()):
                table_of_content_text += "* [{}]({})\n".format(table_of_content[item_id], "/effectives/{}/{}".format(book_name, item_id_to_filename(item_id, "/")))
            # produce table-of-content pages
            table_of_content_dir = os.path.join(self.target_path, self.templates["emcpp"]["tocdest"])
            table_of_content_page = os.path.join(table_of_content_dir, "{}.md".format(book_name))
            with open(table_of_content_page, "w") as outfile:
                rendered = self.templates["emcpp"]["template"].render(title=self.cannonical_book_name[book_name], content=table_of_content_text)
                outfile.write(rendered)
            logging.info("rendered table of content {} from effective {} items".format(table_of_content_page, book_name))
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
