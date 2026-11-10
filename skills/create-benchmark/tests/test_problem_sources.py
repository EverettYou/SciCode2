"""Direct problem provenance must remain local, immutable and traceable."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

path=Path(__file__).resolve().parents[1]/'scripts/validate_benchmark.py'
spec=importlib.util.spec_from_file_location('benchmark_validator',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ProblemProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'problem').mkdir();(self.root/'problem/question.pdf').write_bytes(b'fixed question')
        self.metadata={'problem_sources':[{'path':'problem/question.pdf','sha256':hashlib.sha256(b'fixed question').hexdigest(),'origin':'supplied by user'}],'idea_sources':[{'source_path':'problem/question.pdf','source_field':'user-provided-research-question','role':'primary-question'}]}
    def tearDown(self):self.tmp.cleanup()
    def test_unchanged_question_accepted(self):
        errors=[];module.validate_problem_sources(errors,self.metadata,self.root);self.assertEqual(errors,[])
    def test_changed_question_rejected(self):
        (self.root/'problem/question.pdf').write_bytes(b'different question')
        errors=[];module.validate_problem_sources(errors,self.metadata,self.root);self.assertTrue(any('sha256' in e for e in errors))
    def test_escape_and_empty_paths_rejected(self):
        for path in ['../question.pdf','/tmp/question.pdf','.','']:
            with self.subTest(path=path):
                self.metadata['problem_sources'][0]['path']=path
                errors=[];module.validate_problem_sources(errors,self.metadata,self.root);self.assertTrue(errors)
if __name__=='__main__':unittest.main()
