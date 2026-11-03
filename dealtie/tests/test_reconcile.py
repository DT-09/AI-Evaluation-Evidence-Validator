import unittest
from dealtie.reconcile import reconcile

class ReconcileTests(unittest.TestCase):
    def row(self,doc,value,unit="USD m"):
        return {"document":doc,"metric":"Revenue","period":"FY2025","value":value,"unit":unit,"source_ref":"p.1"}
    def test_tied(self):
        self.assertEqual(reconcile([self.row("CIM","100"),self.row("QoE","100.00")])[0]["status"],"TIED")
    def test_value_mismatch(self):
        self.assertEqual(reconcile([self.row("CIM","100"),self.row("QoE","98")])[0]["status"],"VALUE_MISMATCH")
    def test_unit_mismatch(self):
        self.assertEqual(reconcile([self.row("CIM","100"),self.row("Model","100","EUR m")])[0]["status"],"UNIT_MISMATCH")
    def test_missing(self):
        self.assertEqual(reconcile([self.row("CIM",""),self.row("QoE","100")])[0]["status"],"MISSING_OR_NON_NUMERIC")
    def test_single_source(self):
        self.assertEqual(reconcile([self.row("CIM","100")])[0]["status"],"INSUFFICIENT_COVERAGE")

if __name__=="__main__": unittest.main()
