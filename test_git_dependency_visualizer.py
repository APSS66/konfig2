#!/usr/bin/python
import unittest
from unittest.mock import MagicMock, patch, mock_open, create_autospec
import git_dependency_vizualizer


class test_visualizer(unittest.TestCase):

    @patch('sys.argv', new=['script_name', 'path/to/visualizer', 'path/to/repo', '2023-10-10'])
    def test_parse_arguments_valid(self):
        result = git_dependency_vizualizer.parse_arguments()
        expected = ['path/to/visualizer', 'path/to/repo', '2023-10-10']
        self.assertEqual(result, expected)

    @patch('sys.argv', new=['script_name'])
    def test_parse_arguments_invalid(self):
        with self.assertRaises(SystemExit):
            git_dependency_vizualizer.parse_arguments()

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('sys.exit')
    def test_validate_arguments_valid(self, mock_exit, mock_isfile, mock_isdir):
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        arguments = ['path/to/file', 'path/to/directory', '2023-10-10']
        git_dependency_vizualizer.validate_arguments(arguments)
        mock_exit.assert_not_called() 

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('sys.exit')
    def test_validate_arguments_invalid_file(self, mock_exit, mock_isfile, mock_isdir):
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        arguments = ['path/to/file', 'path/to/directory', '2023-10-10']
        with self.assertRaises(SystemExit):
            git_dependency_vizualizer.validate_arguments(arguments)

    @patch('builtins.open', new_callable=mock_open, read_data=b'x78x9cx4bx4cx4ex55x00x00x00x00')
    @patch('zlib.decompress')
    def test_parse_one_commit(self, mock_decompress, mock_open):
        mock_decompress.return_value = b'commit 123456\nSome commit message'
        result = git_dependency_vizualizer.parse_one_commit('path/to/repo', '1234567890abcdef')
        expected = ['1234567890abcdef', 'commit 123456', 'Some commit message']
        self.assertEqual(result, expected)

    def test_parse_commits(self):
        commits = [
            ['abcd1234', 'data', 'parent_hash_1', 'some info', 'Author Name <email@example.com> 1622548800 +0000'],
            ['efgh5678', 'data', 'parent_hash_2', 'parent_hash_3', 'some_info', 'Author Name <email@example.com> 1622548800 +0000']
        ]
        result = git_dependency_vizualizer.parse_commits(commits)
        expected_result = [
            ['abcd1234', 'parent_hash_1', 1622548800, '+0000'],
            ['efgh5678', 'parent_hash_2', 'parent_hash_3', 1622548800, '+0000']
        ]
        self.assertEqual(result, expected_result)

    def test_filter_commits(self):
            commits = [
                ['abcd1234', 'parent_hash_1', 'second_parent_1', '1622548800', '+0000'],
                ['efgh5678', 'parent_hash_2', 'second_parent_2', '1622548800', '+0300'],
                ['ijkl9012', 'parent_hash_3', 'second_parent_3', '1622548800', '-0500']
            ]
            target_date = "1945-05-31"
            result = git_dependency_vizualizer.filter_commits(commits, target_date)
            self.assertEqual(len(result), 3)
            target_date = "2030-01-31"
            result = git_dependency_vizualizer.filter_commits(commits, target_date)
            self.assertEqual(len(result), 0)

    @patch('builtins.open', new_callable=mock_open)
    def test_build_graphiz(self, mock_file):
        commits = [
            ['abcd1234', 'parent_hash_1', 'second_parent_1', 'data', 'Author Name <email@example.com>'],
            ['efgh5678', 'abcd1234',  'data', 'Author Name <email@example.com>'],
            ['ijkl9012', 'efgh5678',  'data', 'Author Name <email@example.com>']
        ]
        git_dependency_vizualizer.build_graphiz(commits)
        expected_output = """digraph G {
                                rankdir=TB;
                                node [shape=circle];
                commit1 [label="abcd12"];
                commit2 [label="parent_hash_1"];
                commit3 [label="efgh56"];
                commit4 [label="ijkl90"];
                commit2 -> commit1;
                commit3 -> commit2;
                commit4 -> commit3;
            }"""
        mock_file().write.assert_called_once()

    @patch('subprocess.run')
    def test_start_vizual(self, mock_subprocess):
        graph_visualizer_path = "path/to/graph_visualizer"
        git_dependency_vizualizer.start_vizual(graph_visualizer_path)
        mock_subprocess.assert_called_once_with([graph_visualizer_path, "./git.dot"])


if __name__ == "__main__":
    unittest.main()
