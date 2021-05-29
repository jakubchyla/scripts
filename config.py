#! /usr/bin/env python3

import argparse
import json
import os
import pathlib
import random
import shutil
import string
import sys
from typing import Dict, List


class Config:
    def __init__(self, arguments: argparse.Namespace) -> None:

        self.arguments: argparse.Namespace = arguments
        # add '/' to end of path
        self.db_path: str = os.path.join(arguments.db, "")
        if self.db_path is None or self.db_path == "":
            print("DB can't be empty", file=sys.stderr)
            sys.exit(-1)

        self.config: List[Dict[str, str]] = self.read_from_db()
        self.commands = {
            "add": self.add_to_db,
            "rm" : self.remove_from_db,
            "ls" : self.list_db,
            "ln" : self.link
        }

    @staticmethod
    def generate_name() -> str:
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    def read_from_db(self) -> List[Dict[str, str]]:
        try:
            with open(self.db_path + "config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("config.json not found", file=sys.stderr)
            sys.exit(-1)

    def write_to_db(self, config: List[Dict[str, str]]) -> None:
        with open(self.db_path + "config.json", "w") as f:
            json.dump(config, f, indent=2)

    def add_to_db(self) -> None:
        name = self.arguments.name
        # check if name defined in arguments
        if name is None or name == "":
            # generate new name
            while True:
                name = self.generate_name()
                if name not in [entry["name"] for entry in self.config]:
                    break

        # check if name already in db
        if name in [entry["name"] for entry in self.config]:
            raise KeyError(f"entry with {name} name already present")

        # check if dest path defined in arguments
        dest = str(pathlib.Path(self.arguments.dest))
        if dest is None or dest == "":
            raise ValueError("DEST can't be empty")
        # check if entry with dest path already in db
        if dest in [entry["dest"] for entry in self.config]:
            raise KeyError(f"entry with {self.arguments.dest} PATH already present")

        # copy source if exists, exit otherwise
        try:
            db_file = self.db_path + name
            src_file = pathlib.Path(self.arguments.src).expanduser()
            shutil.copyfile(str(src_file), db_file)
        except FileNotFoundError:
            print(f"file does not exist", file=sys.stderr)
            sys.exit(-1)

        # add entry to config file
        self.config.append({
            "name": name,
            "dest": dest
        })
        self.write_to_db(self.config)

    def remove_from_db(self) -> None:
        # search for entry and remove if exists otherwise exit
        for entry in self.config:
            if entry["name"] == self.arguments.name:
                os.remove(self.db_path + entry["name"])
                self.config.remove(entry)
                self.write_to_db()
                return

        print(f"entry {self.arguments.name} does not exist", file=sys.stderr)
        sys.exit(-1)

    # link all files in db
    def link(self) -> None:
        for entry in self.config:
            symlink_location = pathlib.Path(entry["dest"]).expanduser()
            db_file = pathlib.Path(self.db_path + entry["name"])
            
            # create all dirs in path if missing
            #TODO check if dir/link/file
            if not symlink_location.parent.exists():
                symlink_location.parent.mkdir(parents=True)
            
            if os.path.lexists(str(symlink_location)):
                os.remove(str(symlink_location))

            symlink_location.symlink_to(db_file)

    # print all entries in db
    def list_db(self) -> None:
        for entry in self.config:
            print(f"{entry['name']} : {entry['dest']}")

    # execute command from cli arguments
    def exec_command(self) -> None:
        self.commands.get(self.arguments.command, lambda: 'Invalid')()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Symlink config files from repo to local system.")
    parser.add_argument("db", metavar="DB", help="path to directory with config files")
    subparsers = parser.add_subparsers(help="sub-commands", dest="command", required=True)

    # parser for add command
    parser_add = subparsers.add_parser("add", help="add file to database")
    parser_add.add_argument("--name", "-n", help="specify name for file")
    parser_add.add_argument("src", metavar="SRC", help="file to be copied to database")
    parser_add.add_argument("dest", metavar="DEST", help="linking destination")

    # parser for remove command
    parser_remove = subparsers.add_parser("rm", help="remove file from database")
    parser_remove.add_argument("name", metavar="NAME", help="file to be removed")

    # parser for listing
    parser_list = subparsers.add_parser("ls", help="list entries from database")

    # parser for linking
    parser_link = subparsers.add_parser("ln", help="link entries from database")

    return parser.parse_args()


def main():
    Config(parse_args()).exec_command()


if __name__ == "__main__":
    main()
