import argparse
import json
import os
import re
from collections import defaultdict


class RoamGenerator:

    def __init__(self, markdown_path, clippings_path, header_path):
        """
        :param markdown_path: str, path for saving md files
        :param clippings_path: str, path for downloading the clippings file
        :param header_path: str, path for custom page header
        """
        self.clippings = ""
        self.page_header = self.read_header(header_path)
        self.clippings_list = list()
        self.diff = defaultdict(list)
        self.markdown_path = markdown_path
        self.existing_database = self.load_database()
        self.clippings_path = clippings_path

    def read_header(self, header_path):
        """
        Reads header template for the page.
        """
        with open(header_path, 'r') as f:
            page_header = f.read()
        return page_header

    def load_database(self, database_path="database.json"):
        """
        Loads the database with existing notes.
        :param database_path: str, existing database path
        :return: dict, parsed database
        """
        if os.path.isfile(database_path):
            with open(database_path, 'r') as f:
                database = json.load(f)
        else:
            database = defaultdict(list)
        return self.deserialize_tuples(database)

    def dump_database(self, db, database_path="database.json"):
        """
        Dumps database to json file.
        :param db: dict, database ready to be saved into file
        :param database_path: str, path for saving the database
        """
        serialized_db = self.serialize_tuples(db)
        with open(database_path, 'w') as f:
            json.dump(serialized_db, f)

    def read_clippings(self):
        """
        Reads clippings directly from Kindle.
        """
        with open(self.clippings_path, 'r', encoding='utf-8') as f:
            self.clippings = f.read()

    def clear_clippings(self):
        """
        Gets rid of rubbish in clippings.
        """
        self.clippings_list = [s.strip('\n').strip('\ufeff') for s in self.clippings.split('==========')]

    def process_clippings(self):
        """
        Populates diff and database dictionaries with new data.
        """
        for note in self.clippings_list:
            header = note.split('\n')[0]
            title = header.split(" (")[0]
            r = re.search(r'(?<=\()[^.]*', header[:-1])
            author = r.group() if r else ''

            page_name = (title, author)
            if "Ваш выделенный отрывок в месте" or "Your Highlight at location" in note:
                text = note.split('\n\n')[-1]

                self.existing_database = self.update_db(self.existing_database, page_name, text)
                if page_name not in self.diff or text not in self.diff[page_name]:
                    self.diff = self.update_db(self.diff, page_name, text)

    @staticmethod
    def update_db(db, page_name, text):
        """
        Adds a note to the database.
        :param db: dict, existing notes database
        :param page_name: str, page title
        :param text: str, page text
        :return: db: dict, updated database
        """
        previous_chunk = db[page_name][-1].strip("\n").strip("- ") if db[page_name] else ""

        if previous_chunk.endswith(text):
            return db
        elif previous_chunk and text.startswith(previous_chunk.strip("- ")):
            del db[page_name][-1]
        db[page_name].append(f"- {text}\n")
        return db

    @staticmethod
    def deserialize_tuples(parsed_json):
        """
        Converts strings in json keys to tuples.
        :param parsed_json: json dict loaded from file
        :return: dict, database with tuples as values
        """
        dict_json = defaultdict(list)
        for key, value in parsed_json.items():
            key = eval(key)
            dict_json[key] = value
        return dict_json

    @staticmethod
    def serialize_tuples(dictionary):
        """
        Converts tuples in json keys to strings.
        :param dictionary: existing dict with notes database
        :return: dumpable json
        """
        str_json = defaultdict(list)
        for key, value in dictionary.items():
            key = str(key)
            str_json[key] = value
        return str_json

    def diff_to_markdown(self, markdown_path):
        """
        Dumps difference to markdown files.
        :param markdown_path: str, path for saving md files
        """
        if not os.path.exists(markdown_path):
            os.makedirs(markdown_path)
        # print("DIFF ", self.diff)
        for book, note in self.diff.items():
            page_title = book[0]
            author = book[1]
            note = ''.join(note)
            content = self.page_header.format(author=author, note=note)
            page_title = re.sub("[<>’‘]", "'", page_title)
            page_title = re.sub("[:|#?]", "", page_title)
            with open(os.path.join(markdown_path, f"{page_title}.md"), 'w', encoding='utf-8') as f:
                f.write(content)
        print("Diff dumped to Markdown.")

    def run(self):
        """
        Runs the whole pipeline.
        """
        print("Start running...")
        self.read_clippings()
        self.clear_clippings()
        self.process_clippings()
        self.diff_to_markdown(self.markdown_path)
        self.dump_database(self.existing_database)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clippings_path', type=str, nargs='?',
                        default="/Volumes/Kindle/documents/My Clippings.txt",
                        help='clippings path')
    parser.add_argument('--markdown_path', type=str, nargs='?', default="markdown",
                        help='path for saving markdown files')
    parser.add_argument('--header_path', type=str, nargs='?', default="header.txt",
                        help='path to custom header file')
    args = parser.parse_args()
    generator = RoamGenerator(args.markdown_path, args.clippings_path, args.header_path)
    generator.run()
