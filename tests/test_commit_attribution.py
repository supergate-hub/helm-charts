import unittest

from scripts.check_commit_attribution import LEGACY_HEAD, allowed_author, clean_message


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

    def test_co_author_trailers_are_rejected_in_any_casing(self):
        self.assertTrue(clean_message("feat: add\n\nbody"))
        for message in ("feat: add\n\nCo-authored-by: a <a@supergate.cc>",
                        "feat: add\n\nco-authored-by: a <a@supergate.cc>",
                        "feat: add\n\n  Co-Authored-By: Claude <noreply@anthropic.com>"):
            self.assertFalse(clean_message(message), message)

    def test_boundary_is_a_full_commit_id(self):
        self.assertRegex(LEGACY_HEAD, r"^[a-f0-9]{40}$")


if __name__ == "__main__":
    unittest.main()
