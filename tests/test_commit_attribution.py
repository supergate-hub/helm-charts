import unittest

from scripts.check_commit_attribution import allowed_author


class CommitAttributionTests(unittest.TestCase):
    def test_organization_identities_and_automation_are_allowed(self):
        for email in ("jh.byun@supergate.cc", "skim@supergate.cc",
                      "237438496+supergate-jhbyun@users.noreply.github.com",
                      "41898282+github-actions[bot]@users.noreply.github.com",
                      "github-actions[bot]@users.noreply.github.com",
                      "49699333+dependabot[bot]@users.noreply.github.com"):
            self.assertTrue(allowed_author(email), email)

    def test_personal_and_lookalike_addresses_are_rejected(self):
        for email in ("awbrg789@naver.com", "someone@gmail.com", "",
                      "attacker@supergate.cc.example.com", "x@supergate.cc ",
                      "1+jaehanbyun@users.noreply.github.com",
                      "1+supergate-jhbyun@users.noreply.github.com.example.com", None):
            self.assertFalse(allowed_author(email), email)


if __name__ == "__main__":
    unittest.main()
