"""Literature adapter tests with deterministic mocked API responses. No network."""
import json
import tempfile
import unittest
from pathlib import Path
from adapters.literature import search, write_bundle
from core.contracts import validate

OA={"results":[{"id":"https://openalex.org/W1","display_name":"A sensor method",
               "doi":"https://doi.org/10.1234/TEST","publication_year":2024},
              {"id":"https://openalex.org/W2","display_name":"Another method",
               "doi":None,"publication_year":2025}]}
CR={"message":{"items":[{"title":["A sensor method"],"DOI":"10.1234/test",
                "published":{"date-parts":[[2024]]},"URL":"https://doi.org/10.1234/test"},
               {"title":["Third method"],"DOI":"10.5555/xyz",
                "published":{"date-parts":[[2026]]}}]}}

class LiteratureTests(unittest.TestCase):
    def fetcher(self,provider,query,limit,api_key=None):
        self.assertIn("sensor",query)
        self.assertEqual(limit,4)
        return OA if provider=="openalex" else CR

    def test_doi_normalization_and_provenance(self):
        bundle=search("sensor method",limit=4,fetcher=self.fetcher)
        self.assertEqual(len(bundle["records"]),3)
        same=bundle["records"][0]
        self.assertEqual(same["doi"],"10.1234/test")
        self.assertEqual(same["sources"],["openalex","crossref"])
        self.assertEqual(same["verification"],"METADATA_ONLY")
        validate("evidence",bundle)

    def test_partial_provider_failure_is_explicit(self):
        def fetch(p,q,n,api_key=None):
            if p=="openalex": raise RuntimeError("429 limit")
            return CR
        bundle=search("sensor method",limit=4,fetcher=fetch)
        self.assertEqual(bundle["sources_checked"],["crossref"])
        self.assertEqual(bundle["source_errors"][0]["provider"],"openalex")
        self.assertEqual(len(bundle["records"]),2)

    def test_all_provider_failure_is_error_not_fake_success(self):
        def fail(*args,**kwargs):
            raise RuntimeError("network unavailable")
        with self.assertRaisesRegex(RuntimeError,"No usable provider"):
            search("sensor method",limit=4,fetcher=fail)

    def test_bounded_query(self):
        with self.assertRaises(ValueError):
            search("x",fetcher=self.fetcher)
        with self.assertRaises(ValueError):
            search("sensor",limit=100,fetcher=self.fetcher)

    def test_output_no_implicit_overwrite(self):
        bundle=search("sensor method",limit=4,fetcher=self.fetcher)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"EVIDENCE.json"
            write_bundle(path,bundle)
            self.assertEqual(json.loads(path.read_text())["verification"],"METADATA_ONLY")
            with self.assertRaises(FileExistsError):
                write_bundle(path,bundle)
            write_bundle(path,bundle,overwrite=True)
            validate("evidence",json.loads(path.read_text()))

if __name__=="__main__":
    unittest.main()
