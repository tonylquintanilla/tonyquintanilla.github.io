"""patch_L272_1_gallery_readme.py -- L-272. Create the gallery repo's README.

RUN COMMAND
-----------
Save this file into the GALLERY repo root (the folder holding
interactive.html and gallery_maintenance_run.py), open it in VS Code, and
click Run.

    python patch_L272_1_gallery_readme.py

    *** This is the OTHER repository, not the orrery. ***

WHAT IT DOES
------------
Creates README.md. That repository has never had one: someone landing on
it from the site sees a file listing and nothing else.

The new file describes only what is in the gallery repository -- the two
galleries, the served-cache chain, the maintenance runner and its
UNREACHABLE state, the .nojekyll requirement, and the layout -- and points
at the orrery repo for everything about the project itself.

It refuses to run if a README.md already exists. It never overwrites.

WHAT IS PERMANENT
-----------------
README.md. This script is one-shot; archive it into documentation/ once
it has run.

NO BACKUP FILE
--------------
Per safe-file-editing 1.10. Nothing is being replaced here in any case.

Role: patch
Domain: dev_tools

Module created: August 31, 2026 with Anthropic's Claude Opus 5.
"""

import base64
import hashlib
import os
import sys

NEW_MD5 = "cc417c690b405a2e6023beb459766961"
TARGET = "README.md"

NEW_B64 = (
    "IyBQYWxvbWEncyBPcnJlcnkgLS0gV2ViIEdhbGxlcnkKCioqVG9ueSBRdWludGFuaWxsYSwgUEUg"
    "fCBBbnRocm9waWMncyBDbGF1ZGUgT3B1cyA1IHwgQXVndXN0IDMxLCAyMDI2KioKCldyaXR0ZW4g"
    "dW5kZXIgb3JyZXJ5IGxlZGdlciBoYW5kbGUgTC0yNzIuIEN1dCBmcm9tIGAyZWQxMjU2NGAgYXQK"
    "aHR0cHM6Ly9naXRodWIuY29tL3RvbnlscXVpbnRhbmlsbGEvdG9ueXF1aW50YW5pbGxhLmdpdGh1"
    "Yi5pbyAoYnJhbmNoCm1haW4pLiBUaGUgYW5jaG9yIG5hbWVzIHRoZSBzdGF0ZSB0aGlzIGZpbGUg"
    "d2FzIHdyaXR0ZW4gYWdhaW5zdCwgbm90IGEKcHJvbWlzZSB0aGUgcmVwb3NpdG9yeSBzdGlsbCBz"
    "aXRzIHRoZXJlLgoKKipXaGF0IHRoaXMgZmlsZSBpcy4qKiBUaGUgZnJvbnQgZG9vciBmb3IgdGhl"
    "IGdhbGxlcnkgcmVwb3NpdG9yeS4gSXQKZGVzY3JpYmVzIG9ubHkgd2hhdCBpcyBpbiAqdGhpcyog"
    "cmVwb3NpdG9yeTsgdGhlIHByb2plY3QgaXRzZWxmIGlzCmRlc2NyaWJlZCBpbiB0aGUgb3RoZXIg"
    "b25lLgoKLS0tCgpUaGlzIHJlcG9zaXRvcnkgaXMgdGhlIHB1Ymxpc2hlZCB3ZWIgc3VyZmFjZSBv"
    "ZgoqKltQYWxvbWEncyBPcnJlcnldKGh0dHBzOi8vZ2l0aHViLmNvbS90b255bHF1aW50YW5pbGxh"
    "L3BhbG9tYXNfb3JyZXJ5KSoqLAphbiBhc3Ryb25vbWljYWwgdmlzdWFsaXphdGlvbiBzdWl0ZSBi"
    "eSBUb255IFF1aW50YW5pbGxhLiBJdCBpcyBzZXJ2ZWQgYnkKR2l0SHViIFBhZ2VzIGF0ICoqW3Bh"
    "bG9tYXNvcnJlcnkuY29tXShodHRwczovL3BhbG9tYXNvcnJlcnkuY29tLykqKi4KClRoZSBhcHBs"
    "aWNhdGlvbiBpdHNlbGYgLS0gdGhlIFB5dGhvbiB0aGF0IHRhbGtzIHRvIEpQTCBIb3Jpem9ucywg"
    "Y29tcHV0ZXMKdGhlIHNjZW5lcywgYW5kIGhvbGRzIGV2ZXJ5IHBoeXNpY2FsIGNvbnN0YW50IHdp"
    "dGggaXRzIGNpdGF0aW9uIC0tIGxpdmVzIGluCnRoZSBvdGhlciByZXBvc2l0b3J5LiBTdGFydCB0"
    "aGVyZSBmb3Igd2hhdCB0aGUgcHJvamVjdCBpcywgaG93IGl0IHdvcmtzLAphbmQgdGhlIGRpc2Np"
    "cGxpbmUgdGhhdCBrZWVwcyBpdCBjb3JyZWN0OgpbcGFsb21hc19vcnJlcnkvUkVBRE1FLm1kXSho"
    "dHRwczovL2dpdGh1Yi5jb20vdG9ueWxxdWludGFuaWxsYS9wYWxvbWFzX29ycmVyeS9ibG9iL21h"
    "aW4vUkVBRE1FLm1kKS4KCiMjIFdoYXQgeW91IGNhbiByZWFjaCBmcm9tIHdoZXJlCgp8IFdoZXJl"
    "IHlvdSBhcmUgfCBXaGF0IGlzIHJlYWNoYWJsZSB8CnwtLS18LS0tfAp8ICoqcGFsb21hc29ycmVy"
    "eS5jb20qKiwgaW4gYSBicm93c2VyIHwgQm90aCBnYWxsZXJpZXMuIFRoZSBpbnRlcmFjdGl2ZSBv"
    "bmUgcnVucyB0aGUgcHJvamVjdCdzIG93biBQeXRob24gaW4geW91ciBicm93c2VyIHRocm91Z2gg"
    "UHlvZGlkZSwgc28gaXQgbmVlZHMgbm8gaW5zdGFsbCBhbmQgbm8gY2xvbmUuIFRoZSBgLm1kYCBh"
    "bmQgYC5weWAgZmlsZXMgaW4gdGhpcyByZXBvc2l0b3J5IGFyZSBub3Qgc2VydmVkIGFzIHBhZ2Vz"
    "LiB8CnwgKipnaXRodWIuY29tKiosIGluIGEgYnJvd3NlciB8IEV2ZXJ5IHRyYWNrZWQgZmlsZSBo"
    "ZXJlLCByZWFkYWJsZSB3aXRob3V0IGNsb25pbmc6IGJvdGggdmlld2VycywgdGhlIGFzc2VtYmxl"
    "ciwgdGhlIHJlbmRlcmVyLCB0aGUgc2VydmVkIGNhY2hlLCBhbmQgdGhlIHRvb2xpbmcuIFRoZSBy"
    "ZWxhdGl2ZSBsaW5rcyBpbiB0aGlzIGZpbGUgcmVzb2x2ZSBoZXJlLiB8CnwgKipBIGxvY2FsIGNs"
    "b25lLCB3aXRoIFB5dGhvbioqIHwgRXZlcnl0aGluZyBhYm92ZSwgcGx1cyBydW5uaW5nIGB0b29s"
    "cy9nYWxsZXJ5X2NhY2hlX2J1aWxkZXIucHlgIHRvIHJlYnVpbGQgdGhlIHNlcnZlZCBjYWNoZSwg"
    "YGdhbGxlcnlfbWFpbnRlbmFuY2VfcnVuLnB5YCB0byBjaGVjayBpdCwgYW5kIHRoZSBjdXJhdGlv"
    "biB0b29scy4gVGhlIGNhY2hlIGJ1aWxkZXIgbmVlZHMgbmV0d29yayBhY2Nlc3MgdG8gSlBMIEhv"
    "cml6b25zLiB8CgpUaGUgQ2xhdWRlIHByb3RvY29sIGFuZCBza2lsbHMgbGF5ZXIgZGVzY3JpYmVk"
    "IGluIHRoZSBvcnJlcnkncyBSRUFETUUKZ292ZXJucyB3b3JrIGluIHRoaXMgcmVwb3NpdG9yeSB0"
    "b28sIGJ1dCBpdCBpcyBpbnN0YWxsZWQgdG8gdGhlCmRldmVsb3BlcidzIENsYXVkZSBhY2NvdW50"
    "IHJhdGhlciB0aGFuIGtlcHQgaGVyZSAtLSB0aGVyZSBpcyBubyBjb3B5IG9mIGl0CmluIHRoaXMg"
    "cmVwbyB0byBmaW5kLgoKLS0tCgojIyBUd28gZ2FsbGVyaWVzLCBub3Qgb25lCgpUaGV5IGFyZSBk"
    "aWZmZXJlbnQgaW5zdHJ1bWVudHMgYW5kIGJvdGggYXJlIHdhbnRlZC4KCioqVGhlIGN1cmF0ZWQg"
    "Z2FsbGVyeSoqIC0tIFtgaW5kZXguaHRtbGBdKGluZGV4Lmh0bWwpLCBzZXJ2ZWQgYXQgdGhlIHNp"
    "dGUKcm9vdC4gQSBwdWJsaXNoZWQgcGljdHVyZTogdmlzdWFsaXphdGlvbnMgdGhlIGF1dGhvciBj"
    "aG9zZSwgZXhwb3J0ZWQgZnJvbQp0aGUgZGVza3RvcCBhcHAsIGV4dHJhY3RlZCB0byBsaWdodHdl"
    "aWdodCBKU09OLCBhbmQgZHJhd24gd2l0aCBQbG90bHkuanMuCkZhc3QsIGZpeGVkLCBhbmQgZXhh"
    "Y3RseSB3aGF0IHdhcyBpbnRlbmRlZC4gRWFjaCB2aXN1YWxpemF0aW9uIGhhcyBpdHMgb3duCmRp"
    "cmVjdCBsaW5rLgoKKipUaGUgaW50ZXJhY3RpdmUgZ2FsbGVyeSoqIC0tIFtgaW50ZXJhY3RpdmUu"
    "aHRtbGBdKGludGVyYWN0aXZlLmh0bWwpLAphZGRyZXNzZWQgYnkgZXhoaWJpdCwgZm9yIGV4YW1w"
    "bGUKW2BpbnRlcmFjdGl2ZS5odG1sP2V4aGliaXQ9c3VuYF0oaHR0cHM6Ly9wYWxvbWFzb3JyZXJ5"
    "LmNvbS9pbnRlcmFjdGl2ZS5odG1sP2V4aGliaXQ9c3VuKS4KQSB3b3JraW5nIGluc3RydW1lbnQg"
    "dGhlIHZpc2l0b3IgZHJpdmVzLiBUaGUgb3JyZXJ5J3Mgb3duIFB5dGhvbiBydW5zIGluCnRoZSB2"
    "aXNpdG9yJ3MgYnJvd3NlciB0aHJvdWdoIFB5b2RpZGUgYW5kIGFzc2VtYmxlcyB0aGUgc2NlbmUg"
    "bGl2ZSBhZ2FpbnN0CmEgY2FjaGVkIGRhdGFzZXQuIFRoZSBTdW4gaXMgdGhlIGZpcnN0IGV4aGli"
    "aXQ7IG1vcmUgZm9sbG93IGFzIHRoZQpyZW5kZXJpbmcgbGFkZGVyIGFkdmFuY2VzLgoKVGhlIGN1"
    "cmF0ZWQgZ2FsbGVyeSBpcyBub3QgYmVpbmcgcmV0aXJlZC4gSXQgYmVjb21lcyB0aGUgcGVkYWdv"
    "Z2ljYWwKZXhoaWJpdCBsYXllciwgYW5kIHRoZSBpbnRlcmFjdGl2ZSBwYWdlcyBncm93IGFsb25n"
    "c2lkZSBpdC4KCi0tLQoKIyMgSG93IHRoZSBpbnRlcmFjdGl2ZSBnYWxsZXJ5IHdvcmtzCgpgYGAK"
    "ICAgb2JqZWN0c19jb25maWcuanNvbiAgLT4gIGdhbGxlcnlfY2FjaGVfYnVpbGRlci5weSAgLT4g"
    "IGRhdGEvc29sYXItc3lzdGVtLwogICAoZmVhdHVyZXMsIGJ5IGhhbmQpICAgICAgKHBvc2l0aW9u"
    "cywgZnJvbSBIb3Jpem9ucykgICAgICh0aGUgc2VydmVkIGNhY2hlKQogICAgICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB8CiAgIHRo"
    "ZSBicm93c2VyICA8LSAgZmVhdHVyZV9yZW5kZXJlcnMuanMgIDwtICBnYWxsZXJ5L2Fzc2VtYmxl"
    "ci8gIDwtKwogICAgICAgICAgICAgICAgICAgIChkcmF3cykgICAgICAgICAgICAgICAgICAgKGNv"
    "bXB1dGVzLCBpbiBQeW9kaWRlKQpgYGAKCioqYHRvb2xzL2dhbGxlcnlfY2FjaGVfYnVpbGRlci5w"
    "eWAqKiBwcm9kdWNlcyB0aGUgc2VydmVkIGNhY2hlLiBJdCByZWFkcwpgZGF0YS9vYmplY3RzX2Nv"
    "bmZpZy5qc29uYCBmb3Igd2hpY2ggb2JqZWN0cyB0byBzZXJ2ZSBhbmQgd2hhdCBmZWF0dXJlcwp0"
    "aGV5IGhhdmUsIHRoZW4gcXVlcmllcyBKUEwgSG9yaXpvbnMgZm9yIGZyZXNoIHBvc2l0aW9ucy4g"
    "SXQgd3JpdGVzCmF0b21pY2FsbHkgdGhyb3VnaCBhIHN0YWdpbmcgZGlyZWN0b3J5LCBzbyBhIGZh"
    "aWxlZCBidWlsZCBsZWF2ZXMgdGhlCnByZXZpb3VzIGNhY2hlIHNlcnZpbmcgcmF0aGVyIHRoYW4g"
    "YSBoYWxmLXdyaXR0ZW4gb25lLiBJdCBpcyBydW4gYnkgaGFuZApyYXRoZXIgdGhhbiBvbiBhIHNj"
    "aGVkdWxlOiB0aGUgYnVpbGQgbmVlZHMgdGhlIGRldmVsb3BlcidzIG1hY2hpbmUgb24KYW55d2F5"
    "LCBhbmQgYSBzY2hlZHVsZWQgdGFzayBjcmVhdGVkIGFuIGFwcGVhcmFuY2Ugb2YgYXV0b21hdGlv"
    "biB0aGUgc2V0dXAKY291bGQgbm90IGRlbGl2ZXIuCgoqKmBkYXRhL3NvbGFyLXN5c3RlbS9gKiog"
    "aXMgdGhlIHNlcnZlZCBjYWNoZSAtLSBgY292ZXJhZ2VfaW5kZXguanNvbmAgKHdoYXQKaXMgYXZh"
    "aWxhYmxlIGFuZCBmb3Igd2hpY2ggZGF0ZXMpLCBgZmVhdHVyZV9jb25maWdzLmpzb25gICh0aGUg"
    "bm9uLXBvc2l0aW9uCmRhdGE6IHNoZWxscywgcmluZ3MsIGJlbHRzKSwgYHBvc2l0aW9ucy9gIGFu"
    "ZCBgcmF3L2AuCgoqKmBnYWxsZXJ5L2Fzc2VtYmxlci9gKiogaXMgdGhlIHNoYXJlZCBQeXRob24g"
    "cGFja2FnZSB0aGF0IHJ1bnMgaW4gdGhlCmJyb3dzZXIuIGBjYXRhbG9nLnB5YCBhbmQgYGNhY2hl"
    "X3JlYWRlci5weWAgcmVhZCB0aGUgc2VydmVkIGNhY2hlLApgcmVzb2x2ZXIucHlgIGRlY2lkZXMg"
    "d2hhdCBhIHNjZW5lIGNvbnRhaW5zIGFuZCB3aGV0aGVyIHRoZSByZXF1ZXN0ZWQgZGF0ZQppcyBp"
    "bnNpZGUgdGhlIHRydXN0ZWQgd2luZG93LCBhbmQgdGhlIGByZW5kZXJfKmAgbW9kdWxlcyBidWls"
    "ZCB0aGUgc2NlbmUKZGVzY3JpcHRpb24uIEl0IGlzIHN0ZGxpYi1vbmx5IGJ5IGRlc2lnbiwgc28g"
    "UHlvZGlkZSBjYW4gbG9hZCBpdCB3aXRob3V0CnB1bGxpbmcgcGFja2FnZXMuCgoqKmBnYWxsZXJ5"
    "L2ZlYXR1cmVfcmVuZGVyZXJzLmpzYCoqIHRha2VzIHRoZSBhc3NlbWJsZXIncyBmZWF0dXJlIHJl"
    "cG9ydCBhbmQKZHJhd3MgaXQgLS0gcmluZ3MsIHNoZWxscywgYmVsdHMgLS0gaW50byB0aGUgUGxv"
    "dGx5IGZpZ3VyZS4KCioqT25lIGZhY3Qgb3JnYW5pemVzIGFsbCBvZiBpdDogdGhlIGFzc2VtYmxl"
    "ciBjcmVhdGVzIG5vIGRhdGEuIEl0CmltcG9ydHMuKiogVGhlcmUgaXMgbm8gcG9pbnQgb24gdGhp"
    "cyBzaWRlIHdoZXJlIGEgd3JvbmcgbnVtYmVyIGNvdWxkIGJlCmNhdWdodCwgYmVjYXVzZSBub3Ro"
    "aW5nIGhlcmUga25vd3Mgd2hhdCBhIGNvcnJlY3QgcmluZyByYWRpdXMgaXMuClBvc2l0aW9ucyBs"
    "b29rIGFmdGVyIHRoZW1zZWx2ZXMsIHNpbmNlIHRoZSBidWlsZGVyIGFza3MgSG9yaXpvbnMgZGly"
    "ZWN0bHkKYW5kIGEgYmFkIHZhbHVlIGNhbm5vdCBzdXJ2aXZlIHVudGlsIG1vcm5pbmcuIEV2ZXJ5"
    "dGhpbmcgZWxzZSAtLSByaW5nCnJhZGlpLCBiZWx0IGRpc3RhbmNlcywgc2hlbGwgYm91bmRhcmll"
    "cyAtLSBzdGFydHMgYXMgYSBudW1iZXIgaW4gdGhlIG9ycmVyeQpyZXBvc2l0b3J5IGFuZCB0cmF2"
    "ZWxzIGhlcmUgYnkgYmVpbmcgY29waWVkLgoKKipgZGF0YS9vYmplY3RzX2NvbmZpZy5qc29uYCBp"
    "cyBtYWludGFpbmVkIGJ5IGhhbmQsIGFuZCB0aGF0IGlzIHRoZQpjdXJyZW50IGhvbmVzdCBzdGF0"
    "ZS4qKiBUaGUgY2FjaGUgYnVpbGRlciBoYXMgbmV2ZXIgcmVhZCB0aGUgb3JyZXJ5J3MKYGNvbnN0"
    "YW50c19uZXcucHlgLiBBIHZhbHVlIGNvcnJlY3RlZCBpbiB0aGUgb3JyZXJ5IGRvZXMgbm90IGFy"
    "cml2ZSBoZXJlCmJ5IGl0c2VsZjsgb24gb25lIG9jY2FzaW9uIHRoZSBzaXRlIHNlcnZlZCBhIHN1"
    "cGVyc2VkZWQgbnVtYmVyIGZvciBob3VycwphZnRlciB0aGUgY29ycmVjdGlvbiB3YXMgcHVzaGVk"
    "LiBUaGUgYXV0b21hdGVkIHRyYW5zcG9ydCBpcyBkZXNpZ25lZCBhbmQKdHJhY2tlZCBpbiB0aGUg"
    "b3JyZXJ5J3MgbGVkZ2VyLiBVbnRpbCBpdCBpcyBidWlsdCwgdGhpcyBjb3B5IGlzIGEgbWFudWFs"
    "CnN0ZXAgYW5kIGlzIHRyZWF0ZWQgYXMgb25lLgoKLS0tCgojIyBDaGVja2luZyBpdCBiZWZvcmUg"
    "YW5kIGFmdGVyIGEgcHVzaAoKKipgZ2FsbGVyeV9tYWludGVuYW5jZV9ydW4ucHlgKiogaXMgdGhp"
    "cyByZXBvc2l0b3J5J3Mgb3duIHN1aXRlLCBhbmQgaXQKZXhpc3RzIGJlY2F1c2UgdGhlIG9ycmVy"
    "eSdzIHJ1bm5lciBjYW5ub3Qgc2VlIHRoZSBwdWJsaWMgc3VyZmFjZS4gV2hlbiB0aGUKU3VuIGV4"
    "aGliaXQgZmlyc3Qgc2hpcHBlZCwgdGhyZWUgb2YgdGhlIGZvdXIgZGVmZWN0cyBpdCBleHBvc2Vk"
    "IHdlcmUgb24KdGhpcyBzaWRlIGFuZCBubyBjaGVjayBpbiB0aGUgb3RoZXIgcmVwb3NpdG9yeSBj"
    "b3VsZCByZWFjaCBhbnkgb2YgdGhlbSAtLQppbmNsdWRpbmcgb25lIHdoZXJlIEdpdEh1YiBQYWdl"
    "cyBzZXJ2ZWQgbm8gYC5weWAgZmlsZSBhdCBhbGwsIHdoaWNoIHdhcwppbnZpc2libGUgb24gdGhl"
    "IGRldmVsb3BlcidzIG1hY2hpbmUgYW5kIGludmlzaWJsZSBpbiB0aGUgcmVwb3NpdG9yeSwKYmVj"
    "YXVzZSBpdCBleGlzdGVkIG9ubHkgb24gdGhlIGRlcGxveWVkIHNpdGUuCgpgYGAKcHl0aG9uIGdh"
    "bGxlcnlfbWFpbnRlbmFuY2VfcnVuLnB5ICAgICAgICAgICBiZWZvcmUgeW91IGNvbW1pdApweXRo"
    "b24gZ2FsbGVyeV9tYWludGVuYW5jZV9ydW4ucHkgLS1saXZlICAgIGFmdGVyIHlvdSBwdXNoCmBg"
    "YAoKVGhlIGRlZmF1bHQgcGFzcyBpcyBvZmZsaW5lIGFuZCBkZXRlcm1pbmlzdGljLiBUaGUgYC0t"
    "bGl2ZWAgcGFzcyBhZGRzIHRoZQpjaGVja3MgdGhhdCBjYW4gb25seSBtZWFuIHNvbWV0aGluZyBv"
    "bmNlIEdpdEh1YiBQYWdlcyBoYXMgZGVwbG95ZWQsIGFuZApkb2VzIG5vdCByZS1ydW4gdGhlIG9m"
    "ZmxpbmUgb25lcy4KCkl0IHJlcG9ydHMgdGhyZWUgc3RhdGVzIHJhdGhlciB0aGFuIHR3bzogUEFT"
    "UywgRkFJTCwgYW5kICoqVU5SRUFDSEFCTEUqKi4gQQpjaGVjayB0aGF0IGNvdWxkIG5vdCBydW4g"
    "aXMgbmV2ZXIgZm9sZGVkIGludG8gIk4gb2YgTiBwYXNzZWQiLCBiZWNhdXNlIGEKY2hlY2sgdGhh"
    "dCBkaWQgbm90IHJ1biBsb29rcyBleGFjdGx5IGxpa2UgYSBjaGVjayB0aGF0IHBhc3NlZC4gTm9k"
    "ZQptaXNzaW5nIGlzIFVOUkVBQ0hBQkxFLiBObyBuZXR3b3JrIGlzIFVOUkVBQ0hBQkxFLiBBIHNp"
    "dGUgc2VydmluZwpkaWZmZXJlbnQgYnl0ZXMgdGhhbiB0aGUgd29ya2luZyBjb3B5IGlzIFVOUkVB"
    "Q0hBQkxFIC0tIG5vdCBhIHBhc3MgLS0KYmVjYXVzZSB0aGUgdGhpbmcgYmVpbmcgY2hlY2tlZCBp"
    "cyBub3QgdGhlIHRoaW5nIHRoYXQgYW5zd2VyZWQuCgoqKmAubm9qZWt5bGxgIGF0IHRoZSByZXBv"
    "c2l0b3J5IHJvb3QgaXMgbG9hZC1iZWFyaW5nLioqIEdpdEh1YiBQYWdlcyBydW5zCkpla3lsbCBi"
    "eSBkZWZhdWx0LCB3aGljaCBleGNsdWRlcyBkaXJlY3RvcmllcyBpdCB0cmVhdHMgYXMgcHJpdmF0"
    "ZSBhbmQKc2VydmVkIG5vbmUgb2YgdGhlIGFzc2VtYmxlcidzIFB5dGhvbi4gVGhlIGVtcHR5IGZp"
    "bGUgdHVybnMgSmVreWxsIG9mZi4gRG8Kbm90IGRlbGV0ZSBpdC4KCi0tLQoKIyMgTGF5b3V0Cgpg"
    "YGAKdG9ueXF1aW50YW5pbGxhLmdpdGh1Yi5pby8KfC0gaW5kZXguaHRtbCAgICAgICAgICAgICAg"
    "ICAgICAgIyB0aGUgY3VyYXRlZCBnYWxsZXJ5IHZpZXdlcgp8LSBpbnRlcmFjdGl2ZS5odG1sICAg"
    "ICAgICAgICAgICAjIHRoZSBpbnRlcmFjdGl2ZSBnYWxsZXJ5LCA/ZXhoaWJpdD08bmFtZT4KfC0g"
    "Lm5vamVreWxsICAgICAgICAgICAgICAgICAgICAgIyByZXF1aXJlZDsgc2VlIGFib3ZlCnwtIENO"
    "QU1FICAgICAgICAgICAgICAgICAgICAgICAgICMgdGhlIGN1c3RvbSBkb21haW4KfC0gZ2FsbGVy"
    "eV9tYWludGVuYW5jZV9ydW4ucHkgICAgIyB0aGlzIHJlcG8ncyBjaGVjayBzdWl0ZQp8LSBnYWxs"
    "ZXJ5Lwp8ICB8LSAqLmpzb24gICAgICAgICAgICAgICAgICAgICAjIHB1Ymxpc2hlZCB2aXN1YWxp"
    "emF0aW9uIGRhdGEKfCAgfC0gYXNzZW1ibGVyLyAgICAgICAgICAgICAgICAgIyB0aGUgc2hhcmVk"
    "IFB5dGhvbiwgcnVuIGluIFB5b2RpZGUKfCAgfC0gZmVhdHVyZV9yZW5kZXJlcnMuanMgICAgICAg"
    "IyBkcmF3cyB0aGUgYXNzZW1ibGVyJ3MgZmVhdHVyZSByZXBvcnQKfCAgfC0gYXNzZXRzLyAgICAg"
    "ICAgICAgICAgICAgICAgIyBLTVogbGF5ZXJzIGFuZCBvdGhlciBsYXJnZSBhc3NldHMKfC0gZGF0"
    "YS8KfCAgfC0gb2JqZWN0c19jb25maWcuanNvbiAgICAgICAgIyBmZWF0dXJlIHN0b3JlIChoYW5k"
    "LW1haW50YWluZWQpCnwgIHwtIHNvbGFyLXN5c3RlbS8gICAgICAgICAgICAgICMgdGhlIHNlcnZl"
    "ZCBjYWNoZQp8LSB0b29scy8KfCAgfC0gZ2FsbGVyeV9jYWNoZV9idWlsZGVyLnB5ICAgIyBidWls"
    "ZHMgdGhlIHNlcnZlZCBjYWNoZQp8ICB8LSBnYWxsZXJ5X3N0dWRpby5weSAgICAgICAgICAjIHBl"
    "ci1wbG90IGN1cmF0aW9uIGZvciB0aGUgc3RhdGljIGdhbGxlcnkKfCAgfC0ganNvbl9jb252ZXJ0"
    "ZXIucHkgICAgICAgICAgIyBleHBvcnRlZCBIVE1MIC0+IGdhbGxlcnkgSlNPTgp8ICB8LSBnYWxs"
    "ZXJ5X2VkaXRvci5weSAgICAgICAgICAjIHRpdGxlcywgY2F0ZWdvcmllcywgb3JkZXJpbmcKfC0g"
    "ZG9jdW1lbnRhdGlvbi8gICAgICAgICAgICAgICAgIyBkZXNpZ24gbm90ZXMsIGhhbmRvZmZzLCBz"
    "cGVudCBwYXRjaGVzCnwtIE1PRFVMRV9JTkRFWC5tZCAgICAgICAgICAgICAgICMgZ2VuZXJhdGVk"
    "CnwtIE1PRFVMRV9BVExBUy5tZCAgICAgICAgICAgICAgICMgZ2VuZXJhdGVkCmBgYAoKIyMjIFRo"
    "ZSBjdXJhdGVkIGdhbGxlcnkgcGlwZWxpbmUKCmBgYApkZXNrdG9wIGFwcCAtPiBIVE1MIGV4cG9y"
    "dAogICAgLT4gdG9vbHMvZ2FsbGVyeV9zdHVkaW8ucHkgICAgcGVyLXBsb3QgY3VyYXRpb24gKG9w"
    "dGlvbmFsKQogICAgLT4gdG9vbHMvanNvbl9jb252ZXJ0ZXIucHkgICAgSlNPTiArIGdhbGxlcnlf"
    "bWV0YWRhdGEuanNvbgogICAgLT4gdG9vbHMvZ2FsbGVyeV9lZGl0b3IucHkgICAgdGl0bGVzLCBj"
    "YXRlZ29yaWVzLCBvcmRlcmluZwogICAgLT4gaW5kZXguaHRtbCAgICAgICAgICAgICAgICAgcHVi"
    "bGlzaGVkIGJ5IEdpdEh1YiBQYWdlcwpgYGAKCmBnYWxsZXJ5X2NvbmZpZy5qc29uYCBpcyB0aGUg"
    "c2luZ2xlIHNvdXJjZSBvZiB0cnV0aCBmb3IgY2F0ZWdvcnkKZGVmaW5pdGlvbnMgYWNyb3NzIGFs"
    "bCBvZiB0aG9zZSB0b29scy4KCi0tLQoKIyMgVHdvIG9mIHRoZSBwcm9qZWN0J3MgZml2ZSBwb3Np"
    "dGlvbiBjb25zdW1lcnMgbGl2ZSBoZXJlCgpQb3NpdGlvbiBkYXRhIHJlYWNoZXMgYSB2aWV3ZXIg"
    "dGhyb3VnaCBmaXZlIHBhcmFsbGVsIHBhdGhzLCBhbmQgYSBjaGFuZ2UKYXMgc21hbGwgYXMgaG92"
    "ZXIgdGV4dCBjYW4gdG91Y2ggYWxsIG9mIHRoZW0uIFR3byBhcmUgaW4gdGhpcyByZXBvc2l0b3J5"
    "OgpgdG9vbHMvZ2FsbGVyeV9zdHVkaW8ucHlgIGFuZCBgdG9vbHMvanNvbl9jb252ZXJ0ZXIucHlg"
    "LiBUaGUgb3RoZXIgdGhyZWUKYXJlIGluIHRoZSBvcnJlcnkgcmVwb3NpdG9yeS4gRml4aW5nIG9u"
    "ZSBkb2VzIG5vdCBwcm9wYWdhdGUgdG8gdGhlIG90aGVycywKc28gYW55b25lIGNoYW5naW5nIHNv"
    "bWV0aGluZyBpbiB0aGUgZGF0YSBmbG93IG5lZWRzIHRvIGNoZWNrIGFsbCBmaXZlIC0tCmFuZCBn"
    "cmVwcGluZyBvbmx5IG9uZSByZXBvc2l0b3J5IGZpbmRzIHRocmVlLgoKLS0tCgojIyBDb250YWN0"
    "CgoqKkF1dGhvcjoqKiBUb255IFF1aW50YW5pbGxhCioqRW1haWw6KiogPHRvbnlxdWludGFuaWxs"
    "YUBnbWFpbC5jb20+CioqU2l0ZToqKiBbcGFsb21hc29ycmVyeS5jb21dKGh0dHBzOi8vcGFsb21h"
    "c29ycmVyeS5jb20vKQoqKkFwcGxpY2F0aW9uIHJlcG9zaXRvcnk6KiogW2dpdGh1Yi5jb20vdG9u"
    "eWxxdWludGFuaWxsYS9wYWxvbWFzX29ycmVyeV0oaHR0cHM6Ly9naXRodWIuY29tL3RvbnlscXVp"
    "bnRhbmlsbGEvcGFsb21hc19vcnJlcnkpCgpMaWNlbnNlZCBNSVQsIHRoZSBzYW1lIGFzIHRoZSBh"
    "cHBsaWNhdGlvbiByZXBvc2l0b3J5LgoKKipDdXJyZW5jeS4qKiBUaGlzIGZpbGUgY2FycmllcyBu"
    "byBjb3VudHMgb3Igc2l6ZXMgYnkgZGVzaWduLiBXaGF0IGNhbiBnbwpzdGFsZSBoZXJlIGlzIHRo"
    "ZSBkZXNjcmlwdGlvbiBvZiB0aGUgYXJjaGl0ZWN0dXJlLCBhbmQgd2hlbiB0aGF0IGNoYW5nZXMK"
    "dGhpcyBmaWxlIGlzIHBhcnQgb2YgdGhlIGNoYW5nZSAtLSBpbmNsdWRpbmcgaXRzIGhlYWRlciBi"
    "bG9jayBhdCB0aGUgdG9wLgo="
)

REQUIRED = [
    "## Two galleries, not one",
    "## How the interactive gallery works",
    "the assembler creates no data. It",
    "gallery_maintenance_run.py",
    "UNREACHABLE",
    ".nojekyll",
    "tonylquintanilla/palomas_orrery",
    "## What you can reach from where",
    "Anthropic's Claude Opus 5 | August 31, 2026",
    "Written under orrery ledger handle L-272",
]


def fail(msg):
    print("")
    print("FAILURE: " + msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    markers = ["interactive.html", "gallery_maintenance_run.py"]
    missing_markers = [m for m in markers if not os.path.exists(m)]
    if missing_markers:
        fail("run this from the GALLERY repo root -- the folder holding "
             + " and ".join(markers) + ".\n"
             "  Not found here: " + ", ".join(missing_markers) + "\n"
             "  Current folder: " + os.getcwd() + "\n"
             "  (This is the OTHER repository, not palomas_orrery.)")

    if os.path.exists(TARGET):
        fail(TARGET + " already exists in " + os.getcwd() + ". This patch "
             "creates a README and never overwrites one.")

    new_content = base64.b64decode(NEW_B64)
    if hashlib.md5(new_content).hexdigest() != NEW_MD5:
        fail("the embedded text does not match its own fingerprint; this "
             "script is damaged. Do not re-run it.")
    print("ok  embedded text fingerprint matches")

    nonascii = [b for b in new_content if b > 127]
    if nonascii:
        fail("text holds %d non-ASCII byte(s); the encoding gate is "
             "ASCII-only." % len(nonascii))
    print("ok  text is ASCII, LF")

    with open(TARGET, "wb") as fh:
        fh.write(new_content)
    print("ok  wrote " + TARGET + " (%d bytes)" % len(new_content))

    # ---- verification: read back from disk ----
    with open(TARGET, "rb") as fh:
        back = fh.read().replace(b"\r\n", b"\n")

    problems = []
    if hashlib.md5(back).hexdigest() != NEW_MD5:
        problems.append("README.md on disk does not match the intended text")

    text = back.decode("ascii", "replace")
    missing = [a for a in REQUIRED if a not in text]
    if missing:
        problems.append("missing from the written file: " + "; ".join(missing))

    if problems:
        print("")
        print("VERIFICATION FAILED after writing:")
        for p in problems:
            print("  - " + p)
        print("Undo is Discard Changes in GitHub Desktop.")
        sys.exit(1)

    print("ok  verified %d/%d required anchors present in the written file"
          % (len(REQUIRED), len(REQUIRED)))
    print("")
    print("patch applied.")
    print("")
    print("NEXT STEPS")
    print("  1. Read README.md.")
    print("  2. Run: python gallery_maintenance_run.py")
    print("  3. Commit README.md and this script (after moving it into")
    print("     documentation/) together.")
    print("")
    print("NOT DONE BY THIS PATCH:")
    print("  - The ledger lives in the ORRERY repo and is not touched.")
    print("    L-272 does not exist there yet.")


if __name__ == "__main__":
    main()
