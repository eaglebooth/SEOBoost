import unittest


class EscrowModel:
    def __init__(self):
        self.balance = 0
        self.released = 0
        self.refunded = 0
        self.campaigns = []

    def create(self, client, agency, reward):
        if not client or not agency or reward <= 0:
            raise ValueError("invalid funded campaign")
        self.campaigns.append({"client": client, "agency": agency, "reward": reward, "status": "FUNDED"})
        self.balance += reward
        return len(self.campaigns) - 1

    def release(self, campaign_id):
        campaign = self.campaigns[campaign_id]
        if campaign["status"] != "APPROVED":
            raise ValueError("NOT_APPROVED")
        self.balance -= campaign["reward"]
        self.released += campaign["reward"]
        campaign["status"] = "PAID"

    def refund(self, campaign_id, caller, revision_expired=False):
        campaign = self.campaigns[campaign_id]
        if caller != campaign["client"]:
            raise ValueError("CLIENT_ONLY")
        rejected = campaign["status"] == "REJECTED"
        expired_revision = campaign["status"] == "NEEDS_REVIEW" and revision_expired
        if not rejected and not expired_revision:
            raise ValueError("NOT_REFUNDABLE")
        self.balance -= campaign["reward"]
        self.refunded += campaign["reward"]
        campaign["status"] = "REFUNDED"


class FundedLifecycleTests(unittest.TestCase):
    def test_approved_campaign_conserves_value_and_pays_once(self):
        model = EscrowModel()
        campaign_id = model.create("client", "agency", 250)
        self.assertEqual(model.balance, 250)
        model.campaigns[campaign_id]["status"] = "APPROVED"
        model.release(campaign_id)
        self.assertEqual((model.balance, model.released, model.refunded), (0, 250, 0))
        with self.assertRaisesRegex(ValueError, "NOT_APPROVED"):
            model.release(campaign_id)

    def test_rejected_campaign_refunds_only_recorded_client(self):
        model = EscrowModel()
        campaign_id = model.create("client", "agency", 400)
        model.campaigns[campaign_id]["status"] = "REJECTED"
        with self.assertRaisesRegex(ValueError, "CLIENT_ONLY"):
            model.refund(campaign_id, "agency")
        model.refund(campaign_id, "client")
        self.assertEqual((model.balance, model.released, model.refunded), (0, 0, 400))

    def test_unsettled_campaign_cannot_leak_escrow(self):
        model = EscrowModel()
        campaign_id = model.create("client", "agency", 125)
        with self.assertRaisesRegex(ValueError, "NOT_APPROVED"):
            model.release(campaign_id)
        with self.assertRaisesRegex(ValueError, "NOT_REFUNDABLE"):
            model.refund(campaign_id, "client")
        self.assertEqual(model.balance, 125)

    def test_expired_revision_window_returns_escrow_to_client(self):
        model = EscrowModel()
        campaign_id = model.create("client", "agency", 300)
        model.campaigns[campaign_id]["status"] = "NEEDS_REVIEW"
        with self.assertRaisesRegex(ValueError, "NOT_REFUNDABLE"):
            model.refund(campaign_id, "client")
        model.refund(campaign_id, "client", revision_expired=True)
        self.assertEqual((model.balance, model.released, model.refunded), (0, 0, 300))


if __name__ == "__main__":
    unittest.main()
