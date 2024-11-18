#!/usr/bin/python
import subprocess
import os
import zlib
import argparse
from datetime import datetime, timezone, timedelta


DOT_FILENAME = "./git.dot"


def parse_arguments() -> list:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("graph_visualizer_path")
        parser.add_argument("repo_path")
        parser.add_argument("target_date")
        arguments = parser.parse_args()
        result = [arguments.graph_visualizer_path, arguments.repo_path, arguments.target_date]
        return result
    except Exception:
        print("Некорректное число агрументов")
        exit(1)


def validate_arguments(arguments: list):
    if not (os.path.isfile(arguments[0]) and os.path.isdir(arguments[1])):
        print("Некорректные пути к файлам")
        exit(1)
    date_format = "%Y-%m-%d"
    try:
        datetime.strptime(arguments[2], date_format)
    except Exception:
        print("Некорректный формат даты")
        exit(1)


def parse_one_commit(repo: str, commit: str) -> list:
    path_to_commit = os.path.join(repo, 'objects', commit[:2], commit[2:])
    with open(path_to_commit, 'rb') as f:
        try:
            data = zlib.decompress(f.read())
            correct_data = data.decode('utf-8')
            correct_data = commit + '\n' + correct_data
            parsed_data = correct_data.split('\n')
            if "commit" in correct_data and "blob" not in correct_data:
                return parsed_data
            else:
                return []
        except Exception:
            return []


def get_all_commits(repo: str) -> list:
    all_commits = []
    cnt = 0
    objects_path = os.path.join(repo, 'objects')
    for root, dirs, files in os.walk(objects_path):
        for dir in dirs:
            if len(dir) == 2:
                object_dir = os.path.join(objects_path, dir)
                for root_l, dirs_l, files_l in os.walk(object_dir):
                    for file in files_l:
                        commit_hash = dir + file
                        res = parse_one_commit(repo, commit_hash)
                        if res != []:
                            cnt += 1
                            all_commits.append(res)
    return all_commits


def parse_commits(commits: list) -> list:
    parsed_commits = []
    for commit in commits:
        commit_hash = commit[0]
        parent = commit[2][-40:]
        i = 3
        if "parent" in commit[3]:
            i += 1
            second_parent = commit[3][-40:]
        commiter_info = commit[i+1].split(" ")
        commit_date = int(commiter_info[-2])
        commit_timezone = commiter_info[-1]
        commit_info = []
        commit_info.append(commit_hash)
        commit_info.append(parent)
        if i == 4:
            commit_info.append(second_parent)
        commit_info.append(commit_date)
        commit_info.append(commit_timezone)
        parsed_commits.append(commit_info)
    return parsed_commits


def filter_commits(commits: list, target_date: str) -> list:
    filtered_commits = []
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    target_timestamp = int(target_date_obj.timestamp())
    for commit in commits:
        timestamp = int(commit[-2])
        timezone_offset = commit[-1]
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        offset_hours = int(timezone_offset[:3])
        offset_minutes = int(timezone_offset[0] + timezone_offset[3:])
        dt += timedelta(hours=offset_hours, minutes=offset_minutes)
        if int(dt.timestamp()) >= target_timestamp:
            filtered_commits.append(commit)
    return filtered_commits


def build_graphiz(commits: list):
    commit_dict = dict()
    commit_links = set()
    result = """digraph G {
                rankdir=TB;
                node [shape=circle];\n"""
    i = 1
    for commit in commits:
        if commit[0] not in commit_dict:
            commit_dict[commit[0]] = f"commit{i}"
            i += 1
        if commit[1] not in commit_dict:
            commit_dict[commit[1]] = f"commit{i}"
            i += 1
        commit_links.add((commit_dict[commit[1]], commit_dict[commit[0]]))
        if len(commit) == 5:
            if commit[2] not in commit_dict:
                commit_dict[commit[2]] = f"commit{i}"
                i += 1
            commit_links.add((commit_dict[commit[2]], commit_dict[commit[0]]))
    for k, v in commit_dict.items():
        result += f"{v} [label=\"{k[:6]}\"];\n"
    result += '\n'
    for x in commit_links:
        frm, t = x
        result += f"{frm} -> {t};\n"
    result += '}'
    with open("git.dot", 'w') as file:
        file.write(result)


def start_vizual(graph_visualizer_path: str):
    subprocess.run([graph_visualizer_path, DOT_FILENAME])


if __name__ == '__main__':
    arguments = parse_arguments()
    all_commits = get_all_commits(arguments[1])
    parsed_commits = parse_commits(all_commits)
    filtered_commits = filter_commits(parsed_commits, arguments[2])
    build_graphiz(filtered_commits)
    start_vizual(arguments[0])
