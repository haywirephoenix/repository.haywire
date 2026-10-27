"""update_repo.py tests. Run: python -m unittest discover tests"""
import hashlib
import os
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import update_repo  # noqa: E402


def addon_zip(folder, addon_id, version, icon=b"PNG"):
    path = os.path.join(folder, "{}-{}.build.zip".format(addon_id, version))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<addon id="{0}" name="{0}" version="{1}">'
           '<extension point="xbmc.addon.metadata"><assets><icon>resources/icon.png</icon></assets></extension>'
           '</addon>').format(addon_id, version)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("{}/addon.xml".format(addon_id), xml)
        z.writestr("{}/resources/icon.png".format(addon_id), icon)
    return path


class UpdateRepoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.zips = os.path.join(self.tmp, "zips")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_add_index_and_prune(self):
        for version in ("1.0.0", "1.2.0", "1.10.0"):
            update_repo.add(addon_zip(self.tmp, "plugin.video.a", version), self.zips)
        update_repo.add(addon_zip(self.tmp, "script.b", "0.1.0"), self.zips)
        # Newest first, numbers compared as numbers, only KEEP versions left.
        self.assertEqual(update_repo.published(self.zips), {"plugin.video.a": ["1.10.0", "1.2.0"], "script.b": ["0.1.0"]})
        folder = os.path.join(self.zips, "plugin.video.a")
        self.assertFalse(os.path.exists(os.path.join(folder, "plugin.video.a-1.0.0.zip")))
        zip_path = os.path.join(folder, "plugin.video.a-1.10.0.zip")
        with open(zip_path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        with open(zip_path + ".sha256") as f:
            self.assertEqual(f.read().strip(), digest)
        self.assertTrue(os.path.exists(os.path.join(folder, "resources", "icon.png")))  # the asset, for the browser

        self.assertEqual(update_repo.index(self.zips), ["plugin.video.a", "script.b"])
        with open(os.path.join(self.zips, "addons.xml"), "rb") as f:
            xml = f.read()
        addons = ET.fromstring(xml)
        self.assertEqual([(a.get("id"), a.get("version")) for a in addons], [("plugin.video.a", "1.10.0"), ("script.b", "0.1.0")])
        with open(os.path.join(self.zips, "addons.xml.md5")) as f:
            self.assertEqual(f.read(), hashlib.md5(xml).hexdigest())

    def test_rejects_a_zip_without_its_folder(self):
        path = os.path.join(self.tmp, "flat.zip")
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("addon.xml", '<addon id="x" version="1"/>')
        with self.assertRaises(ValueError):
            update_repo.add(path, self.zips)

    def test_pack_the_repository_addon(self):
        addon_id, version = update_repo.pack(os.path.join(ROOT, "repository.haywire"), self.zips)
        self.assertEqual(addon_id, "repository.haywire")
        with zipfile.ZipFile(os.path.join(self.zips, addon_id, "{}-{}.zip".format(addon_id, version))) as z:
            self.assertIn("repository.haywire/addon.xml", z.namelist())

    def test_version_order(self):
        versions = ["1.2.0", "1.10.0", "1.2.0~beta1", "0.9"]
        self.assertEqual(sorted(versions, key=update_repo.version_key), ["0.9", "1.2.0~beta1", "1.2.0", "1.10.0"])


if __name__ == "__main__":
    unittest.main()
